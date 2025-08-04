from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FolderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên thư mục")
    description: Optional[str] = Field(None, description="Mô tả thư mục")
    color: Optional[str] = Field(None, max_length=20, description="Màu sắc thư mục")
    icon: Optional[str] = Field(None, max_length=50, description="Biểu tượng thư mục")
    is_public: Optional[bool] = Field(False, description="Công khai hay riêng tư")


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    is_public: Optional[bool] = None


class FolderPublicToggle(BaseModel):
    is_public: bool = Field(..., description="Công khai hay riêng tư")


class FolderResponse(FolderBase):
    id: int
    user_id: int
    position: int
    study_sets_count: int = 0  # Sẽ được tính toán
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class FolderDetailResponse(FolderResponse):
    study_sets: List[dict] = []  # Sẽ chứa thông tin study sets


class FolderReorder(BaseModel):
    folder_ids: List[int] = Field(..., min_items=1, description="Danh sách ID thư mục theo thứ tự mới")


class FolderColorsIcons(BaseModel):
    colors: List[str] = [
        "#3B82F6", "#EF4444", "#10B981", "#F59E0B", 
        "#8B5CF6", "#EC4899", "#6B7280", "#F97316",
        "#06B6D4", "#84CC16", "#A855F7", "#F43F5E"
    ]
    icons: List[str] = [
        "folder", "book", "language", "science", "history", 
        "math", "music", "art", "sports", "business",
        "computer", "medical", "travel", "food", "nature",
        "star", "heart", "fire", "lightning", "moon", "sun"
    ]


class StudySetInFolder(BaseModel):
    id: int
    title: str
    description: Optional[str]
    terms_count: int
    color: Optional[str]
    is_public: bool
    added_at: datetime
    model_config = {"from_attributes": True}


class FolderStudySetsResponse(BaseModel):
    folder: FolderResponse
    study_sets: List[StudySetInFolder]
    total: int 