from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ClassBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None  # Môn học (optional)
    school: Optional[str] = None   # Trường/Tổ chức (optional)


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None  # Môn học (optional)
    school: Optional[str] = None   # Trường/Tổ chức (optional)
    is_active: Optional[bool] = None


class ClassJoin(BaseModel):
    join_code: str


class ClassResponse(ClassBase):
    id: int
    teacher_id: int
    join_code: str
    created_at: datetime
    is_active: bool
    member_count: Optional[int] = None
    study_set_count: Optional[int] = None

    class Config:
        from_attributes = True


class ClassMemberBase(BaseModel):
    role: str = "student"


class ClassMemberCreate(ClassMemberBase):
    pass


class ClassMemberResponse(BaseModel):
    id: int
    class_id: int
    user_id: int
    role: str
    joined_at: datetime
    user: Optional[dict] = None

    class Config:
        from_attributes = True


class ClassStudySetBase(BaseModel):
    study_set_id: int
    due_date: Optional[datetime] = None
    is_optional: bool = False


class ClassStudySetCreate(ClassStudySetBase):
    pass


class ClassStudySetUpdate(BaseModel):
    due_date: Optional[datetime] = None
    is_optional: Optional[bool] = None


class ClassStudySetResponse(ClassStudySetBase):
    id: int
    class_id: int
    assigned_at: datetime
    study_set: Optional[dict] = None

    class Config:
        from_attributes = True


class ClassProgressResponse(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    total_assignments: int
    completed_assignments: int
    average_score: Optional[float] = None
    last_activity: Optional[datetime] = None


class ClassDetailResponse(ClassResponse):
    teacher: Optional[dict] = None
    members: List[ClassMemberResponse] = []
    study_sets: List[ClassStudySetResponse] = []