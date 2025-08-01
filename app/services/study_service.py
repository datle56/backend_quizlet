from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.study_progress import StudyProgress, StudySession, FamiliarityLevelEnum, StudyModeEnum
from app.models.study_set import Term
from app.models.user import User

class StudyService:
    @staticmethod
    def get_study_progress(db: Session, user_id: int, study_set_id: int):
        return db.query(StudyProgress).filter_by(user_id=user_id, study_set_id=study_set_id).all()

    @staticmethod
    def update_term_progress(db: Session, user_id: int, study_set_id: int, term_id: int, correct: bool, response_time: float = None, difficulty: int = None):
        progress = db.query(StudyProgress).filter_by(user_id=user_id, study_set_id=study_set_id, term_id=term_id).first()
        now = datetime.utcnow()
        if not progress:
            progress = StudyProgress(user_id=user_id, study_set_id=study_set_id, term_id=term_id, last_studied=now, correct_count=0, incorrect_count=0, current_streak=0, longest_streak=0)
            db.add(progress)
        progress.last_studied = now
        if correct:
            progress.correct_count += 1
            progress.current_streak += 1
            progress.longest_streak = max(progress.longest_streak, progress.current_streak)
            # SRS: next_review = now + longer interval
            progress.familiarity_level = StudyService._next_familiarity(progress.familiarity_level, up=True)
            progress.next_review = now + timedelta(days=StudyService._srs_interval(progress.familiarity_level))
        else:
            progress.incorrect_count += 1
            progress.current_streak = 0
            progress.familiarity_level = StudyService._next_familiarity(progress.familiarity_level, up=False)
            progress.next_review = now + timedelta(days=1)
        db.commit()
        return progress

    @staticmethod
    def get_review_terms(db: Session, user_id: int, study_set_id: int):
        # Return terms that are due for review (SRS)
        now = datetime.utcnow()
        progresses = db.query(StudyProgress).filter_by(user_id=user_id, study_set_id=study_set_id).all()
        due_terms = [p for p in progresses if not p.next_review or p.next_review <= now]
        return due_terms

    @staticmethod
    def start_study_session(db: Session, user_id: int, study_set_id: int, study_mode: StudyModeEnum):
        now = datetime.utcnow()
        session = StudySession(user_id=user_id, study_set_id=study_set_id, study_mode=study_mode, started_at=now)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def update_study_session(db: Session, session_id: int, **kwargs):
        session = db.query(StudySession).filter_by(id=session_id).first()
        if not session:
            return None
        for key, value in kwargs.items():
            setattr(session, key, value)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def _next_familiarity(current, up=True):
        # Simple logic: learning -> familiar -> mastered, or reverse
        if up:
            if current == FamiliarityLevelEnum.learning:
                return FamiliarityLevelEnum.familiar
            elif current == FamiliarityLevelEnum.familiar:
                return FamiliarityLevelEnum.mastered
            else:
                return FamiliarityLevelEnum.mastered
        else:
            if current == FamiliarityLevelEnum.mastered:
                return FamiliarityLevelEnum.familiar
            elif current == FamiliarityLevelEnum.familiar:
                return FamiliarityLevelEnum.learning
            else:
                return FamiliarityLevelEnum.learning

    @staticmethod
    def _srs_interval(familiarity):
        # Example: learning=1d, familiar=3d, mastered=7d
        if familiarity == FamiliarityLevelEnum.mastered:
            return 7
        elif familiarity == FamiliarityLevelEnum.familiar:
            return 3
        else:
            return 1