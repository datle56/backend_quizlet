from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse, NotificationListResponse, NotificationStats,
    NotificationUpdate
)
from app.services.notification_service import NotificationService
from app.models.notification import Notification
from app.models.study_set import StudySet
from app.models.class_ import Class

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notifications for the current user"""
    notifications = NotificationService.get_user_notifications(
        db, current_user.id, skip, limit, unread_only
    )
    
    # Get total counts
    total = NotificationService.get_notification_stats(db, current_user.id)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(notif) for notif in notifications],
        total=total["total_notifications"],
        unread_count=total["unread_notifications"]
    )


@router.get("/stats", response_model=NotificationStats)
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for the current user"""
    stats = NotificationService.get_notification_stats(db, current_user.id)
    return NotificationStats.model_validate(stats)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a specific notification as read"""
    notification = NotificationService.mark_as_read(db, notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return NotificationResponse.model_validate(notification)


@router.put("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    count = NotificationService.mark_all_as_read(db, current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification (only if it belongs to the current user)"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    return None


@router.post("/test-email", response_model=dict)
def test_email_notification(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test email notification (for development)"""
    subject = "Test Notification from Quizlet"
    message = f"Hello {current_user.username}, this is a test notification!"
    
    background_tasks.add_task(
        NotificationService.send_email_notification,
        current_user.email,
        subject,
        message
    )
    
    return {"message": "Test email notification sent"}


@router.post("/test-push", response_model=dict)
def test_push_notification(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test push notification (for development)"""
    title = "Test Push Notification"
    body = f"Hello {current_user.username}, this is a test push notification!"
    
    background_tasks.add_task(
        NotificationService.send_push_notification,
        current_user.id,
        title,
        body
    )
    
    return {"message": "Test push notification sent"}


@router.post("/study-reminder/{study_set_id}", response_model=NotificationResponse)
def create_study_reminder(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a study reminder notification"""
    # Get study set title
    study_set = db.query(StudySet).filter(StudySet.id == study_set_id).first()
    if not study_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found"
        )
    
    notification = NotificationService.create_study_reminder_notification(
        db, current_user.id, study_set_id, study_set.title
    )
    
    return NotificationResponse.model_validate(notification)


@router.post("/class-notification/{class_id}", response_model=NotificationResponse)
def create_class_notification(
    class_id: int,
    notification_type: str = Query(..., description="Type of notification"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a class-related notification"""
    # Get class name
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    notification = NotificationService.create_class_notification(
        db, current_user.id, class_obj.name, notification_type, class_id
    )
    
    return NotificationResponse.model_validate(notification) 