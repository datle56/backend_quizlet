from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.study_progress import (
    StudyProgressResponse, TermProgressUpdate, ReviewTermList, StudySessionCreate, StudySessionResponse, StudySessionUpdate,
    # Flashcards
    FlashcardResponse, StarCardRequest, StarredCardsResponse,
    # Learn Mode
    LearnOptions, LearnQuestion, LearnAnswer, LearnProgress,
    # Test Mode
    TestConfig, TestSession, TestQuestion, TestSubmission, TestResult,
    # Match Mode
    MatchGame, MatchCard, MatchMove, MatchCompletion, MatchResult,
    # Gravity Mode
    GravityGame, GravityTerm, GravityAnswer, GravityCompletion, GravityLeaderboardEntry,
    # Write Mode
    WriteQuestion, WriteAnswer, WriteValidation,
    # Common
    StudyModeResponse, ErrorResponse,
    # Enums
    StudyModeEnum, AnswerWithEnum, QuestionTypeEnum
)
from app.services.study_service import StudyService

router = APIRouter()

# Base Study Progress Endpoints
@router.get('/progress/{study_set_id}', response_model=List[StudyProgressResponse])
def get_study_progress(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progresses = StudyService.get_study_progress(db, current_user.id, study_set_id)
    return progresses

@router.post('/progress/{study_set_id}/terms/{term_id}', response_model=StudyProgressResponse)
def update_term_progress(study_set_id: int, term_id: int, update: TermProgressUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progress = StudyService.update_term_progress(db, current_user.id, study_set_id, term_id, update.correct, update.response_time, update.difficulty)
    return progress

@router.get('/review/{study_set_id}', response_model=ReviewTermList)
def get_review_terms(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    due_terms = StudyService.get_review_terms(db, current_user.id, study_set_id)
    # Map to ReviewTermList schema
    terms = []
    for p in due_terms:
        terms.append({
            'term_id': p.term_id,
            'term': '',  # You may want to join with Term model for term/definition
            'definition': '',
            'familiarity_level': p.familiarity_level,
            'next_review': p.next_review
        })
    return {'study_set_id': study_set_id, 'terms': terms}

@router.post('/session', response_model=StudySessionResponse)
def start_study_session(session: StudySessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = StudyService.start_study_session(db, current_user.id, session.study_set_id, session.study_mode)
    return s

@router.put('/session/{id}', response_model=StudySessionResponse)
def update_study_session(id: int, update: StudySessionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = StudyService.update_study_session(db, id, **update.dict(exclude_unset=True))
    if not s:
        raise HTTPException(status_code=404, detail='Session not found')
    return s

# Flashcards Mode Endpoints
@router.get('/modes/flashcards/{study_set_id}', response_model=List[FlashcardResponse])
def get_flashcards(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get flashcards for a study set with progress and starred status"""
    flashcards = StudyService.get_flashcards(db, current_user.id, study_set_id)
    return flashcards

@router.post('/modes/flashcards/{study_set_id}/star/{term_id}')
def star_card(study_set_id: int, term_id: int, star_request: StarCardRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Star or unstar a flashcard"""
    result = StudyService.toggle_star_card(db, current_user.id, study_set_id, term_id, star_request.starred)
    return result

@router.get('/modes/flashcards/{study_set_id}/starred', response_model=StarredCardsResponse)
def get_starred_cards(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all starred cards for a study set"""
    cards = StudyService.get_starred_cards(db, current_user.id, study_set_id)
    return {'study_set_id': study_set_id, 'cards': cards}

# Learn Mode Endpoints
@router.get('/modes/learn/{study_set_id}', response_model=LearnQuestion)
def get_learn_question(study_set_id: int, learn_session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get next adaptive question for learn mode"""
    question = StudyService.get_learn_question(db, learn_session_id)
    if not question:
        raise HTTPException(status_code=404, detail='No more questions available')
    return question

@router.post('/modes/learn/{study_set_id}/answer')
def submit_learn_answer(study_set_id: int, learn_session_id: int, answer: LearnAnswer, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Submit answer for learn mode"""
    result = StudyService.submit_learn_answer(db, learn_session_id, answer.question_id, answer.answer, answer.response_time)
    if not result:
        raise HTTPException(status_code=404, detail='Learn session not found')
    return result

@router.get('/modes/learn/{study_set_id}/options', response_model=LearnOptions)
def get_learn_options(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get learn mode customization options"""
    return LearnOptions()

# Test Mode Endpoints
@router.post('/modes/test/{study_set_id}', response_model=TestSession)
def create_test(study_set_id: int, config: TestConfig, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new test session"""
    test_session = StudyService.create_test_session(db, current_user.id, study_set_id, config)
    return test_session

@router.get('/modes/test/{test_id}', response_model=TestSession)
def get_test(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get test session with questions"""
    test_session = StudyService.get_test_session(db, test_id)
    if not test_session:
        raise HTTPException(status_code=404, detail='Test session not found')
    return test_session

@router.post('/modes/test/{test_id}/submit', response_model=TestResult)
def submit_test(test_id: int, submission: TestSubmission, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Submit test answers and get results"""
    result = StudyService.submit_test(db, test_id, submission.answers, submission.total_time_spent)
    if not result:
        raise HTTPException(status_code=404, detail='Test session not found')
    return result

@router.get('/modes/test/{test_id}/results', response_model=TestResult)
def get_test_results(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get test results"""
    # This would need to be implemented to retrieve stored results
    raise HTTPException(status_code=501, detail='Not implemented yet')

# Match Mode Endpoints
@router.post('/modes/match/{study_set_id}', response_model=MatchGame)
def create_match_game(study_set_id: int, pairs_count: int = Query(6, ge=4, le=12), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new match game"""
    match_game = StudyService.create_match_game(db, current_user.id, study_set_id, pairs_count)
    return match_game

@router.get('/modes/match/{game_id}', response_model=MatchGame)
def get_match_game(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get match game data"""
    # This would need to be implemented
    raise HTTPException(status_code=501, detail='Not implemented yet')

@router.post('/modes/match/{game_id}/move')
def submit_match_move(game_id: int, move: MatchMove, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Submit a move in match game"""
    result = StudyService.submit_match_move(db, game_id, move.first_card_id, move.second_card_id, 0.0)  # time_spent would need to be calculated
    if not result:
        raise HTTPException(status_code=404, detail='Match game not found')
    return result

@router.post('/modes/match/{game_id}/complete', response_model=MatchResult)
def complete_match_game(game_id: int, completion: MatchCompletion, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Complete match game and get results"""
    result = StudyService.complete_match_game(db, game_id, completion.completion_time)
    if not result:
        raise HTTPException(status_code=404, detail='Match game not found')
    return result

# Gravity Mode Endpoints
@router.post('/modes/gravity/{study_set_id}', response_model=GravityGame)
def create_gravity_game(study_set_id: int, difficulty_level: int = Query(1, ge=1, le=5), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new gravity game"""
    gravity_game = StudyService.create_gravity_game(db, current_user.id, study_set_id, difficulty_level)
    return gravity_game

@router.post('/modes/gravity/{game_id}/answer')
def submit_gravity_answer(game_id: int, answer: GravityAnswer, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Submit answer for gravity game"""
    result = StudyService.submit_gravity_answer(db, game_id, answer.term_id, answer.answer, answer.time_to_answer)
    if not result:
        raise HTTPException(status_code=404, detail='Gravity game not found')
    return result

@router.post('/modes/gravity/{game_id}/complete', response_model=GravityCompletion)
def complete_gravity_game(game_id: int, completion: GravityCompletion, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Complete gravity game"""
    result = StudyService.complete_gravity_game(db, game_id, completion.final_score, completion.game_duration)
    if not result:
        raise HTTPException(status_code=404, detail='Gravity game not found')
    return result

@router.get('/modes/gravity/{game_id}/leaderboard', response_model=List[GravityLeaderboardEntry])
def get_gravity_leaderboard(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get gravity game leaderboard"""
    # This would need to be implemented
    raise HTTPException(status_code=501, detail='Not implemented yet')

# Write Mode Endpoints
@router.get('/modes/write/{study_set_id}', response_model=List[WriteQuestion])
def get_write_questions(study_set_id: int, answer_with: AnswerWithEnum = AnswerWithEnum.both, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get write mode questions"""
    questions = StudyService.get_write_questions(db, current_user.id, study_set_id, answer_with)
    return questions

@router.post('/modes/write/{study_set_id}/check', response_model=WriteValidation)
def check_write_answer(study_set_id: int, answer: WriteAnswer, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Check written answer"""
    result = StudyService.check_write_answer(db, answer.question_id, answer.answer, answer.response_time)
    if not result:
        raise HTTPException(status_code=404, detail='Question not found')
    return result

# Test endpoint để force next_review về quá khứ
@router.post('/test/force-review/{study_set_id}/terms/{term_id}')
def force_next_review(study_set_id: int, term_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Force next_review về quá khứ để test SRS ngay lập tức"""
    progress = StudyService.force_next_review(db, current_user.id, study_set_id, term_id)
    if not progress:
        raise HTTPException(status_code=404, detail='Progress not found')
    return {"message": f"Next review for term {term_id} forced to past time", "progress": progress}