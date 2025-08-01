from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FolderBase(BaseModel):
    name: str


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: Optional[str] = None


class FolderResponse(FolderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    study_sets_count: Optional[int] = 0
    
    model_config = {"from_attributes": True}


class FolderStudySetCreate(BaseModel):
    study_set_id: int


class FolderStudySetResponse(BaseModel):
    id: int
    folder_id: int
    study_set_id: int
    added_at: datetime
    
    model_config = {"from_attributes": True}


class FolderWithStudySets(FolderResponse):
    study_sets: List[dict] = [] 