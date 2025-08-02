from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models.user import User
from app.models.study_set import StudySet
from app.models.class_ import Class, ClassMember
from app.models.study_progress import StudyProgress, StudySession
from app.models.social import Favorite, Rating
from app.schemas.analytics import UserStats, StudySetStats, ClassStats, StudySessionStats


class AnalyticsService:
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> UserStats:
        """Get comprehensive statistics for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Study sets created
        total_study_sets_created = db.query(StudySet).filter(
            StudySet.user_id == user_id
        ).count()
        
        # Terms learned (from study progress)
        total_terms_learned = db.query(StudyProgress).filter(
            StudyProgress.user_id == user_id,
            StudyProgress.familiarity_level.in_(["familiar", "mastered"])
        ).count()
        
        # Study sessions
        sessions = db.query(StudySession).filter(StudySession.user_id == user_id)
        total_study_sessions = sessions.count()
        
        # Total time studied
        total_time_studied_minutes = db.query(
            func.sum(StudySession.time_spent_seconds)
        ).filter(StudySession.user_id == user_id).scalar() or 0
        total_time_studied_minutes = total_time_studied_minutes // 60
        
        # Average score
        avg_score = db.query(
            func.avg(StudySession.score)
        ).filter(
            StudySession.user_id == user_id,
            StudySession.score.isnot(None)
        ).scalar() or 0.0
        
        # Study streak (consecutive days with study sessions)
        study_streak_days = AnalyticsService._calculate_study_streak(db, user_id)
        
        # Favorite study sets
        favorite_study_sets_count = db.query(Favorite).filter(
            Favorite.user_id == user_id
        ).count()
        
        # Classes joined
        classes_joined_count = db.query(Class).join(
            Class.members
        ).filter(
            ClassMember.user_id == user_id
        ).count()
        
        return UserStats(
            total_study_sets_created=total_study_sets_created,
            total_terms_learned=total_terms_learned,
            total_study_sessions=total_study_sessions,
            total_time_studied_minutes=total_time_studied_minutes,
            average_score=float(avg_score),
            study_streak_days=study_streak_days,
            favorite_study_sets_count=favorite_study_sets_count,
            classes_joined_count=classes_joined_count,
            last_active_at=user.last_active_at
        )
    
    @staticmethod
    def get_study_set_stats(db: Session, study_set_id: int) -> StudySetStats:
        """Get comprehensive statistics for a study set"""
        study_set = db.query(StudySet).filter(StudySet.id == study_set_id).first()
        if not study_set:
            return None
        
        # Views, favorites, ratings
        total_views = study_set.views_count or 0
        total_favorites = db.query(Favorite).filter(
            Favorite.study_set_id == study_set_id
        ).count()
        total_ratings = db.query(Rating).filter(
            Rating.study_set_id == study_set_id
        ).count()
        
        # Average rating
        avg_rating = db.query(
            func.avg(Rating.rating)
        ).filter(Rating.study_set_id == study_set_id).scalar() or 0.0
        
        # Study sessions
        sessions = db.query(StudySession).filter(StudySession.study_set_id == study_set_id)
        total_study_sessions = sessions.count()
        
        # Total time studied
        total_time_studied_minutes = db.query(
            func.sum(StudySession.time_spent_seconds)
        ).filter(StudySession.study_set_id == study_set_id).scalar() or 0
        total_time_studied_minutes = total_time_studied_minutes // 60
        
        # Unique students
        unique_students_count = db.query(
            func.count(func.distinct(StudySession.user_id))
        ).filter(StudySession.study_set_id == study_set_id).scalar() or 0
        
        # Completion rate (students who completed at least one session)
        completion_rate = 0.0
        if total_study_sessions > 0:
            completed_sessions = db.query(StudySession).filter(
                and_(
                    StudySession.study_set_id == study_set_id,
                    StudySession.completed_at.isnot(None)
                )
            ).count()
            completion_rate = (completed_sessions / total_study_sessions) * 100
        
        # Difficulty distribution (based on study progress)
        difficulty_stats = db.query(
            StudyProgress.familiarity_level,
            func.count(StudyProgress.id)
        ).filter(StudyProgress.study_set_id == study_set_id).group_by(
            StudyProgress.familiarity_level
        ).all()
        
        difficulty_distribution = {
            stat.familiarity_level: stat.count 
            for stat in difficulty_stats
        }
        
        return StudySetStats(
            total_views=total_views,
            total_favorites=total_favorites,
            total_ratings=total_ratings,
            average_rating=float(avg_rating),
            total_study_sessions=total_study_sessions,
            total_time_studied_minutes=total_time_studied_minutes,
            unique_students_count=unique_students_count,
            completion_rate=completion_rate,
            difficulty_distribution=difficulty_distribution
        )
    
    @staticmethod
    def get_class_stats(db: Session, class_id: int) -> ClassStats:
        """Get comprehensive statistics for a class"""
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            return None
        
        # Total members
        total_members = db.query(func.count(Class.members)).filter(
            Class.id == class_id
        ).scalar() or 0
        
        # Total study sets
        total_study_sets = db.query(StudySet).filter(
            StudySet.user_id == class_obj.teacher_id
        ).count()
        
        # Total study sessions by class members
        member_ids = [member.user_id for member in class_obj.members]
        total_study_sessions = db.query(StudySession).filter(
            StudySession.user_id.in_(member_ids)
        ).count()
        
        # Average student progress
        avg_progress = db.query(
            func.avg(StudyProgress.familiarity_level)
        ).filter(
            StudyProgress.user_id.in_(member_ids)
        ).scalar() or 0.0
        
        # Top students (by study sessions)
        top_students = db.query(
            User.username,
            func.count(StudySession.id).label('session_count')
        ).join(StudySession).filter(
            StudySession.user_id.in_(member_ids)
        ).group_by(User.id, User.username).order_by(
            desc('session_count')
        ).limit(5).all()
        
        top_students_data = [
            {"username": student.username, "session_count": student.session_count}
            for student in top_students
        ]
        
        # Most popular study sets in class
        popular_sets = db.query(
            StudySet.title,
            func.count(StudySession.id).label('session_count')
        ).join(StudySession).filter(
            StudySession.user_id.in_(member_ids)
        ).group_by(StudySet.id, StudySet.title).order_by(
            desc('session_count')
        ).limit(5).all()
        
        popular_sets_data = [
            {"title": study_set.title, "session_count": study_set.session_count}
            for study_set in popular_sets
        ]
        
        # Recent activity
        recent_activity = db.query(StudySession).filter(
            StudySession.user_id.in_(member_ids)
        ).order_by(desc(StudySession.started_at)).limit(10).all()
        
        recent_activity_data = [
            {
                "user_id": session.user_id,
                "study_set_id": session.study_set_id,
                "started_at": session.started_at,
                "score": session.score
            }
            for session in recent_activity
        ]
        
        return ClassStats(
            total_members=total_members,
            total_study_sets=total_study_sets,
            total_study_sessions=total_study_sessions,
            average_student_progress=float(avg_progress),
            top_students=top_students_data,
            most_popular_study_sets=popular_sets_data,
            recent_activity=recent_activity_data
        )
    
    @staticmethod
    def get_study_session_stats(db: Session, user_id: int) -> StudySessionStats:
        """Get study session statistics for a user"""
        sessions = db.query(StudySession).filter(StudySession.user_id == user_id)
        total_sessions = sessions.count()
        
        # Total time
        total_time_minutes = db.query(
            func.sum(StudySession.time_spent_seconds)
        ).filter(StudySession.user_id == user_id).scalar() or 0
        total_time_minutes = total_time_minutes // 60
        
        # Average score
        avg_score = db.query(
            func.avg(StudySession.score)
        ).filter(
            StudySession.user_id == user_id,
            StudySession.score.isnot(None)
        ).scalar() or 0.0
        
        # Sessions by mode
        mode_stats = db.query(
            StudySession.study_mode,
            func.count(StudySession.id)
        ).filter(StudySession.user_id == user_id).group_by(
            StudySession.study_mode
        ).all()
        
        sessions_by_mode = {
            stat.study_mode: stat.count 
            for stat in mode_stats
        }
        
        # Sessions by date (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_sessions = db.query(
            func.date(StudySession.started_at).label('date'),
            func.count(StudySession.id).label('count')
        ).filter(
            and_(
                StudySession.user_id == user_id,
                StudySession.started_at >= thirty_days_ago
            )
        ).group_by(func.date(StudySession.started_at)).all()
        
        sessions_by_date = [
            {"date": session.date, "count": session.count}
            for session in daily_sessions
        ]
        
        # Improvement trend (score over time)
        score_trend = db.query(
            func.date(StudySession.started_at).label('date'),
            func.avg(StudySession.score).label('avg_score')
        ).filter(
            and_(
                StudySession.user_id == user_id,
                StudySession.score.isnot(None),
                StudySession.started_at >= thirty_days_ago
            )
        ).group_by(func.date(StudySession.started_at)).order_by(
            func.date(StudySession.started_at)
        ).all()
        
        improvement_trend = [
            {"date": trend.date, "avg_score": float(trend.avg_score)}
            for trend in score_trend
        ]
        
        return StudySessionStats(
            total_sessions=total_sessions,
            total_time_minutes=total_time_minutes,
            average_score=float(avg_score),
            sessions_by_mode=sessions_by_mode,
            sessions_by_date=sessions_by_date,
            improvement_trend=improvement_trend
        )
    
    @staticmethod
    def _calculate_study_streak(db: Session, user_id: int) -> int:
        """Calculate consecutive days with study sessions"""
        # Get all study session dates for user
        session_dates = db.query(
            func.date(StudySession.started_at)
        ).filter(StudySession.user_id == user_id).distinct().all()
        
        if not session_dates:
            return 0
        
        # Convert to datetime objects and sort
        dates = [datetime.strptime(str(date[0]), '%Y-%m-%d').date() for date in session_dates]
        dates.sort(reverse=True)
        
        # Calculate streak
        streak = 0
        current_date = datetime.utcnow().date()
        
        for i, date in enumerate(dates):
            if i == 0:
                if (current_date - date).days <= 1:
                    streak = 1
                else:
                    break
            else:
                if (dates[i-1] - date).days == 1:
                    streak += 1
                else:
                    break
        
        return streak 