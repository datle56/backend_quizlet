from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean, Text, DECIMAL
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