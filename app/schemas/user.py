from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    email: EmailStr
    avatar_url: Optional[str] = None
    receive_tips: Optional[bool] = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None
    receive_tips: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_premium: bool
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None
    total_study_sets_created: int
    total_terms_learned: int
    receive_tips: Optional[bool] = False
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
