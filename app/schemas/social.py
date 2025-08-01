from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FavoriteBase(BaseModel):
    study_set_id: int = Field(..., description="ID of the study set to favorite")


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    favorited_at: datetime

    class Config:
        from_attributes = True


class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, description="Optional comment for the rating")


class RatingCreate(RatingBase):
    pass


class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, description="Optional comment for the rating")


class RatingResponse(RatingBase):
    id: int
    study_set_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudySetWithFavorite(BaseModel):
    id: int
    title: str
    description: Optional[str]
    user_id: int
    is_public: bool
    created_at: datetime
    updated_at: datetime
    terms_count: int
    language_from: Optional[str]
    language_to: Optional[str]
    views_count: int
    favorites_count: int
    average_rating: Optional[float]
    favorited_at: datetime

    class Config:
        from_attributes = True


class StudySetWithRating(BaseModel):
    id: int
    title: str
    description: Optional[str]
    user_id: int
    is_public: bool
    created_at: datetime
    updated_at: datetime
    terms_count: int
    language_from: Optional[str]
    language_to: Optional[str]
    views_count: int
    favorites_count: int
    average_rating: Optional[float]
    user_rating: Optional[int]
    user_comment: Optional[str]

    class Config:
        from_attributes = True


class RatingSummary(BaseModel):
    study_set_id: int
    average_rating: float
    total_ratings: int
    rating_distribution: dict  # e.g., {"1": 5, "2": 10, "3": 15, "4": 20, "5": 25}
    user_rating: Optional[int] = None
    user_comment: Optional[str] = None

    class Config:
        from_attributes = True 