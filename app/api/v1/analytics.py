from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    UserStats, StudySetStats, ClassStats, StudySessionStats, AnalyticsResponse
)
from app.services.analytics_service import AnalyticsService
from app.models.study_progress import StudySession, StudyProgress
from app.models.social import Favorite
from app.models.notification import Notification
from sqlalchemy import desc

router = APIRouter()


@router.get("/user-stats", response_model=UserStats)
def get_user_stats(
    user_id: Optional[int] = Query(None, description="User ID (defaults to current user)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive statistics for a user"""
    target_user_id = user_id or current_user.id
    
    # Users can only view their own stats unless they're admin
    # TODO: Add admin role check
    # if target_user_id != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Access denied")
    
    stats = AnalyticsService.get_user_stats(db, target_user_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return stats


@router.get("/study-set-stats/{study_set_id}", response_model=StudySetStats)
def get_study_set_stats(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive statistics for a study set"""
    stats = AnalyticsService.get_study_set_stats(db, study_set_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study set not found"
        )
    
    return stats


@router.get("/class-stats/{class_id}", response_model=ClassStats)
def get_class_stats(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive statistics for a class"""
    # TODO: Add class membership check
    # Check if user is a member of the class or is admin
    
    stats = AnalyticsService.get_class_stats(db, class_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    return stats


@router.get("/study-session-stats", response_model=StudySessionStats)
def get_study_session_stats(
    user_id: Optional[int] = Query(None, description="User ID (defaults to current user)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get study session statistics for a user"""
    target_user_id = user_id or current_user.id
    
    # Users can only view their own stats unless they're admin
    # TODO: Add admin role check
    # if target_user_id != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Access denied")
    
    stats = AnalyticsService.get_study_session_stats(db, target_user_id)
    return stats


@router.get("/comprehensive", response_model=AnalyticsResponse)
def get_comprehensive_analytics(
    user_id: Optional[int] = Query(None, description="User ID for user stats"),
    study_set_id: Optional[int] = Query(None, description="Study set ID for study set stats"),
    class_id: Optional[int] = Query(None, description="Class ID for class stats"),
    include_session_stats: bool = Query(True, description="Include study session stats"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics combining multiple statistics"""
    response = AnalyticsResponse()
    
    # Get user stats
    if user_id:
        response.user_stats = AnalyticsService.get_user_stats(db, user_id)
    elif not study_set_id and not class_id:
        # Default to current user if no specific IDs provided
        response.user_stats = AnalyticsService.get_user_stats(db, current_user.id)
    
    # Get study set stats
    if study_set_id:
        response.study_set_stats = AnalyticsService.get_study_set_stats(db, study_set_id)
    
    # Get class stats
    if class_id:
        response.class_stats = AnalyticsService.get_class_stats(db, class_id)
    
    # Get study session stats
    if include_session_stats:
        target_user_id = user_id or current_user.id
        response.study_session_stats = AnalyticsService.get_study_session_stats(db, target_user_id)
    
    return response


@router.get("/dashboard", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics for the current user"""
    # Get user stats
    user_stats = AnalyticsService.get_user_stats(db, current_user.id)
    
    # Get recent study sessions
    recent_sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).order_by(desc(StudySession.started_at)).limit(5).all()
    
    # Get favorite study sets count
    favorite_count = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).count()
    
    # Get unread notifications count
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # Get study streak
    study_streak = AnalyticsService._calculate_study_streak(db, current_user.id)
    
    return {
        "user_stats": user_stats,
        "recent_sessions": [
            {
                "id": session.id,
                "study_set_id": session.study_set_id,
                "study_mode": session.study_mode,
                "score": session.score,
                "started_at": session.started_at
            }
            for session in recent_sessions
        ],
        "favorite_study_sets_count": favorite_count,
        "unread_notifications_count": unread_notifications,
        "study_streak_days": study_streak
    }


@router.get("/progress/{study_set_id}", response_model=dict)
def get_study_progress(
    study_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed progress for a specific study set"""
    # Get study progress for this user and study set
    progress_records = db.query(StudyProgress).filter(
        StudyProgress.user_id == current_user.id,
        StudyProgress.study_set_id == study_set_id
    ).all()
    
    if not progress_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this study set"
        )
    
    # Calculate progress statistics
    total_terms = len(progress_records)
    mastered_terms = len([p for p in progress_records if p.familiarity_level == "mastered"])
    familiar_terms = len([p for p in progress_records if p.familiarity_level == "familiar"])
    learning_terms = len([p for p in progress_records if p.familiarity_level == "learning"])
    
    # Calculate accuracy
    total_correct = sum(p.correct_count for p in progress_records)
    total_incorrect = sum(p.incorrect_count for p in progress_records)
    total_attempts = total_correct + total_incorrect
    accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        "study_set_id": study_set_id,
        "total_terms": total_terms,
        "mastered_terms": mastered_terms,
        "familiar_terms": familiar_terms,
        "learning_terms": learning_terms,
        "mastery_percentage": (mastered_terms / total_terms * 100) if total_terms > 0 else 0,
        "accuracy_percentage": accuracy,
        "total_correct_answers": total_correct,
        "total_incorrect_answers": total_incorrect,
        "progress_details": [
            {
                "term_id": p.term_id,
                "familiarity_level": p.familiarity_level,
                "correct_count": p.correct_count,
                "incorrect_count": p.incorrect_count,
                "current_streak": p.current_streak,
                "longest_streak": p.longest_streak,
                "last_studied": p.last_studied,
                "next_review": p.next_review
            }
            for p in progress_records
        ]
    } 