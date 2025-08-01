from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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
    gravity = 'gravity'


class QuestionTypeEnum(str, Enum):
    multiple_choice = 'multiple_choice'
    true_false = 'true_false'
    written = 'written'
    matching = 'matching'


class AnswerWithEnum(str, Enum):
    term = 'term'
    definition = 'definition'
    both = 'both'


# Base schemas
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
        from_attributes = True


class TermProgressUpdate(BaseModel):
    correct: bool
    response_time: Optional[float] = None
    difficulty: Optional[int] = None


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
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    total_questions: Optional[int] = None
    correct_answers: Optional[int] = None
    time_spent_seconds: Optional[int] = None


class StudySessionCreate(StudySessionBase):
    study_set_id: int


class StudySessionUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    total_questions: Optional[int] = None
    correct_answers: Optional[int] = None
    time_spent_seconds: Optional[int] = None


class StudySessionResponse(StudySessionBase):
    id: int
    user_id: int
    study_set_id: int

    class Config:
        from_attributes = True


# Flashcards Mode Schemas
class FlashcardResponse(BaseModel):
    term_id: int
    term: str
    definition: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    is_starred: bool = False
    familiarity_level: Optional[FamiliarityLevelEnum] = None
    position: int


class StarCardRequest(BaseModel):
    starred: bool = True


class StarredCardsResponse(BaseModel):
    study_set_id: int
    cards: List[FlashcardResponse]


# Learn Mode Schemas
class LearnOptions(BaseModel):
    study_with_spell: bool = False
    answer_with: AnswerWithEnum = AnswerWithEnum.both
    question_types: List[QuestionTypeEnum] = [QuestionTypeEnum.multiple_choice, QuestionTypeEnum.written]


class LearnQuestion(BaseModel):
    question_id: str
    term_id: int
    question_type: QuestionTypeEnum
    question_text: str
    correct_answer: str
    options: Optional[List[str]] = None
    difficulty_level: int = 1
    points_worth: int = 1


class LearnAnswer(BaseModel):
    question_id: str
    answer: str
    response_time: float


class LearnProgress(BaseModel):
    questions_answered: int
    correct_answers: int
    current_streak: int
    current_difficulty: int
    score: int


# Test Mode Schemas
class TestConfig(BaseModel):
    max_questions: int = Field(ge=5, le=100)
    answer_with: AnswerWithEnum = AnswerWithEnum.both
    question_types: List[QuestionTypeEnum] = [QuestionTypeEnum.multiple_choice, QuestionTypeEnum.true_false]
    time_limit: Optional[int] = Field(None, ge=60, le=3600)  # 1 minute to 1 hour
    randomize_order: bool = True


class TestSession(BaseModel):
    test_id: int
    study_set_id: int
    config: TestConfig
    total_questions: int
    time_limit: Optional[int]
    created_at: datetime


class TestQuestion(BaseModel):
    question_id: str
    term_id: int
    question_type: QuestionTypeEnum
    question_text: str
    correct_answer: str
    options: Optional[List[str]] = None
    points_worth: float = 1.0
    position: int


class TestAnswer(BaseModel):
    question_id: str
    answer: str
    time_spent: float


class TestSubmission(BaseModel):
    answers: List[TestAnswer]
    total_time_spent: float


class TestResult(BaseModel):
    test_id: int
    score: float
    total_questions: int
    correct_answers: int
    total_time_spent: float
    breakdown_by_type: Dict[str, Dict[str, Any]]
    incorrect_answers: List[Dict[str, Any]]
    suggested_review: List[int]  # term_ids


# Match Mode Schemas
class MatchGame(BaseModel):
    game_id: int
    study_set_id: int
    pairs_count: int
    selected_terms: List[int]  # term_ids
    max_time: Optional[int] = None


class MatchCard(BaseModel):
    card_id: str
    term_id: int
    content: str  # term or definition
    is_term: bool
    position: int


class MatchMove(BaseModel):
    first_card_id: str
    second_card_id: str


class MatchCompletion(BaseModel):
    completion_time: float
    incorrect_matches: int = 0


class MatchResult(BaseModel):
    game_id: int
    completion_time: float
    total_matches: int
    incorrect_matches: int
    score: int
    moves_history: List[Dict[str, Any]]


# Gravity Mode Schemas
class GravityGame(BaseModel):
    game_id: int
    study_set_id: int
    difficulty_level: int = 1
    lives_remaining: int = 3
    speed_multiplier: float = 1.0


class GravityTerm(BaseModel):
    term_id: int
    term: str
    definition: str
    appeared_at: datetime


class GravityAnswer(BaseModel):
    term_id: int
    answer: str
    time_to_answer: float


class GravityCompletion(BaseModel):
    final_score: int
    terms_destroyed: int
    game_duration: float
    lives_remaining: int


class GravityLeaderboardEntry(BaseModel):
    user_id: int
    username: str
    score: int
    terms_destroyed: int
    game_duration: float
    completed_at: datetime


# Write Mode Schemas
class WriteQuestion(BaseModel):
    question_id: str
    term_id: int
    prompt: str  # "What is the definition of X?" or "What term means Y?"
    correct_answer: str
    synonyms: List[str] = []
    points_worth: int = 1


class WriteAnswer(BaseModel):
    question_id: str
    answer: str
    response_time: float


class WriteValidation(BaseModel):
    is_correct: bool
    score: float
    feedback: str
    suggested_answer: Optional[str] = None
    partial_credit: bool = False


# Common Response Schemas
class StudyModeResponse(BaseModel):
    mode: StudyModeEnum
    study_set_id: int
    session_id: int
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
