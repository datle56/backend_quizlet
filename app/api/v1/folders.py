from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.folder import (
    FolderCreate, FolderUpdate, FolderResponse, FolderStudySetCreate,
    FolderStudySetResponse, FolderWithStudySets
)
from app.services.folder_service import FolderService

router = APIRouter(prefix="/folders", tags=["folders"])


def _to_folder_dict(folder) -> dict:
    """Convert SQLAlchemy folder to dict"""
    return {
        "id": folder.id,
        "name": folder.name,
        "user_id": folder.user_id,
        "created_at": folder.created_at,
        "updated_at": folder.updated_at,
        "study_sets_count": len(folder.study_sets) if hasattr(folder, 'study_sets') else 0
    }


def _to_study_set_dict(study_set) -> dict:
    """Convert SQLAlchemy study_set to dict"""
    return {
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
        "average_rating": study_set.average_rating
    }


@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new folder"""
    folder = FolderService.create_folder(db, folder_data, current_user.id)
    data = _to_folder_dict(folder)
    return FolderResponse.model_validate(data)


@router.get("/", response_model=List[FolderResponse])
def get_user_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all folders for current user"""
    folders = FolderService.get_user_folders(db, current_user.id)
    return [FolderResponse.model_validate(_to_folder_dict(folder)) for folder in folders]


@router.get("/{folder_id}", response_model=FolderWithStudySets)
def get_folder_with_study_sets(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get folder with its study sets"""
    result = FolderService.get_folder_with_study_sets(db, folder_id, current_user.id)
    folder_data = _to_folder_dict(result["folder"])
    study_sets_data = [_to_study_set_dict(study_set) for study_set in result["study_sets"]]
    
    folder_data["study_sets"] = study_sets_data
    return FolderWithStudySets.model_validate(folder_data)


@router.put("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update folder"""
    folder = FolderService.update_folder(db, folder_id, folder_data, current_user.id)
    data = _to_folder_dict(folder)
    return FolderResponse.model_validate(data)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete folder"""
    FolderService.delete_folder(db, folder_id, current_user.id)
    return None


@router.post("/{folder_id}/study-sets", response_model=FolderStudySetResponse, status_code=status.HTTP_201_CREATED)
def add_study_set_to_folder(
    folder_id: int,
    study_set_data: FolderStudySetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add study set to folder"""
    folder_study_set = FolderService.add_study_set_to_folder(
        db, folder_id, study_set_data.study_set_id, current_user.id
    )
    return FolderStudySetResponse.model_validate({
        "id": folder_study_set.id,
        "folder_id": folder_study_set.folder_id,
        "study_set_id": folder_study_set.study_set_id,
        "added_at": folder_study_set.added_at
    })


@router.delete("/{folder_id}/study-sets/{study_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_study_set_from_folder(
    folder_id: int,
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove study set from folder"""
    FolderService.remove_study_set_from_folder(db, folder_id, study_set_id, current_user.id)
    return None 