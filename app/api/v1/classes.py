from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.class_ import Class, ClassMember, ClassStudySet
from app.schemas.class_ import (
    ClassCreate, ClassUpdate, ClassResponse, ClassDetailResponse,
    ClassJoin, ClassMemberResponse, ClassStudySetCreate, ClassStudySetResponse,
    ClassProgressResponse
)
from app.services.class_service import ClassService, ClassStudySetService, ClassProgressService
from sqlalchemy import and_
from app.models.study_set import StudySet

router = APIRouter()


def _get_user_info(user: User) -> dict:
    """Convert user to dict for response"""
    return {
        "id": user.id,
        "last_name": user.last_name,
        "first_name": user.first_name,
        "avatar_url": user.avatar_url
    }


def _to_class_dict(class_: Class) -> dict:
    """Convert SQLAlchemy class to dict with only required fields"""
    return {
        "id": class_.id,
        "name": class_.name,
        "description": class_.description,
        "subject": class_.subject,  # Thêm trường subject
        "school": class_.school,    # Thêm trường school
        "teacher_id": class_.teacher_id,
        "join_code": class_.join_code,
        "created_at": class_.created_at,
        "is_active": class_.is_active
    }


def _to_class_member_dict(member: ClassMember) -> dict:
    """Convert SQLAlchemy class member to dict"""
    return {
        "id": member.id,
        "class_id": member.class_id,
        "user_id": member.user_id,
        "role": member.role,
        "joined_at": member.joined_at
    }


def _to_class_study_set_dict(assignment: ClassStudySet) -> dict:
    """Convert SQLAlchemy class study set to dict"""
    return {
        "id": assignment.id,
        "class_id": assignment.class_id,
        "study_set_id": assignment.study_set_id,
        "assigned_at": assignment.assigned_at,
        "due_date": assignment.due_date,
        "is_optional": assignment.is_optional
    }


@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new class (teacher only)"""
    class_ = ClassService.create_class(db, class_data, current_user.id)
    data = _to_class_dict(class_)
    resp = ClassResponse.model_validate(data)
    return resp


@router.get("/", response_model=List[ClassResponse])
def get_user_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all classes where user is a member"""
    classes = ClassService.get_user_classes(db, current_user.id)
    return [ClassResponse.model_validate(_to_class_dict(class_)) for class_ in classes]


@router.post("/join", response_model=ClassResponse)
def join_class(
    join_data: ClassJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a class using join code"""
    class_ = ClassService.join_class(db, join_data.join_code, current_user.id)
    data = _to_class_dict(class_)
    resp = ClassResponse.model_validate(data)
    return resp


@router.get("/{class_id}", response_model=ClassDetailResponse)
def get_class_detail(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed class information including members and assignments"""
    # Check if user is a member of the class
    member = db.query(ClassMember).filter(
        and_(ClassMember.class_id == class_id, ClassMember.user_id == current_user.id)
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this class"
        )

    class_ = ClassService.get_class_by_id(db, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Get teacher info
    teacher = db.query(User).filter(User.id == class_.teacher_id).first()
    teacher_info = _get_user_info(teacher) if teacher else None

    # Get members
    members = ClassService.get_class_members(db, class_id)
    member_responses = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        member_data = _to_class_member_dict(member)
        member_data["user"] = _get_user_info(user) if user else None
        member_responses.append(ClassMemberResponse.model_validate(member_data))

    # Get assignments
    assignments = ClassStudySetService.get_class_assignments(db, class_id)
    assignment_responses = []
    for assignment in assignments:
        study_set = db.query(StudySet).filter(StudySet.id == assignment.study_set_id).first()
        assignment_data = _to_class_study_set_dict(assignment)
        assignment_data["study_set"] = {
            "id": study_set.id,
            "title": study_set.title,
            "description": study_set.description,
            "terms_count": study_set.terms_count
        } if study_set else None
        assignment_responses.append(ClassStudySetResponse.model_validate(assignment_data))

    # Build response
    class_data = _to_class_dict(class_)
    class_data["teacher"] = teacher_info
    class_data["members"] = member_responses
    class_data["study_sets"] = assignment_responses

    return ClassDetailResponse.model_validate(class_data)


@router.get("/{class_id}/members", response_model=List[ClassMemberResponse])
def get_class_members(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all members of a class"""
    # Check if user is a member of the class
    member = db.query(ClassMember).filter(
        and_(ClassMember.class_id == class_id, ClassMember.user_id == current_user.id)
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this class"
        )

    members = ClassService.get_class_members(db, class_id)
    member_responses = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        member_data = _to_class_member_dict(member)
        member_data["user"] = _get_user_info(user) if user else None
        member_responses.append(ClassMemberResponse.model_validate(member_data))

    return member_responses


@router.post("/{class_id}/study-sets", response_model=ClassStudySetResponse, status_code=status.HTTP_201_CREATED)
def assign_study_set(
    class_id: int,
    assignment_data: ClassStudySetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a study set to a class (teacher only)"""
    assignment = ClassStudySetService.assign_study_set(db, class_id, assignment_data, current_user.id)
    data = _to_class_study_set_dict(assignment)
    resp = ClassStudySetResponse.model_validate(data)
    return resp


@router.get("/{class_id}/assignments", response_model=List[ClassStudySetResponse])
def get_class_assignments(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all study sets assigned to a class"""
    # Check if user is a member of the class
    member = db.query(ClassMember).filter(
        and_(ClassMember.class_id == class_id, ClassMember.user_id == current_user.id)
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this class"
        )

    assignments = ClassStudySetService.get_class_assignments(db, class_id)
    assignment_responses = []
    for assignment in assignments:
        study_set = db.query(StudySet).filter(StudySet.id == assignment.study_set_id).first()
        assignment_data = _to_class_study_set_dict(assignment)
        assignment_data["study_set"] = {
            "id": study_set.id,
            "title": study_set.title,
            "description": study_set.description,
            "terms_count": study_set.terms_count
        } if study_set else None
        assignment_responses.append(ClassStudySetResponse.model_validate(assignment_data))

    return assignment_responses


@router.delete("/{class_id}/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_assignment(
    class_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a study set assignment (teacher only)"""
    ClassStudySetService.remove_assignment(db, class_id, assignment_id, current_user.id)


@router.get("/{class_id}/progress", response_model=List[ClassProgressResponse])
def get_class_progress(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress of all students in a class (teacher only)"""
    progress_data = ClassProgressService.get_class_progress(db, class_id, current_user.id)
    return [ClassProgressResponse.model_validate(data) for data in progress_data]


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update class (teacher only)"""
    class_ = ClassService.update_class(db, class_id, class_data, current_user.id)
    data = _to_class_dict(class_)
    resp = ClassResponse.model_validate(data)
    return resp


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete class (teacher only)"""
    ClassService.delete_class(db, class_id, current_user.id) 