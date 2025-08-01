from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean, Text, DECIMAL, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from app.core.database import Base

class FamiliarityLevelEnum(str, enum.Enum):
    learning = 'learning'
    familiar = 'familiar'
    mastered = 'mastered'

class StudyModeEnum(str, enum.Enum):
    flashcards = 'flashcards'
    learn = 'learn'
    write = 'write'
    spell = 'spell'
    test = 'test'
    match = 'match'
    gravity = 'gravity'

class StudyProgress(Base):
    __tablename__ = 'study_progress'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    study_set_id = Column(Integer, ForeignKey('study_sets.id'), nullable=False)
    term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    familiarity_level = Column(Enum(FamiliarityLevelEnum), nullable=True)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    last_studied = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

class StudySession(Base):
    __tablename__ = 'study_sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    study_set_id = Column(Integer, ForeignKey('study_sets.id'), nullable=False)
    study_mode = Column(Enum(StudyModeEnum), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    score = Column(DECIMAL(5,2), nullable=True)
    total_questions = Column(Integer, nullable=True)
    correct_answers = Column(Integer, nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)

class StarredCard(Base):
    __tablename__ = 'starred_cards'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    study_set_id = Column(Integer, ForeignKey('study_sets.id'), nullable=False)
    term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    starred_at = Column(DateTime, nullable=True)

class TestSession(Base):
    __tablename__ = 'test_sessions'
    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey('study_sessions.id'), nullable=False)
    max_questions = Column(Integer, nullable=False)
    answer_with = Column(String(20), nullable=False)
    question_types = Column(ARRAY(String), nullable=True)  # Array of question types
    time_limit = Column(Integer, nullable=True)  # seconds
    randomized_order = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)

class TestQuestion(Base):
    __tablename__ = 'test_questions'
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey('test_sessions.id'), nullable=False)
    term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    question_type = Column(String(20), nullable=False)  # multiple_choice, true_false, written, matching
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    options = Column(ARRAY(String), nullable=True)  # For multiple choice
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(DECIMAL(3,2), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)
    position = Column(Integer, nullable=False)

class MatchGame(Base):
    __tablename__ = 'match_games'
    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey('study_sessions.id'), nullable=False)
    pairs_count = Column(Integer, nullable=False)
    selected_terms = Column(ARRAY(String), nullable=True)  # Array of term IDs used in this game
    completed_at = Column(DateTime, nullable=True)
    completion_time_seconds = Column(Integer, nullable=True)
    incorrect_matches = Column(Integer, default=0)
    total_matches = Column(Integer, nullable=True)

class MatchMove(Base):
    __tablename__ = 'match_moves'
    id = Column(Integer, primary_key=True, index=True)
    match_game_id = Column(Integer, ForeignKey('match_games.id'), nullable=False)
    move_number = Column(Integer, nullable=False)
    first_card_term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    second_card_term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    is_match = Column(Boolean, nullable=False)
    time_spent_seconds = Column(Integer, nullable=True)
    move_timestamp = Column(DateTime, nullable=True)

class GravityGame(Base):
    __tablename__ = 'gravity_games'
    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey('study_sessions.id'), nullable=False)
    difficulty_level = Column(Integer, default=1)
    speed_multiplier = Column(DECIMAL(3,2), default=1.0)
    lives_remaining = Column(Integer, default=3)
    score = Column(Integer, default=0)
    terms_destroyed = Column(Integer, default=0)
    game_duration_seconds = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class GravityTerm(Base):
    __tablename__ = 'gravity_terms'
    id = Column(Integer, primary_key=True, index=True)
    gravity_game_id = Column(Integer, ForeignKey('gravity_games.id'), nullable=False)
    term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    appeared_at = Column(DateTime, nullable=True)
    was_destroyed = Column(Boolean, default=False)
    time_to_destroy_seconds = Column(Integer, nullable=True)
    user_answer = Column(Text, nullable=True)

class LearnSession(Base):
    __tablename__ = 'learn_sessions'
    id = Column(Integer, primary_key=True, index=True)
    study_session_id = Column(Integer, ForeignKey('study_sessions.id'), nullable=False)
    current_difficulty = Column(Integer, default=1)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    adaptive_algorithm_data = Column(JSON, nullable=True)  # Store algorithm state
    created_at = Column(DateTime, nullable=True)

class LearnQuestion(Base):
    __tablename__ = 'learn_questions'
    id = Column(Integer, primary_key=True, index=True)
    learn_session_id = Column(Integer, ForeignKey('learn_sessions.id'), nullable=False)
    term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    question_type = Column(String(20), nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    response_time_seconds = Column(DECIMAL(5,2), nullable=True)
    points_earned = Column(Integer, nullable=True)
    asked_at = Column(DateTime, nullable=True)