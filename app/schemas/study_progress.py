from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FamiliarityLevelEnum(str, Enum):
    learning = 'learning'
    familiar = 'familiar'
    mastered = 'mastered'

class StudyModeEnum(str, Enum):
    flashcards = 'flashcards'
    learn = 'learn'
    write = 'write'
    spell = 'spell'
    test = 'test'
    match = 'match'

class StudyProgressBase(BaseModel):
    familiarity_level: Optional[FamiliarityLevelEnum]
    correct_count: int = 0
    incorrect_count: int = 0
    last_studied: Optional[datetime]
    next_review: Optional[datetime]
    current_streak: int = 0
    longest_streak: int = 0

class StudyProgressCreate(StudyProgressBase):
    pass

class StudyProgressResponse(StudyProgressBase):
    id: int
    user_id: int
    study_set_id: int
    term_id: int

    class Config:
        orm_mode = True

class TermProgressUpdate(BaseModel):
    correct: bool
    response_time: Optional[float]
    difficulty: Optional[int]

class ReviewTerm(BaseModel):
    term_id: int
    term: str
    definition: str
    familiarity_level: Optional[FamiliarityLevelEnum]
    next_review: Optional[datetime]

class ReviewTermList(BaseModel):
    study_set_id: int
    terms: List[ReviewTerm]

class StudySessionBase(BaseModel):
    study_mode: StudyModeEnum
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    score: Optional[float]
    total_questions: Optional[int]
    correct_answers: Optional[int]
    time_spent_seconds: Optional[int]

class StudySessionCreate(StudySessionBase):
    study_set_id: int

class StudySessionUpdate(BaseModel):
    completed_at: Optional[datetime]
    score: Optional[float]
    correct_answers: Optional[int]
    time_spent_seconds: Optional[int]

class StudySessionResponse(StudySessionBase):
    id: int
    user_id: int
    study_set_id: int

    class Config:
        orm_mode = True