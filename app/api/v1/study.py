from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.study_progress import (
    StudyProgressResponse, TermProgressUpdate, ReviewTermList, StudySessionCreate, StudySessionResponse, StudySessionUpdate
)
from app.services.study_service import StudyService

router = APIRouter()

@router.get('/progress/{study_set_id}', response_model=List[StudyProgressResponse])
def get_study_progress(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progresses = StudyService.get_study_progress(db, current_user.id, study_set_id)
    return progresses

@router.post('/progress/{study_set_id}/terms/{term_id}', response_model=StudyProgressResponse)
def update_term_progress(study_set_id: int, term_id: int, update: TermProgressUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progress = StudyService.update_term_progress(db, current_user.id, study_set_id, term_id, update.correct, update.response_time, update.difficulty)
    return progress

@router.get('/review/{study_set_id}', response_model=ReviewTermList)
def get_review_terms(study_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    due_terms = StudyService.get_review_terms(db, current_user.id, study_set_id)
    # Map to ReviewTermList schema
    terms = []
    for p in due_terms:
        terms.append({
            'term_id': p.term_id,
            'term': '',  # You may want to join with Term model for term/definition
            'definition': '',
            'familiarity_level': p.familiarity_level,
            'next_review': p.next_review
        })
    return {'study_set_id': study_set_id, 'terms': terms}

@router.post('/session', response_model=StudySessionResponse)
def start_study_session(session: StudySessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = StudyService.start_study_session(db, current_user.id, session.study_set_id, session.study_mode)
    return s

@router.put('/session/{id}', response_model=StudySessionResponse)
def update_study_session(id: int, update: StudySessionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = StudyService.update_study_session(db, id, **update.dict(exclude_unset=True))
    if not s:
        raise HTTPException(status_code=404, detail='Session not found')
    return s