from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


def _to_user_dict(user: User) -> dict:
    """Convert SQLAlchemy user to dict with only required fields"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "is_premium": user.is_premium,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_active_at": user.last_active_at,
        "total_study_sets_created": user.total_study_sets_created,
        "total_terms_learned": user.total_terms_learned
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    data = _to_user_dict(current_user)
    resp = UserResponse.model_validate(data)
    return resp


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    # Update user fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    data = _to_user_dict(current_user)
    resp = UserResponse.model_validate(data)
    return resp


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID (public information only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    data = _to_user_dict(user)
    resp = UserResponse.model_validate(data)
    return resp 