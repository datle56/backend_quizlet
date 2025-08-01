from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Tuple
from app.models.class_ import Class, ClassMember, ClassStudySet
from app.models.user import User
from app.models.study_set import StudySet
from app.models.study_progress import StudySession
from app.schemas.class_ import ClassCreate, ClassUpdate, ClassJoin, ClassStudySetCreate
from fastapi import HTTPException, status
import secrets
import string


class ClassService:
    @staticmethod
    def generate_join_code() -> str:
        """Generate a unique 6-character join code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(6))

    @staticmethod
    def create_class(db: Session, class_data: ClassCreate, teacher_id: int) -> Class:
        """Create a new class"""
        # Generate unique join code
        join_code = ClassService.generate_join_code()
        while db.query(Class).filter(Class.join_code == join_code).first():
            join_code = ClassService.generate_join_code()

        class_ = Class(
            **class_data.dict(),
            teacher_id=teacher_id,
            join_code=join_code
        )
        db.add(class_)
        db.commit()
        db.refresh(class_)

        # Add teacher as first member
        teacher_member = ClassMember(
            class_id=class_.id,
            user_id=teacher_id,
            role="teacher"
        )
        db.add(teacher_member)
        db.commit()

        return class_

    @staticmethod
    def get_class_by_id(db: Session, class_id: int) -> Optional[Class]:
        """Get class by ID"""
        return db.query(Class).filter(Class.id == class_id).first()

    @staticmethod
    def get_user_classes(db: Session, user_id: int) -> List[Class]:
        """Get all classes where user is a member"""
        return db.query(Class).join(ClassMember).filter(
            ClassMember.user_id == user_id
        ).all()

    @staticmethod
    def join_class(db: Session, join_code: str, user_id: int) -> Class:
        """Join a class using join code"""
        class_ = db.query(Class).filter(Class.join_code == join_code).first()
        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

        if not class_.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class is not active"
            )

        # Check if user is already a member
        existing_member = db.query(ClassMember).filter(
            and_(ClassMember.class_id == class_.id, ClassMember.user_id == user_id)
        ).first()

        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this class"
            )

        # Add user as member
        member = ClassMember(
            class_id=class_.id,
            user_id=user_id,
            role="student"
        )
        db.add(member)
        db.commit()

        return class_

    @staticmethod
    def get_class_members(db: Session, class_id: int) -> List[ClassMember]:
        """Get all members of a class"""
        return db.query(ClassMember).filter(ClassMember.class_id == class_id).all()

    @staticmethod
    def update_class(db: Session, class_id: int, class_data: ClassUpdate, user_id: int) -> Class:
        """Update class (only teacher can update)"""
        class_ = db.query(Class).filter(
            and_(Class.id == class_id, Class.teacher_id == user_id)
        ).first()

        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission to edit it"
            )

        update_data = class_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(class_, field, value)

        db.commit()
        db.refresh(class_)
        return class_

    @staticmethod
    def delete_class(db: Session, class_id: int, user_id: int) -> bool:
        """Delete class (only teacher can delete)"""
        class_ = db.query(Class).filter(
            and_(Class.id == class_id, Class.teacher_id == user_id)
        ).first()

        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission to delete it"
            )

        # Soft delete by setting is_active to False
        class_.is_active = False
        db.commit()
        return True


class ClassStudySetService:
    @staticmethod
    def assign_study_set(db: Session, class_id: int, study_set_data: ClassStudySetCreate, user_id: int) -> ClassStudySet:
        """Assign a study set to a class (only teacher can assign)"""
        # Check if user is teacher of the class
        class_ = db.query(Class).filter(
            and_(Class.id == class_id, Class.teacher_id == user_id)
        ).first()

        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission to assign study sets"
            )

        # Check if study set exists
        study_set = db.query(StudySet).filter(StudySet.id == study_set_data.study_set_id).first()
        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found"
            )

        # Check if study set is already assigned
        existing_assignment = db.query(ClassStudySet).filter(
            and_(ClassStudySet.class_id == class_id, ClassStudySet.study_set_id == study_set_data.study_set_id)
        ).first()

        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Study set is already assigned to this class"
            )

        assignment = ClassStudySet(
            class_id=class_id,
            **study_set_data.dict()
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_class_assignments(db: Session, class_id: int) -> List[ClassStudySet]:
        """Get all study sets assigned to a class"""
        return db.query(ClassStudySet).filter(ClassStudySet.class_id == class_id).all()

    @staticmethod
    def remove_assignment(db: Session, class_id: int, assignment_id: int, user_id: int) -> bool:
        """Remove a study set assignment (only teacher can remove)"""
        # Check if user is teacher of the class
        class_ = db.query(Class).filter(
            and_(Class.id == class_id, Class.teacher_id == user_id)
        ).first()

        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission to remove assignments"
            )

        assignment = db.query(ClassStudySet).filter(
            and_(ClassStudySet.id == assignment_id, ClassStudySet.class_id == class_id)
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        db.delete(assignment)
        db.commit()
        return True


class ClassProgressService:
    @staticmethod
    def get_class_progress(db: Session, class_id: int, user_id: int) -> List[dict]:
        """Get progress of all students in a class"""
        # Check if user is teacher of the class
        class_ = db.query(Class).filter(
            and_(Class.id == class_id, Class.teacher_id == user_id)
        ).first()

        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission to view progress"
            )

        # Get all students in the class
        students = db.query(ClassMember).filter(
            and_(ClassMember.class_id == class_id, ClassMember.role == "student")
        ).all()

        progress_data = []
        for student_member in students:
            student = db.query(User).filter(User.id == student_member.user_id).first()
            if not student:
                continue

            # Get assigned study sets
            assignments = db.query(ClassStudySet).filter(ClassStudySet.class_id == class_id).all()
            total_assignments = len(assignments)
            completed_assignments = 0
            total_score = 0
            score_count = 0

            for assignment in assignments:
                # Check if student has studied this study set
                study_sessions = db.query(StudySession).filter(
                    and_(
                        StudySession.user_id == student.id,
                        StudySession.study_set_id == assignment.study_set_id
                    )
                ).all()

                if study_sessions:
                    completed_assignments += 1
                    # Calculate average score for this study set
                    for session in study_sessions:
                        if session.score is not None:
                            total_score += session.score
                            score_count += 1

            average_score = total_score / score_count if score_count > 0 else None

            # Get last activity
            last_session = db.query(StudySession).filter(
                StudySession.user_id == student.id
            ).order_by(desc(StudySession.completed_at)).first()

            progress_data.append({
                "user_id": student.id,
                "username": student.username,
                "full_name": student.full_name,
                "total_assignments": total_assignments,
                "completed_assignments": completed_assignments,
                "average_score": average_score,
                "last_activity": last_session.completed_at if last_session else None
            })

        return progress_data 