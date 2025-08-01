from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from app.models.social import Favorite, Rating
from app.models.study_set import StudySet
from app.models.user import User
from app.schemas.social import FavoriteCreate, RatingCreate, RatingUpdate
from fastapi import HTTPException, status


class SocialService:
    @staticmethod
    def toggle_favorite(db: Session, user_id: int, study_set_id: int) -> Dict[str, Any]:
        """Toggle favorite status for a study set"""
        # Check if study set exists
        study_set = db.query(StudySet).filter(StudySet.id == study_set_id).first()
        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found"
            )

        # Check if already favorited
        existing_favorite = db.query(Favorite).filter(
            and_(Favorite.user_id == user_id, Favorite.study_set_id == study_set_id)
        ).first()

        if existing_favorite:
            # Remove from favorites
            db.delete(existing_favorite)
            study_set.favorites_count = max(0, study_set.favorites_count - 1)
            db.commit()
            return {"is_favorited": False, "favorites_count": study_set.favorites_count}
        else:
            # Add to favorites
            new_favorite = Favorite(user_id=user_id, study_set_id=study_set_id)
            db.add(new_favorite)
            study_set.favorites_count += 1
            db.commit()
            db.refresh(new_favorite)
            return {"is_favorited": True, "favorites_count": study_set.favorites_count}

    @staticmethod
    def get_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all favorited study sets for a user"""
        favorites = db.query(Favorite, StudySet).join(StudySet).filter(
            Favorite.user_id == user_id
        ).offset(skip).limit(limit).all()

        result = []
        for favorite, study_set in favorites:
            study_set_dict = {
                "id": study_set.id,
                "title": study_set.title,
                "description": study_set.description,
                "user_id": study_set.user_id,
                "is_public": study_set.is_public,
                "created_at": study_set.created_at,
                "updated_at": study_set.updated_at,
                "terms_count": study_set.terms_count,
                "language_from": study_set.language_from,
                "language_to": study_set.language_to,
                "views_count": study_set.views_count,
                "favorites_count": study_set.favorites_count,
                "average_rating": study_set.average_rating,
                "favorited_at": favorite.favorited_at
            }
            result.append(study_set_dict)

        return result

    @staticmethod
    def create_or_update_rating(db: Session, user_id: int, study_set_id: int, rating_data: RatingCreate) -> Rating:
        """Create or update a rating for a study set"""
        # Check if study set exists
        study_set = db.query(StudySet).filter(StudySet.id == study_set_id).first()
        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found"
            )

        # Check if user is trying to rate their own study set
        if study_set.user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot rate your own study set"
            )

        # Check if rating already exists
        existing_rating = db.query(Rating).filter(
            and_(Rating.user_id == user_id, Rating.study_set_id == study_set_id)
        ).first()

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_data.rating
            existing_rating.comment = rating_data.comment
            db.commit()
            db.refresh(existing_rating)
            rating = existing_rating
        else:
            # Create new rating
            rating = Rating(
                user_id=user_id,
                study_set_id=study_set_id,
                rating=rating_data.rating,
                comment=rating_data.comment
            )
            db.add(rating)
            db.commit()
            db.refresh(rating)

        # Update study set average rating
        SocialService._update_study_set_average_rating(db, study_set_id)
        
        return rating

    @staticmethod
    def get_rating_summary(db: Session, study_set_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get rating summary for a study set"""
        # Check if study set exists
        study_set = db.query(StudySet).filter(StudySet.id == study_set_id).first()
        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found"
            )

        # Get all ratings for this study set
        ratings = db.query(Rating).filter(Rating.study_set_id == study_set_id).all()

        if not ratings:
            return {
                "study_set_id": study_set_id,
                "average_rating": 0.0,
                "total_ratings": 0,
                "rating_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                "user_rating": None,
                "user_comment": None
            }

        # Calculate average rating
        total_rating = sum(r.rating for r in ratings)
        average_rating = total_rating / len(ratings)

        # Calculate rating distribution
        distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for r in ratings:
            distribution[str(r.rating)] += 1

        # Get user's rating if provided
        user_rating = None
        user_comment = None
        if user_id:
            user_rating_obj = db.query(Rating).filter(
                and_(Rating.user_id == user_id, Rating.study_set_id == study_set_id)
            ).first()
            if user_rating_obj:
                user_rating = user_rating_obj.rating
                user_comment = user_rating_obj.comment

        return {
            "study_set_id": study_set_id,
            "average_rating": round(average_rating, 2),
            "total_ratings": len(ratings),
            "rating_distribution": distribution,
            "user_rating": user_rating,
            "user_comment": user_comment
        }

    @staticmethod
    def get_all_ratings(db: Session, study_set_id: int, skip: int = 0, limit: int = 100) -> List[Rating]:
        """Get all ratings for a study set with user information"""
        ratings = db.query(Rating, User).join(User).filter(
            Rating.study_set_id == study_set_id
        ).offset(skip).limit(limit).all()

        result = []
        for rating, user in ratings:
            rating_dict = {
                "id": rating.id,
                "study_set_id": rating.study_set_id,
                "user_id": rating.user_id,
                "rating": rating.rating,
                "comment": rating.comment,
                "created_at": rating.created_at,
                "updated_at": rating.updated_at,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url
                }
            }
            result.append(rating_dict)

        return result

    @staticmethod
    def delete_rating(db: Session, user_id: int, study_set_id: int) -> bool:
        """Delete a user's rating for a study set"""
        rating = db.query(Rating).filter(
            and_(Rating.user_id == user_id, Rating.study_set_id == study_set_id)
        ).first()

        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found"
            )

        db.delete(rating)
        db.commit()

        # Update study set average rating
        SocialService._update_study_set_average_rating(db, study_set_id)
        
        return True

    @staticmethod
    def _update_study_set_average_rating(db: Session, study_set_id: int) -> None:
        """Update the average rating for a study set"""
        # Calculate new average rating
        result = db.query(func.avg(Rating.rating)).filter(
            Rating.study_set_id == study_set_id
        ).scalar()

        average_rating = float(result) if result else 0.0

        # Update study set
        study_set = db.query(StudySet).filter(StudySet.id == study_set_id).first()
        if study_set:
            study_set.average_rating = average_rating
            db.commit() 