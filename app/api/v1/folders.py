from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.folder import (
    FolderCreate, FolderUpdate, FolderResponse, FolderDetailResponse,
    FolderReorder, FolderColorsIcons, FolderStudySetsResponse, StudySetInFolder,
    FolderPublicToggle
)
from app.services.folder_service import FolderService

router = APIRouter()


@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo thư mục mới"""
    folder = FolderService.create_folder(db, folder_data, current_user.id)
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    return FolderResponse.model_validate(folder_dict)


@router.get("/user/me", response_model=List[FolderResponse])
def get_my_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách thư mục của user hiện tại"""
    folders = FolderService.get_user_folders(db, current_user.id)
    result = []
    for folder in folders:
        folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
        result.append(FolderResponse.model_validate(folder_dict))
    return result


@router.get("/public", response_model=List[FolderResponse])
def get_public_folders(
    limit: int = Query(50, ge=1, le=100, description="Số lượng thư mục tối đa"),
    offset: int = Query(0, ge=0, description="Số thư mục bỏ qua"),
    db: Session = Depends(get_db)
):
    """Lấy danh sách thư mục public (không cần đăng nhập)"""
    folders = FolderService.get_public_folders(db, limit=limit, offset=offset)
    result = []
    for folder in folders:
        folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
        result.append(FolderResponse.model_validate(folder_dict))
    return result


@router.put("/reorder", response_model=List[FolderResponse])
def reorder_folders(
    reorder_data: FolderReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sắp xếp lại thứ tự thư mục"""
    success = FolderService.reorder_folders(db, reorder_data.folder_ids, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể sắp xếp lại thư mục"
        )
    
    # Trả về danh sách thư mục đã sắp xếp
    folders = FolderService.get_user_folders(db, current_user.id)
    result = []
    for folder in folders:
        folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
        result.append(FolderResponse.model_validate(folder_dict))
    return result


@router.get("/colors-icons", response_model=FolderColorsIcons)
def get_colors_and_icons():
    """Lấy danh sách màu sắc và biểu tượng có sẵn"""
    return FolderColorsIcons()


@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy chi tiết thư mục (cho user sở hữu)"""
    folder = FolderService.get_folder_by_id(db, folder_id, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại"
        )
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    return FolderResponse.model_validate(folder_dict)


@router.get("/public/{folder_id}", response_model=FolderResponse)
def get_public_folder(
    folder_id: int,
    db: Session = Depends(get_db)
):
    """Lấy chi tiết thư mục public (không cần đăng nhập)"""
    folder = FolderService.get_public_folder_by_id(db, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại hoặc không công khai"
        )
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    return FolderResponse.model_validate(folder_dict)


@router.put("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật thông tin thư mục"""
    folder = FolderService.update_folder(db, folder_id, folder_data, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại"
        )
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    return FolderResponse.model_validate(folder_dict)


@router.put("/{folder_id}/public", response_model=FolderResponse)
def toggle_folder_public(
    folder_id: int,
    public_data: FolderPublicToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chuyển đổi trạng thái public/private của thư mục"""
    folder = FolderService.toggle_folder_public(db, folder_id, current_user.id, public_data.is_public)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại"
        )
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    return FolderResponse.model_validate(folder_dict)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa thư mục"""
    success = FolderService.delete_folder(db, folder_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại"
        )


# Study Sets trong Folders
@router.get("/{folder_id}/study-sets", response_model=FolderStudySetsResponse)
def get_study_sets_in_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách study sets trong thư mục (cho user sở hữu)"""
    # Lấy thông tin folder
    folder = FolderService.get_folder_by_id(db, folder_id, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại"
        )
    
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    folder_response = FolderResponse.model_validate(folder_dict)
    
    # Lấy study sets trong folder
    study_sets_data = FolderService.get_study_sets_in_folder(db, folder_id, current_user.id)
    study_sets = [StudySetInFolder.model_validate(data) for data in study_sets_data]
    
    return FolderStudySetsResponse(
        folder=folder_response,
        study_sets=study_sets,
        total=len(study_sets)
    )


@router.get("/public/{folder_id}/study-sets", response_model=FolderStudySetsResponse)
def get_public_study_sets_in_folder(
    folder_id: int,
    db: Session = Depends(get_db)
):
    """Lấy danh sách study sets public trong thư mục (cho public access)"""
    # Lấy thông tin folder
    folder = FolderService.get_public_folder_by_id(db, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thư mục không tồn tại hoặc không công khai"
        )
    
    folder_dict = FolderService.get_folder_with_study_sets_count(db, folder)
    folder_response = FolderResponse.model_validate(folder_dict)
    
    # Lấy study sets public trong folder
    study_sets_data = FolderService.get_public_study_sets_in_folder(db, folder_id)
    study_sets = [StudySetInFolder.model_validate(data) for data in study_sets_data]
    
    return FolderStudySetsResponse(
        folder=folder_response,
        study_sets=study_sets,
        total=len(study_sets)
    )


@router.post("/{folder_id}/study-sets/{study_set_id}", status_code=status.HTTP_201_CREATED)
def add_study_set_to_folder(
    folder_id: int,
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Thêm study set vào thư mục"""
    success = FolderService.add_study_set_to_folder(db, folder_id, study_set_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể thêm study set vào thư mục"
        )
    return {"message": "Đã thêm study set vào thư mục"}


@router.delete("/{folder_id}/study-sets/{study_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_study_set_from_folder(
    folder_id: int,
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa study set khỏi thư mục"""
    success = FolderService.remove_study_set_from_folder(db, folder_id, study_set_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set không tồn tại trong thư mục"
        )


# Endpoint để di chuyển study set giữa các thư mục (đặt trong study_sets.py)
# PUT /api/v1/study-sets/{study_set_id}/move-to-folder/{folder_id} 