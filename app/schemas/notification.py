from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    type: str = Field(..., description="Type of notification")
    related_entity_type: Optional[str] = Field(None, description="Type of related entity")
    related_entity_id: Optional[int] = Field(None, description="ID of related entity")
    message: str = Field(..., description="Notification message")


class NotificationCreate(NotificationBase):
    user_id: int = Field(..., description="User ID to receive notification")


class NotificationUpdate(BaseModel):
    is_read: bool = Field(..., description="Read status")


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationStats(BaseModel):
    total_notifications: int
    unread_notifications: int
    notifications_by_type: dict[str, int] 