import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.study_progress import StudyProgress


class BackgroundService:
    
    @staticmethod
    async def send_study_reminders():
        """Send study reminders to users who haven't studied recently"""
        db = SessionLocal()
        try:
            # Find users who haven't studied in the last 3 days
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            
            # Get users with study progress but no recent activity
            users_to_remind = db.query(User).join(StudyProgress).filter(
                User.last_active_at < three_days_ago
            ).distinct().all()
            
            for user in users_to_remind:
                # Create notification
                NotificationService.create_notification(
                    db, user.id, "study_reminder", 
                    "It's been a while since you studied. Keep up the good work!",
                    "user", user.id
                )
                
                # Send email notification
                await NotificationService.send_email_notification(
                    user.email,
                    "Study Reminder",
                    f"Hello {user.username}, it's been a while since you studied. Don't forget to review your study sets!"
                )
                
                # Send push notification
                await NotificationService.send_push_notification(
                    user.id,
                    "Study Reminder",
                    "Time to study! Don't forget to review your study sets."
                )
                
        finally:
            db.close()
    
    @staticmethod
    async def send_daily_progress_summary():
        """Send daily progress summary to users"""
        db = SessionLocal()
        try:
            # Get all active users
            active_users = db.query(User).filter(
                User.last_active_at >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            for user in active_users:
                # Get user's study stats for today
                today = datetime.utcnow().date()
                today_sessions = db.query(StudySession).filter(
                    StudySession.user_id == user.id,
                    func.date(StudySession.started_at) == today
                ).all()
                
                if today_sessions:
                    total_time = sum(session.time_spent_seconds or 0 for session in today_sessions)
                    avg_score = sum(session.score or 0 for session in today_sessions) / len(today_sessions)
                    
                    message = f"Today's study summary: {len(today_sessions)} sessions, {total_time//60} minutes, {avg_score:.1f}% average score"
                    
                    # Create notification
                    NotificationService.create_notification(
                        db, user.id, "daily_summary", message, "user", user.id
                    )
                    
                    # Send email
                    await NotificationService.send_email_notification(
                        user.email,
                        "Daily Study Summary",
                        f"Hello {user.username},\n\n{message}\n\nKeep up the great work!"
                    )
                    
        finally:
            db.close()
    
    @staticmethod
    async def cleanup_old_notifications():
        """Clean up old read notifications"""
        db = SessionLocal()
        try:
            deleted_count = NotificationService.delete_old_notifications(db, days_old=30)
            print(f"Cleaned up {deleted_count} old notifications")
        finally:
            db.close()
    
    @staticmethod
    async def send_class_announcements():
        """Send class announcements to students"""
        db = SessionLocal()
        try:
            # This would be triggered when a teacher posts an announcement
            # For now, just a placeholder
            pass
        finally:
            db.close()
    
    @staticmethod
    async def process_report_notifications():
        """Send notifications for new reports (admin notifications)"""
        db = SessionLocal()
        try:
            # Get new reports that need admin attention
            new_reports = db.query(Report).filter(
                Report.status == "pending"
            ).all()
            
            if new_reports:
                # Send notification to admins
                admin_users = db.query(User).filter(User.is_admin == True).all()
                
                for admin in admin_users:
                    NotificationService.create_notification(
                        db, admin.id, "new_reports", 
                        f"There are {len(new_reports)} new reports that need attention",
                        "admin", admin.id
                    )
                    
        finally:
            db.close()
    
    @staticmethod
    async def send_achievement_notifications():
        """Send notifications for user achievements"""
        db = SessionLocal()
        try:
            # Check for users who have reached milestones
            # Example: 100 terms learned, 10 study sets created, etc.
            
            # Users with 100+ terms learned
            users_100_terms = db.query(User).join(StudyProgress).group_by(User.id).having(
                func.count(StudyProgress.id) >= 100
            ).all()
            
            for user in users_100_terms:
                # Check if we already sent this achievement notification
                existing_notification = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.type == "achievement_100_terms"
                ).first()
                
                if not existing_notification:
                    NotificationService.create_notification(
                        db, user.id, "achievement_100_terms",
                        "Congratulations! You've learned 100 terms!",
                        "achievement", user.id
                    )
                    
                    await NotificationService.send_email_notification(
                        user.email,
                        "Achievement Unlocked!",
                        f"Congratulations {user.username}! You've learned 100 terms. Keep up the great work!"
                    )
                    
        finally:
            db.close()


# Import necessary modules for the background service
from app.models.study_progress import StudySession
from app.models.report import Report
from app.models.notification import Notification
from sqlalchemy import func 