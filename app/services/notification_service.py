from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationService:
    
    @staticmethod
    def create_notification(
        db: Session, 
        user_id: int, 
        notification_type: str, 
        message: str, 
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def get_user_notifications(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        
        return notification
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        return result
    
    @staticmethod
    def get_notification_stats(db: Session, user_id: int) -> Dict:
        """Get notification statistics for a user"""
        total = db.query(Notification).filter(Notification.user_id == user_id).count()
        unread = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        # Get notifications by type
        type_stats = db.query(
            Notification.type,
            func.count(Notification.id).label('count')
        ).filter(Notification.user_id == user_id).group_by(Notification.type).all()
        
        notifications_by_type = {stat.type: stat.count for stat in type_stats}
        
        return {
            "total_notifications": total,
            "unread_notifications": unread,
            "notifications_by_type": notifications_by_type
        }
    
    @staticmethod
    def delete_old_notifications(db: Session, days_old: int = 30) -> int:
        """Delete notifications older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        result = db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        
        db.commit()
        return result
    
    @staticmethod
    async def send_email_notification(
        user_email: str, 
        subject: str, 
        message: str,
        smtp_config: Dict = None
    ):
        """Send email notification (background task)"""
        if not smtp_config:
            # Default configuration - should be moved to settings
            smtp_config = {
                "host": "smtp.gmail.com",
                "port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password"
            }
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config["username"]
            msg['To'] = user_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
            server.starttls()
            server.login(smtp_config["username"], smtp_config["password"])
            
            text = msg.as_string()
            server.sendmail(smtp_config["username"], user_email, text)
            server.quit()
            
            print(f"Email notification sent to {user_email}")
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    @staticmethod
    async def send_push_notification(user_id: int, title: str, body: str):
        """Send push notification (background task)"""
        # This would integrate with a push notification service like Firebase
        # For now, just log the notification
        print(f"Push notification for user {user_id}: {title} - {body}")
    
    @staticmethod
    def create_study_reminder_notification(
        db: Session, 
        user_id: int, 
        study_set_id: int, 
        study_set_title: str
    ):
        """Create a study reminder notification"""
        message = f"Time to study! Don't forget to review '{study_set_title}'"
        return NotificationService.create_notification(
            db, user_id, "study_reminder", message, "study_set", study_set_id
        )
    
    @staticmethod
    def create_class_notification(
        db: Session, 
        user_id: int, 
        class_name: str, 
        notification_type: str,
        related_entity_id: Optional[int] = None
    ):
        """Create a class-related notification"""
        messages = {
            "new_assignment": f"New assignment posted in {class_name}",
            "grade_posted": f"New grade posted in {class_name}",
            "class_announcement": f"New announcement in {class_name}"
        }
        
        message = messages.get(notification_type, f"New activity in {class_name}")
        return NotificationService.create_notification(
            db, user_id, notification_type, message, "class", related_entity_id
        ) 