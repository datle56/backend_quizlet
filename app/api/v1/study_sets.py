from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.study_set import (
    StudySetCreate, StudySetUpdate, StudySetResponse, StudySetDetailResponse,
    StudySetListResponse, StudySetSearchParams, StudySetListItem,
    TermCreate, TermUpdate, TermResponse, TermBulkCreate, TermReorder
)
from app.services.study_set_service import StudySetService, TermService
from app.services.folder_service import FolderService
from app.schemas.user import UserResponse
from pydantic import BaseModel

router = APIRouter()


class StudySetPublicToggle(BaseModel):
    is_public: bool


def _get_user_info(user: User) -> dict:
    """Convert user to dict for response"""
    return {
        "id": user.id,
        "last_name": user.last_name,
        "first_name": user.first_name,
        "avatar_url": user.avatar_url
    }


def _to_study_set_dict(study_set) -> dict:
    """Convert SQLAlchemy study_set to dict with only required fields"""
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
        "average_rating": study_set.average_rating,
        "color": getattr(study_set, "color", None)
    }


def _to_term_dict(term) -> dict:
    """Convert SQLAlchemy term to dict with only required fields"""
    return {
        "id": term.id,
        "term": term.term,
        "definition": term.definition,
        "image_url": term.image_url,
        "audio_url": term.audio_url,
        "study_set_id": term.study_set_id,
        "position": term.position,
        "created_at": term.created_at,
        "updated_at": term.updated_at
    }


@router.post("/", response_model=StudySetResponse, status_code=status.HTTP_201_CREATED)
def create_study_set(
    study_set_data: StudySetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new study set"""
    study_set = StudySetService.create_study_set(
        db, study_set_data, current_user.id)
    data = _to_study_set_dict(study_set)
    data["user"] = _get_user_info(current_user)
    resp = StudySetResponse.model_validate(data)
    return resp


@router.get("/{study_set_id}", response_model=StudySetDetailResponse)
def get_study_set(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get study set details with terms"""
    study_set = StudySetService.get_study_set_by_id(db, study_set_id)
    if not study_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found"
        )
    if not study_set.is_public and (not current_user or current_user.id != study_set.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    terms = TermService.get_terms_by_study_set(db, study_set_id)
    term_responses = [TermResponse.model_validate(
        _to_term_dict(term)) for term in terms]
    user = db.query(User).filter(User.id == study_set.user_id).first()
    user_info = _get_user_info(user) if user else {}
    data = _to_study_set_dict(study_set)
    data["user"] = user_info
    data["terms"] = term_responses
    resp = StudySetDetailResponse.model_validate(data)
    return resp


@router.get("/public/{study_set_id}", response_model=StudySetDetailResponse)
def get_public_study_set(
    study_set_id: int,
    db: Session = Depends(get_db)
):
    """Get public study set details with terms (no authentication required)"""
    study_set = StudySetService.get_public_study_set_by_id(db, study_set_id)
    if not study_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found or not public"
        )
    terms = TermService.get_terms_by_study_set(db, study_set_id)
    term_responses = [TermResponse.model_validate(
        _to_term_dict(term)) for term in terms]
    user = db.query(User).filter(User.id == study_set.user_id).first()
    user_info = _get_user_info(user) if user else {}
    data = _to_study_set_dict(study_set)
    data["user"] = user_info
    data["terms"] = term_responses
    resp = StudySetDetailResponse.model_validate(data)
    return resp


@router.put("/{study_set_id}", response_model=StudySetResponse)
def update_study_set(
    study_set_id: int,
    study_set_data: StudySetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update study set"""
    study_set = StudySetService.update_study_set(
        db, study_set_id, study_set_data, current_user.id)
    data = _to_study_set_dict(study_set)
    data["user"] = _get_user_info(current_user)
    resp = StudySetResponse.model_validate(data)
    return resp


@router.put("/{study_set_id}/public", response_model=StudySetResponse)
def toggle_study_set_public(
    study_set_id: int,
    public_data: StudySetPublicToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle study set public/private status"""
    study_set = StudySetService.toggle_study_set_public(
        db, study_set_id, current_user.id, public_data.is_public)
    if not study_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found"
        )
    data = _to_study_set_dict(study_set)
    data["user"] = _get_user_info(current_user)
    resp = StudySetResponse.model_validate(data)
    return resp


@router.delete("/{study_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_set(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete study set"""
    StudySetService.delete_study_set(db, study_set_id, current_user.id)


@router.get("/", response_model=StudySetListResponse)
def search_study_sets(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    language_from: Optional[str] = Query(None, description="Source language"),
    language_to: Optional[str] = Query(None, description="Target language"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    min_rating: Optional[float] = Query(
        None, ge=0, le=5, description="Minimum rating"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """Search and filter study sets (public only)"""
    params = StudySetSearchParams(
        page=page,
        size=size,
        search=search,
        language_from=language_from,
        language_to=language_to,
        user_id=user_id,
        min_rating=min_rating,
        sort_by=sort_by,
        sort_order=sort_order
    )
    study_sets, total = StudySetService.search_public_study_sets(db, params)
    items = []
    for study_set in study_sets:
        user = db.query(User).filter(User.id == study_set.user_id).first()
        user_info = _get_user_info(user) if user else {}
        data = _to_study_set_dict(study_set)
        data["user"] = user_info
        item = StudySetListItem.model_validate(data)
        items.append(item)
    pages = (total + params.size - 1) // params.size
    return StudySetListResponse(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
        pages=pages
    )


@router.get("/user/me", response_model=List[StudySetResponse])
def get_my_study_sets(
    include_private: bool = Query(
        True, description="Include private study sets"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's study sets"""
    study_sets = StudySetService.get_user_study_sets(
        db, current_user.id, include_private)
    result = []
    for study_set in study_sets:
        data = _to_study_set_dict(study_set)
        data["user"] = _get_user_info(current_user)
        resp = StudySetResponse.model_validate(data)
        result.append(resp)
    return result


# Terms endpoints
@router.post("/{study_set_id}/terms/", response_model=TermResponse, status_code=status.HTTP_201_CREATED)
def create_term(
    study_set_id: int,
    term_data: TermCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new term to study set"""
    term = TermService.create_term(
        db, study_set_id, term_data.dict(), current_user.id)
    return TermResponse.model_validate(_to_term_dict(term))


@router.get("/{study_set_id}/terms/", response_model=List[TermResponse])
def get_terms(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get all terms for a study set"""
    study_set = StudySetService.get_study_set_by_id(
        db, study_set_id, increment_views=False)
    if not study_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found"
        )
    if not study_set.is_public and (not current_user or current_user.id != study_set.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    terms = TermService.get_terms_by_study_set(db, study_set_id)
    return [TermResponse.model_validate(_to_term_dict(term)) for term in terms]


@router.get("/public/{study_set_id}/terms/", response_model=List[TermResponse])
def get_public_terms(
    study_set_id: int,
    db: Session = Depends(get_db)
):
    """Get all terms for a public study set (no authentication required)"""
    study_set = StudySetService.get_public_study_set_by_id(db, study_set_id)
    if not study_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found or not public"
        )
    terms = TermService.get_terms_by_study_set(db, study_set_id)
    return [TermResponse.model_validate(_to_term_dict(term)) for term in terms]


@router.put("/{study_set_id}/terms/{term_id}", response_model=TermResponse)
def update_term(
    study_set_id: int,
    term_id: int,
    term_data: TermUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a term"""
    update_data = term_data.dict(exclude_unset=True)
    term = TermService.update_term(
        db, study_set_id, term_id, update_data, current_user.id)
    return TermResponse.model_validate(_to_term_dict(term))


@router.delete("/{study_set_id}/terms/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_term(
    study_set_id: int,
    term_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a term"""
    TermService.delete_term(db, study_set_id, term_id, current_user.id)


@router.post("/{study_set_id}/terms/bulk", response_model=List[TermResponse], status_code=status.HTTP_201_CREATED)
def bulk_create_terms(
    study_set_id: int,
    terms_data: TermBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple terms at once"""
    terms = TermService.bulk_create_terms(
        db, study_set_id, [term.dict()
                           for term in terms_data.terms], current_user.id
    )
    return [TermResponse.model_validate(_to_term_dict(term)) for term in terms]


@router.put("/{study_set_id}/terms/reorder", response_model=List[TermResponse])
def reorder_terms(
    study_set_id: int,
    reorder_data: TermReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reorder terms by updating their positions"""
    terms = TermService.reorder_terms(
        db, study_set_id, reorder_data.term_ids, current_user.id)
    return [TermResponse.model_validate(_to_term_dict(term)) for term in terms]


@router.put("/{study_set_id}/move-to-folder/{folder_id}")
def move_study_set_to_folder(
    study_set_id: int,
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Di chuyển study set sang thư mục khác"""
    success = FolderService.move_study_set_to_folder(db, study_set_id, folder_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể di chuyển study set"
        )
    return {"message": "Đã di chuyển study set sang thư mục mới"}
