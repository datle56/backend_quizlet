from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TermBase(BaseModel):
    term: str = Field(..., min_length=1, max_length=500)
    definition: str = Field(..., min_length=1)
    image_url: Optional[str] = None
    audio_url: Optional[str] = None


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    term: Optional[str] = Field(None, min_length=1, max_length=500)
    definition: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = None
    audio_url: Optional[str] = None


class TermResponse(TermBase):
    id: int
    study_set_id: int
    position: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TermBulkCreate(BaseModel):
    terms: List[TermCreate]


class TermReorder(BaseModel):
    term_ids: List[int] = Field(..., min_items=1)


class StudySetBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = True
    language_from: Optional[str] = Field(None, max_length=10)
    language_to: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=20, description="Màu chủ đề")


class StudySetCreate(StudySetBase):
    pass


class StudySetUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    language_from: Optional[str] = Field(None, max_length=10)
    language_to: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=20, description="Màu chủ đề")


class StudySetResponse(StudySetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    terms_count: int
    views_count: int
    favorites_count: int
    average_rating: float
    color: Optional[str]
    user: dict  # Will be populated with user info
    model_config = {"from_attributes": True}


class StudySetDetailResponse(StudySetResponse):
    terms: List[TermResponse] = []
    model_config = {"from_attributes": True}


class StudySetListItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime
    terms_count: int
    views_count: int
    favorites_count: int
    average_rating: float
    language_from: Optional[str]
    language_to: Optional[str]
    color: Optional[str]
    is_public: bool
    user: dict  # Will be populated with user info
    model_config = {"from_attributes": True}


class StudySetSearchParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    language_from: Optional[str] = None
    language_to: Optional[str] = None
    user_id: Optional[int] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    sort_by: str = Field(
        "created_at", pattern="^(created_at|title|views_count|favorites_count|average_rating)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class StudySetListResponse(BaseModel):
    items: List[StudySetListItem]
    total: int
    page: int
    size: int
    pages: int
