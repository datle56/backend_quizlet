from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import json
from app.models.study_progress import (
    StudyProgress, StudySession, FamiliarityLevelEnum, StudyModeEnum,
    StarredCard, TestSession, TestQuestion, MatchGame, MatchMove,
    GravityGame, GravityTerm, LearnSession, LearnQuestion
)
from app.models.study_set import Term, StudySet
from app.models.user import User
from app.schemas.study_progress import (
    TestConfig, LearnOptions, QuestionTypeEnum, AnswerWithEnum
)


class StudyService:
    @staticmethod
    def get_study_progress(db: Session, user_id: int, study_set_id: int):
        return db.query(StudyProgress).filter_by(user_id=user_id, study_set_id=study_set_id).all()

    @staticmethod
    def update_term_progress(db: Session, user_id: int, study_set_id: int, term_id: int, correct: bool, response_time: float = None, difficulty: int = None):
        progress = db.query(StudyProgress).filter_by(
            user_id=user_id, study_set_id=study_set_id, term_id=term_id).first()
        now = datetime.utcnow()
        if not progress:
            progress = StudyProgress(user_id=user_id, study_set_id=study_set_id, term_id=term_id,
                                     last_studied=now, correct_count=0, incorrect_count=0, current_streak=0, longest_streak=0)
            db.add(progress)
        progress.last_studied = now
        if correct:
            progress.correct_count += 1
            progress.current_streak += 1
            progress.longest_streak = max(
                progress.longest_streak, progress.current_streak)
            # SRS: next_review = now + longer interval (minutes for testing)
            progress.familiarity_level = StudyService._next_familiarity(
                progress.familiarity_level, up=True)
            progress.next_review = now + \
                timedelta(minutes=StudyService._srs_interval(
                    progress.familiarity_level))
        else:
            progress.incorrect_count += 1
            progress.current_streak = 0
            progress.familiarity_level = StudyService._next_familiarity(
                progress.familiarity_level, up=False)
            progress.next_review = now + timedelta(minutes=1)
        db.commit()
        return progress

    @staticmethod
    def get_review_terms(db: Session, user_id: int, study_set_id: int):
        # Return terms that are due for review (SRS)
        now = datetime.utcnow()
        progresses = db.query(StudyProgress).filter_by(
            user_id=user_id, study_set_id=study_set_id).all()
        due_terms = [
            p for p in progresses if not p.next_review or p.next_review <= now]
        return due_terms

    @staticmethod
    def start_study_session(db: Session, user_id: int, study_set_id: int, study_mode: StudyModeEnum):
        now = datetime.utcnow()
        session = StudySession(
            user_id=user_id, study_set_id=study_set_id, study_mode=study_mode, started_at=now)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def update_study_session(db: Session, session_id: int, **kwargs):
        session = db.query(StudySession).filter_by(id=session_id).first()
        if not session:
            return None
        for key, value in kwargs.items():
            setattr(session, key, value)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def force_next_review(db: Session, user_id: int, study_set_id: int, term_id: int):
        """Force next_review về quá khứ để test SRS ngay lập tức"""
        progress = db.query(StudyProgress).filter_by(
            user_id=user_id, study_set_id=study_set_id, term_id=term_id).first()
        if not progress:
            return None
        # Set next_review về 1 giờ trước
        progress.next_review = datetime.utcnow() - timedelta(hours=1)
        db.commit()
        db.refresh(progress)
        return progress

    # Flashcards Mode Methods
    @staticmethod
    def get_flashcards(db: Session, user_id: int, study_set_id: int) -> List[Dict[str, Any]]:
        """Get flashcards for a study set with progress and starred status"""
        terms = db.query(Term).filter_by(study_set_id=study_set_id).order_by(Term.position).all()
        starred_terms = db.query(StarredCard).filter_by(
            user_id=user_id, study_set_id=study_set_id).all()
        starred_term_ids = {st.term_id for st in starred_terms}
        
        progresses = db.query(StudyProgress).filter_by(
            user_id=user_id, study_set_id=study_set_id).all()
        progress_dict = {p.term_id: p for p in progresses}
        
        flashcards = []
        for i, term in enumerate(terms):
            progress = progress_dict.get(term.id)
            flashcards.append({
                'term_id': term.id,
                'term': term.term,
                'definition': term.definition,
                'image_url': term.image_url,
                'audio_url': term.audio_url,
                'is_starred': term.id in starred_term_ids,
                'familiarity_level': progress.familiarity_level if progress else None,
                'position': i + 1
            })
        return flashcards

    @staticmethod
    def toggle_star_card(db: Session, user_id: int, study_set_id: int, term_id: int, starred: bool):
        """Star or unstar a flashcard"""
        if starred:
            # Check if already starred
            existing = db.query(StarredCard).filter_by(
                user_id=user_id, study_set_id=study_set_id, term_id=term_id).first()
            if not existing:
                starred_card = StarredCard(
                    user_id=user_id, study_set_id=study_set_id, term_id=term_id, starred_at=datetime.utcnow())
                db.add(starred_card)
                db.commit()
        else:
            # Remove star
            db.query(StarredCard).filter_by(
                user_id=user_id, study_set_id=study_set_id, term_id=term_id).delete()
            db.commit()
        return {'starred': starred}

    @staticmethod
    def get_starred_cards(db: Session, user_id: int, study_set_id: int) -> List[Dict[str, Any]]:
        """Get all starred cards for a study set"""
        starred_cards = db.query(StarredCard).filter_by(
            user_id=user_id, study_set_id=study_set_id).all()
        
        cards = []
        for sc in starred_cards:
            term = db.query(Term).filter_by(id=sc.term_id).first()
            if term:
                cards.append({
                    'term_id': term.id,
                    'term': term.term,
                    'definition': term.definition,
                    'image_url': term.image_url,
                    'audio_url': term.audio_url,
                    'is_starred': True,
                    'starred_at': sc.starred_at
                })
        return cards

    # Test Mode Methods
    @staticmethod
    def create_test_session(db: Session, user_id: int, study_set_id: int, config: TestConfig):
        """Create a new test session"""
        # Check if study set exists and has terms
        terms = db.query(Term).filter_by(study_set_id=study_set_id).all()
        if not terms:
            raise ValueError(f"No terms found in study set {study_set_id}")
        
        # Create study session
        session = StudyService.start_study_session(db, user_id, study_set_id, StudyModeEnum.test)
        
        # Create test session
        test_session = TestSession(
            study_session_id=session.id,
            max_questions=min(config.max_questions, len(terms)),  # Don't exceed available terms
            answer_with=config.answer_with,
            question_types=config.question_types,  # Use array directly
            time_limit=config.time_limit,
            randomized_order=config.randomize_order,
            created_at=datetime.utcnow()
        )
        db.add(test_session)
        db.commit()
        db.refresh(test_session)
        
        # Generate questions
        questions = StudyService._generate_test_questions(db, test_session, config)
        
        return {
            'test_id': test_session.id,
            'study_set_id': study_set_id,
            'config': config.dict(),
            'total_questions': len(questions),
            'time_limit': config.time_limit,
            'created_at': test_session.created_at,
            'questions': questions
        }

    @staticmethod
    def get_test_session(db: Session, test_id: int):
        """Get test session with questions"""
        test_session = db.query(TestSession).filter_by(id=test_id).first()
        if not test_session:
            return None
        
        # Get study session to access study_set_id
        study_session = db.query(StudySession).filter_by(id=test_session.study_session_id).first()
        if not study_session:
            return None
        
        questions = db.query(TestQuestion).filter_by(test_session_id=test_id).order_by(TestQuestion.position).all()
        
        return {
            'test_id': test_session.id,
            'study_set_id': study_session.study_set_id,
            'config': {
                'max_questions': test_session.max_questions,
                'answer_with': test_session.answer_with,
                'question_types': test_session.question_types if test_session.question_types else [],
                'time_limit': test_session.time_limit,
                'randomized_order': test_session.randomized_order
            },
            'total_questions': len(questions),
            'time_limit': test_session.time_limit,
            'created_at': test_session.created_at,
            'questions': [
                {
                    'question_id': f"test_{q.id}",
                    'term_id': q.term_id,
                    'question_type': q.question_type,
                    'question_text': q.question_text,
                    'correct_answer': q.correct_answer,
                    'options': q.options,
                    'points_worth': float(q.points_earned) if q.points_earned else 1.0,
                    'position': q.position
                } for q in questions
            ]
        }

    @staticmethod
    def submit_test(db: Session, test_id: int, answers: List[Dict[str, Any]], total_time_spent: float):
        """Submit test answers and calculate results"""
        test_session = db.query(TestSession).filter_by(id=test_id).first()
        if not test_session:
            return None
        
        questions = db.query(TestQuestion).filter_by(test_session_id=test_id).all()
        question_dict = {q.id: q for q in questions}
        
        correct_answers = 0
        total_score = 0
        breakdown_by_type = {}
        incorrect_answers = []
        suggested_review = []
        
        for answer in answers:
            question_id = int(answer['question_id'].split('_')[1])
            question = question_dict.get(question_id)
            if not question:
                continue
            
            user_answer = answer['answer']
            time_spent = answer.get('time_spent', 0)
            
            # Check answer
            is_correct = StudyService._check_answer_by_type(question, user_answer)
            
            # Update question
            question.user_answer = user_answer
            question.is_correct = is_correct
            question.time_spent_seconds = int(time_spent)
            question.points_earned = question.points_earned if is_correct else 0
            
            if is_correct:
                correct_answers += 1
                total_score += float(question.points_earned)
            else:
                incorrect_answers.append({
                    'term_id': question.term_id,
                    'question_text': question.question_text,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_answer,
                    'question_type': question.question_type
                })
                suggested_review.append(question.term_id)
            
            # Update breakdown
            q_type = question.question_type
            if q_type not in breakdown_by_type:
                breakdown_by_type[q_type] = {'correct': 0, 'total': 0, 'score': 0}
            breakdown_by_type[q_type]['total'] += 1
            if is_correct:
                breakdown_by_type[q_type]['correct'] += 1
                breakdown_by_type[q_type]['score'] += float(question.points_earned)
        
        # Update study session
        study_session = db.query(StudySession).filter_by(id=test_session.study_session_id).first()
        if study_session:
            study_session.completed_at = datetime.utcnow()
            study_session.score = total_score
            study_session.total_questions = len(questions)
            study_session.correct_answers = correct_answers
            study_session.time_spent_seconds = int(total_time_spent)
        
        db.commit()
        
        return {
            'test_id': test_id,
            'score': total_score,
            'total_questions': len(questions),
            'correct_answers': correct_answers,
            'total_time_spent': total_time_spent,
            'breakdown_by_type': breakdown_by_type,
            'incorrect_answers': incorrect_answers,
            'suggested_review': list(set(suggested_review))
        }

    # Match Mode Methods
    @staticmethod
    def create_match_game(db: Session, user_id: int, study_set_id: int, pairs_count: int = 6):
        """Create a new match game"""
        # Check if study set exists and has terms
        terms = db.query(Term).filter_by(study_set_id=study_set_id).all()
        if not terms:
            raise ValueError(f"No terms found in study set {study_set_id}")
        
        # Create study session
        session = StudyService.start_study_session(db, user_id, study_set_id, StudyModeEnum.match)
        
        # Adjust pairs_count if not enough terms
        if len(terms) < pairs_count:
            pairs_count = len(terms)
        
        selected_terms = random.sample(terms, pairs_count)
        selected_term_ids = [str(t.id) for t in selected_terms]  # Convert to string array
        
        # Create match game
        match_game = MatchGame(
            study_session_id=session.id,
            pairs_count=pairs_count,
            selected_terms=selected_term_ids
        )
        db.add(match_game)
        db.commit()
        db.refresh(match_game)
        
        # Generate cards
        cards = []
        for i, term in enumerate(selected_terms):
            # Term card
            cards.append({
                'card_id': f"term_{term.id}",
                'term_id': term.id,
                'content': term.term,
                'is_term': True,
                'position': i * 2
            })
            # Definition card
            cards.append({
                'card_id': f"def_{term.id}",
                'term_id': term.id,
                'content': term.definition,
                'is_term': False,
                'position': i * 2 + 1
            })
        
        # Shuffle cards
        random.shuffle(cards)
        for i, card in enumerate(cards):
            card['position'] = i
        
        return {
            'game_id': match_game.id,
            'study_set_id': study_set_id,
            'pairs_count': pairs_count,
            'selected_terms': selected_term_ids,
            'cards': cards
        }

    @staticmethod
    def submit_match_move(db: Session, game_id: int, first_card_id: str, second_card_id: str, time_spent: float):
        """Submit a move in match game"""
        match_game = db.query(MatchGame).filter_by(id=game_id).first()
        if not match_game:
            return None
        
        # Parse card IDs
        first_term_id = int(first_card_id.split('_')[1])
        second_term_id = int(second_card_id.split('_')[1])
        
        # Check if it's a match
        is_match = first_term_id == second_term_id
        
        # Record move
        move = MatchMove(
            match_game_id=game_id,
            move_number=1,  # Simplified
            first_card_term_id=first_term_id,
            second_card_term_id=second_term_id,
            is_match=is_match,
            time_spent_seconds=int(time_spent),
            move_timestamp=datetime.utcnow()
        )
        db.add(move)
        
        if not is_match:
            match_game.incorrect_matches += 1
        
        db.commit()
        
        return {
            'is_match': is_match,
            'move_number': move.move_number,
            'incorrect_matches': match_game.incorrect_matches
        }

    @staticmethod
    def complete_match_game(db: Session, game_id: int, completion_time: float):
        """Complete match game and calculate results"""
        match_game = db.query(MatchGame).filter_by(id=game_id).first()
        if not match_game:
            return None
        
        match_game.completed_at = datetime.utcnow()
        match_game.completion_time_seconds = int(completion_time)
        match_game.total_matches = match_game.pairs_count
        
        # Calculate score (bonus for speed, penalty for incorrect matches)
        base_score = 100 * match_game.pairs_count
        time_bonus = max(0, 50 - int(completion_time / 10))  # Bonus for speed
        penalty = match_game.incorrect_matches * 10  # Penalty for wrong matches
        final_score = base_score + time_bonus - penalty
        
        # Update study session
        study_session = db.query(StudySession).filter_by(id=match_game.study_session_id).first()
        if study_session:
            study_session.completed_at = datetime.utcnow()
            study_session.score = final_score
            study_session.time_spent_seconds = int(completion_time)
        
        db.commit()
        
        return {
            'game_id': game_id,
            'completion_time': completion_time,
            'total_matches': match_game.pairs_count,
            'incorrect_matches': match_game.incorrect_matches,
            'score': final_score
        }

    # Gravity Mode Methods
    @staticmethod
    def create_gravity_game(db: Session, user_id: int, study_set_id: int, difficulty_level: int = 1):
        """Create a new gravity game"""
        # Create study session
        session = StudyService.start_study_session(db, user_id, study_set_id, StudyModeEnum.gravity)
        
        # Create gravity game
        gravity_game = GravityGame(
            study_session_id=session.id,
            difficulty_level=difficulty_level,
            speed_multiplier=1.0 + (difficulty_level - 1) * 0.2,
            lives_remaining=3
        )
        db.add(gravity_game)
        db.commit()
        db.refresh(gravity_game)
        
        return {
            'game_id': gravity_game.id,
            'study_set_id': study_set_id,
            'difficulty_level': difficulty_level,
            'lives_remaining': gravity_game.lives_remaining,
            'speed_multiplier': float(gravity_game.speed_multiplier)
        }

    @staticmethod
    def submit_gravity_answer(db: Session, game_id: int, term_id: int, answer: str, time_to_answer: float):
        """Submit answer for gravity game"""
        gravity_game = db.query(GravityGame).filter_by(id=game_id).first()
        if not gravity_game:
            return None
        
        term = db.query(Term).filter_by(id=term_id).first()
        if not term:
            return None
        
        # Check answer
        is_correct = StudyService._check_answer(term, answer, 'written')
        
        # Record gravity term
        gravity_term = GravityTerm(
            gravity_game_id=game_id,
            term_id=term_id,
            appeared_at=datetime.utcnow(),
            was_destroyed=is_correct,
            time_to_destroy_seconds=int(time_to_answer) if is_correct else None,
            user_answer=answer
        )
        db.add(gravity_term)
        
        if is_correct:
            gravity_game.terms_destroyed += 1
            gravity_game.score += 10 + max(0, 20 - int(time_to_answer))  # Bonus for speed
        else:
            gravity_game.lives_remaining -= 1
        
        db.commit()
        
        return {
            'is_correct': is_correct,
            'lives_remaining': gravity_game.lives_remaining,
            'score': gravity_game.score,
            'terms_destroyed': gravity_game.terms_destroyed
        }

    @staticmethod
    def complete_gravity_game(db: Session, game_id: int, final_score: int, game_duration: float):
        """Complete gravity game"""
        gravity_game = db.query(GravityGame).filter_by(id=game_id).first()
        if not gravity_game:
            return None
        
        gravity_game.completed_at = datetime.utcnow()
        gravity_game.score = final_score
        gravity_game.game_duration_seconds = int(game_duration)
        
        # Update study session
        study_session = db.query(StudySession).filter_by(id=gravity_game.study_session_id).first()
        if study_session:
            study_session.completed_at = datetime.utcnow()
            study_session.score = final_score
            study_session.time_spent_seconds = int(game_duration)
        
        db.commit()
        
        return {
            'final_score': final_score,
            'terms_destroyed': gravity_game.terms_destroyed,
            'game_duration': game_duration,
            'lives_remaining': gravity_game.lives_remaining
        }

    # Write Mode Methods
    @staticmethod
    def get_write_questions(db: Session, user_id: int, study_set_id: int, answer_with: AnswerWithEnum = AnswerWithEnum.both):
        """Get write mode questions"""
        terms = db.query(Term).filter_by(study_set_id=study_set_id).all()
        questions = []
        
        for term in terms:
            if answer_with == AnswerWithEnum.term or answer_with == AnswerWithEnum.both:
                questions.append({
                    'question_id': f"write_term_{term.id}",
                    'term_id': term.id,
                    'prompt': f"What is the definition of '{term.term}'?",
                    'correct_answer': term.definition,
                    'synonyms': [],
                    'points_worth': 1
                })
            
            if answer_with == AnswerWithEnum.definition or answer_with == AnswerWithEnum.both:
                questions.append({
                    'question_id': f"write_def_{term.id}",
                    'term_id': term.id,
                    'prompt': f"What term means '{term.definition}'?",
                    'correct_answer': term.term,
                    'synonyms': [],
                    'points_worth': 1
                })
        
        return questions

    @staticmethod
    def check_write_answer(db: Session, question_id: str, answer: str, response_time: float):
        """Check written answer with fuzzy matching"""
        parts = question_id.split('_')
        term_id = int(parts[2])
        question_type = parts[1]
        
        term = db.query(Term).filter_by(id=term_id).first()
        if not term:
            return None
        
        correct_answer = term.definition if question_type == 'term' else term.term
        
        # Simple fuzzy matching (can be improved with more sophisticated algorithms)
        is_correct = StudyService._fuzzy_match(answer, correct_answer)
        partial_credit = StudyService._calculate_partial_credit(answer, correct_answer)
        
        score = 1.0 if is_correct else partial_credit
        
        return {
            'is_correct': is_correct,
            'score': score,
            'feedback': StudyService._generate_feedback(answer, correct_answer, is_correct),
            'suggested_answer': correct_answer if not is_correct else None,
            'partial_credit': partial_credit > 0
        }

    # Helper Methods
    @staticmethod
    def _next_familiarity(current, up=True):
        # Simple logic: learning -> familiar -> mastered, or reverse
        if up:
            if current == FamiliarityLevelEnum.learning:
                return FamiliarityLevelEnum.familiar
            elif current == FamiliarityLevelEnum.familiar:
                return FamiliarityLevelEnum.mastered
            else:
                return FamiliarityLevelEnum.mastered
        else:
            if current == FamiliarityLevelEnum.mastered:
                return FamiliarityLevelEnum.familiar
            elif current == FamiliarityLevelEnum.familiar:
                return FamiliarityLevelEnum.learning
            else:
                return FamiliarityLevelEnum.learning

    @staticmethod
    def _srs_interval(familiarity):
        # Đổi sang phút để test nhanh: learning=1p, familiar=3p, mastered=7p
        if familiarity == FamiliarityLevelEnum.mastered:
            return 7
        elif familiarity == FamiliarityLevelEnum.familiar:
            return 3
        else:
            return 1

    @staticmethod
    def _generate_test_questions(db: Session, test_session: TestSession, config: TestConfig):
        """Generate questions for test mode"""
        # Get study session to access study_set_id
        study_session = db.query(StudySession).filter_by(id=test_session.study_session_id).first()
        if not study_session:
            return []
        
        terms = db.query(Term).filter_by(study_set_id=study_session.study_set_id).all()
        
        if config.max_questions < len(terms):
            terms = random.sample(terms, config.max_questions)
        
        questions = []
        for i, term in enumerate(terms):
            question_type = random.choice(config.question_types) if config.question_types else "written"
            question_data = StudyService._generate_question(term, question_type, config.answer_with)
            
            test_question = TestQuestion(
                test_session_id=test_session.id,
                term_id=term.id,
                question_type=question_type,
                question_text=question_data['question_text'],
                correct_answer=question_data['correct_answer'],
                options=question_data.get('options'),
                points_earned=1.0,
                position=i + 1
            )
            db.add(test_question)
            questions.append(test_question)
        
        db.commit()
        return questions

    @staticmethod
    def _generate_question(term: Term, question_type: str, answer_with: str):
        """Generate question based on type and answer_with preference"""
        if question_type == 'multiple_choice':
            # This would need to be enhanced with actual options from other terms
            return {
                'question_text': f"What is the definition of '{term.term}'?",
                'correct_answer': term.definition,
                'options': [term.definition, "Option 2", "Option 3", "Option 4"]  # Simplified
            }
        elif question_type == 'written':
            if answer_with == 'term':
                return {
                    'question_text': f"What is the definition of '{term.term}'?",
                    'correct_answer': term.definition
                }
            else:
                return {
                    'question_text': f"What term means '{term.definition}'?",
                    'correct_answer': term.term
                }
        else:
            return {
                'question_text': f"What is the definition of '{term.term}'?",
                'correct_answer': term.definition
            }

    @staticmethod
    def _check_answer(term: Term, answer: str, question_type: str):
        """Check if answer is correct"""
        if question_type == 'written':
            return StudyService._fuzzy_match(answer, term.definition) or StudyService._fuzzy_match(answer, term.term)
        else:
            return answer.lower().strip() == term.definition.lower().strip() or answer.lower().strip() == term.term.lower().strip()

    @staticmethod
    def _check_answer_by_type(question: TestQuestion, answer: str):
        """Check answer based on question type"""
        if question.question_type == 'multiple_choice':
            return answer.lower().strip() == question.correct_answer.lower().strip()
        elif question.question_type == 'true_false':
            return answer.lower().strip() == question.correct_answer.lower().strip()
        elif question.question_type == 'written':
            return StudyService._fuzzy_match(answer, question.correct_answer)
        else:
            return answer.lower().strip() == question.correct_answer.lower().strip()

    @staticmethod
    def _fuzzy_match(answer: str, correct: str, threshold: float = 0.8):
        """Simple fuzzy matching (can be enhanced with more sophisticated algorithms)"""
        answer_clean = answer.lower().strip()
        correct_clean = correct.lower().strip()
        
        # Exact match
        if answer_clean == correct_clean:
            return True
        
        # Contains match
        if answer_clean in correct_clean or correct_clean in answer_clean:
            return True
        
        # Simple similarity (can be enhanced with Levenshtein distance, etc.)
        return False

    @staticmethod
    def _calculate_partial_credit(answer: str, correct: str):
        """Calculate partial credit for close answers"""
        # Simplified partial credit calculation
        answer_clean = answer.lower().strip()
        correct_clean = correct.lower().strip()
        
        if len(answer_clean) > len(correct_clean) * 0.7:
            return 0.5
        return 0.0

    @staticmethod
    def _generate_feedback(answer: str, correct: str, is_correct: bool):
        """Generate feedback for written answers"""
        if is_correct:
            return "Correct! Well done!"
        else:
            return f"Not quite right. The correct answer is: {correct}"
