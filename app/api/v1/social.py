from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.social import (
    FavoriteResponse, RatingCreate, RatingResponse, RatingSummary,
    StudySetWithFavorite, StudySetWithRating
)
from app.services.social_service import SocialService

router = APIRouter()


@router.post("/favorites/{study_set_id}", response_model=dict)
def toggle_favorite(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status for a study set"""
    result = SocialService.toggle_favorite(db, current_user.id, study_set_id)
    return result


@router.get("/favorites", response_model=List[StudySetWithFavorite])
def get_user_favorites(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorited study sets for the current user"""
    favorites = SocialService.get_user_favorites(db, current_user.id, skip, limit)
    return [StudySetWithFavorite.model_validate(fav) for fav in favorites]


@router.post("/ratings/{study_set_id}", response_model=RatingResponse)
def create_or_update_rating(
    study_set_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a rating for a study set"""
    rating = SocialService.create_or_update_rating(db, current_user.id, study_set_id, rating_data)
    return RatingResponse.model_validate(rating)


@router.get("/ratings/{study_set_id}", response_model=RatingSummary)
def get_rating_summary(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get rating summary for a study set"""
    user_id = current_user.id if current_user else None
    summary = SocialService.get_rating_summary(db, study_set_id, user_id)
    return RatingSummary.model_validate(summary)


@router.get("/ratings/{study_set_id}/all", response_model=List[dict])
def get_all_ratings(
    study_set_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """Get all ratings for a study set with user information"""
    ratings = SocialService.get_all_ratings(db, study_set_id, skip, limit)
    return ratings


@router.delete("/ratings/{study_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the current user's rating for a study set"""
    SocialService.delete_rating(db, current_user.id, study_set_id)
    return None 