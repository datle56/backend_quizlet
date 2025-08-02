from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class UserStats(BaseModel):
    total_study_sets_created: int
    total_terms_learned: int
    total_study_sessions: int
    total_time_studied_minutes: int
    average_score: float
    study_streak_days: int
    favorite_study_sets_count: int
    classes_joined_count: int
    last_active_at: Optional[datetime]


class StudySetStats(BaseModel):
    total_views: int
    total_favorites: int
    total_ratings: int
    average_rating: float
    total_study_sessions: int
    total_time_studied_minutes: int
    unique_students_count: int
    completion_rate: float
    difficulty_distribution: Dict[str, int]


class ClassStats(BaseModel):
    total_members: int
    total_study_sets: int
    total_study_sessions: int
    average_student_progress: float
    top_students: List[Dict[str, Any]]
    most_popular_study_sets: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class StudySessionStats(BaseModel):
    total_sessions: int
    total_time_minutes: int
    average_score: float
    sessions_by_mode: Dict[str, int]
    sessions_by_date: List[Dict[str, Any]]
    improvement_trend: List[Dict[str, Any]]


class AnalyticsResponse(BaseModel):
    user_stats: Optional[UserStats] = None
    study_set_stats: Optional[StudySetStats] = None
    class_stats: Optional[ClassStats] = None
    study_session_stats: Optional[StudySessionStats] = None 