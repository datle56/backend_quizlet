from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Tuple
from app.models.study_set import StudySet, Term, StudySetVersion
from app.models.user import User
from app.schemas.study_set import StudySetCreate, StudySetUpdate, StudySetSearchParams
from fastapi import HTTPException, status


class StudySetService:
    @staticmethod
    def create_study_set(db: Session, study_set_data: StudySetCreate, user_id: int) -> StudySet:
        """Create a new study set and update user's total_study_sets_created"""
        data = study_set_data.dict()
        study_set = StudySet(
            **data,
            user_id=user_id
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        # Update user's total_study_sets_created
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.total_study_sets_created += 1
            db.commit()
        return study_set

    @staticmethod
    def get_study_set_by_id(db: Session, study_set_id: int, increment_views: bool = True) -> Optional[StudySet]:
        """Get study set by ID and optionally increment views count"""
        study_set = db.query(StudySet).filter(
            StudySet.id == study_set_id).first()

        if not study_set:
            return None

        if increment_views:
            study_set.views_count += 1
            db.commit()
            db.refresh(study_set)

        return study_set

    @staticmethod
    def get_public_study_set_by_id(db: Session, study_set_id: int, increment_views: bool = True) -> Optional[StudySet]:
        """Get public study set by ID (no authentication required)"""
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.is_public == True)
        ).first()

        if not study_set:
            return None

        if increment_views:
            study_set.views_count += 1
            db.commit()
            db.refresh(study_set)

        return study_set

    @staticmethod
    def update_study_set(db: Session, study_set_id: int, study_set_data: StudySetUpdate, user_id: int) -> StudySet:
        """Update study set and create version history"""
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to edit it"
            )

        # Create version history before updating
        current_version = db.query(StudySetVersion).filter(
            StudySetVersion.study_set_id == study_set_id
        ).order_by(desc(StudySetVersion.version_number)).first()

        version_number = (current_version.version_number +
                          1) if current_version else 1

        version = StudySetVersion(
            study_set_id=study_set_id,
            version_number=version_number,
            title=study_set.title,
            description=study_set.description,
            user_id=user_id,
            changes_summary="Updated study set"
        )
        db.add(version)

        # Update study set
        update_data = study_set_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(study_set, field, value)
        db.commit()
        db.refresh(study_set)
        return study_set

    @staticmethod
    def toggle_study_set_public(db: Session, study_set_id: int, user_id: int, is_public: bool) -> Optional[StudySet]:
        """Toggle study set public/private status"""
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            return None

        study_set.is_public = is_public
        db.commit()
        db.refresh(study_set)
        return study_set

    @staticmethod
    def delete_study_set(db: Session, study_set_id: int, user_id: int) -> bool:
        """Delete study set (soft delete by setting is_public to False)"""
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to delete it"
            )

        # Soft delete by setting is_public to False
        study_set.is_public = False
        db.commit()

        # Update user's total_study_sets_created
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.total_study_sets_created > 0:
            user.total_study_sets_created -= 1
            db.commit()

        return True

    @staticmethod
    def search_study_sets(db: Session, params: StudySetSearchParams) -> Tuple[List[StudySet], int]:
        """Search and filter study sets with pagination (includes private for authenticated users)"""
        query = db.query(StudySet).filter(StudySet.is_public == True)

        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    StudySet.title.ilike(search_term),
                    StudySet.description.ilike(search_term)
                )
            )

        # Apply language filters
        if params.language_from:
            query = query.filter(StudySet.language_from ==
                                 params.language_from)
        if params.language_to:
            query = query.filter(StudySet.language_to == params.language_to)

        # Apply user filter
        if params.user_id:
            query = query.filter(StudySet.user_id == params.user_id)

        # Apply rating filter
        if params.min_rating is not None:
            query = query.filter(StudySet.average_rating >= params.min_rating)

        # Apply sorting
        sort_column = getattr(StudySet, params.sort_by)
        if params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (params.page - 1) * params.size
        study_sets = query.offset(offset).limit(params.size).all()

        return study_sets, total

    @staticmethod
    def search_public_study_sets(db: Session, params: StudySetSearchParams) -> Tuple[List[StudySet], int]:
        """Search and filter public study sets with pagination (public access only)"""
        query = db.query(StudySet).filter(StudySet.is_public == True)

        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    StudySet.title.ilike(search_term),
                    StudySet.description.ilike(search_term)
                )
            )

        # Apply language filters
        if params.language_from:
            query = query.filter(StudySet.language_from ==
                                 params.language_from)
        if params.language_to:
            query = query.filter(StudySet.language_to == params.language_to)

        # Apply user filter
        if params.user_id:
            query = query.filter(StudySet.user_id == params.user_id)

        # Apply rating filter
        if params.min_rating is not None:
            query = query.filter(StudySet.average_rating >= params.min_rating)

        # Apply sorting
        sort_column = getattr(StudySet, params.sort_by)
        if params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (params.page - 1) * params.size
        study_sets = query.offset(offset).limit(params.size).all()

        return study_sets, total

    @staticmethod
    def get_user_study_sets(db: Session, user_id: int, include_private: bool = True) -> List[StudySet]:
        """Get all study sets for a specific user"""
        query = db.query(StudySet).filter(StudySet.user_id == user_id)

        if not include_private:
            query = query.filter(StudySet.is_public == True)

        return query.order_by(desc(StudySet.created_at)).all()


class TermService:
    @staticmethod
    def create_term(db: Session, study_set_id: int, term_data: dict, user_id: int) -> Term:
        """Create a new term and update study set's terms_count"""
        # Verify study set exists and user has permission
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to add terms"
            )

        # Get the next position
        max_position = db.query(func.max(Term.position)).filter(
            Term.study_set_id == study_set_id
        ).scalar() or 0

        term = Term(
            **term_data,
            study_set_id=study_set_id,
            position=max_position + 1
        )
        db.add(term)

        # Update study set's terms_count
        study_set.terms_count += 1

        db.commit()
        db.refresh(term)
        return term

    @staticmethod
    def get_terms_by_study_set(db: Session, study_set_id: int) -> List[Term]:
        """Get all terms for a study set, ordered by position"""
        return db.query(Term).filter(
            Term.study_set_id == study_set_id
        ).order_by(Term.position).all()

    @staticmethod
    def update_term(db: Session, study_set_id: int, term_id: int, term_data: dict, user_id: int) -> Term:
        """Update a term"""
        # Verify study set exists and user has permission
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to edit terms"
            )

        term = db.query(Term).filter(
            and_(Term.id == term_id, Term.study_set_id == study_set_id)
        ).first()

        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        # Update term
        for field, value in term_data.items():
            if value is not None:
                setattr(term, field, value)

        db.commit()
        db.refresh(term)
        return term

    @staticmethod
    def delete_term(db: Session, study_set_id: int, term_id: int, user_id: int) -> bool:
        """Delete a term and update study set's terms_count"""
        # Verify study set exists and user has permission
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to delete terms"
            )

        term = db.query(Term).filter(
            and_(Term.id == term_id, Term.study_set_id == study_set_id)
        ).first()

        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Term not found"
            )

        # Update study set's terms_count
        if study_set.terms_count > 0:
            study_set.terms_count -= 1

        db.delete(term)
        db.commit()
        return True

    @staticmethod
    def bulk_create_terms(db: Session, study_set_id: int, terms_data: List[dict], user_id: int) -> List[Term]:
        """Create multiple terms at once"""
        # Verify study set exists and user has permission
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to add terms"
            )

        # Get the next position
        max_position = db.query(func.max(Term.position)).filter(
            Term.study_set_id == study_set_id
        ).scalar() or 0

        terms = []
        for i, term_data in enumerate(terms_data):
            term = Term(
                **term_data,
                study_set_id=study_set_id,
                position=max_position + i + 1
            )
            terms.append(term)
            db.add(term)

        # Update study set's terms_count
        study_set.terms_count += len(terms)

        db.commit()

        # Refresh all terms to get their IDs
        for term in terms:
            db.refresh(term)

        return terms

    @staticmethod
    def reorder_terms(db: Session, study_set_id: int, term_ids: List[int], user_id: int) -> List[Term]:
        """Reorder terms by updating their positions"""
        # Verify study set exists and user has permission
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()

        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found or you don't have permission to reorder terms"
            )

        # Verify all terms belong to this study set
        terms = db.query(Term).filter(
            and_(Term.id.in_(term_ids), Term.study_set_id == study_set_id)
        ).all()

        if len(terms) != len(term_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some terms do not belong to this study set"
            )

        # Update positions
        for i, term_id in enumerate(term_ids):
            term = next(t for t in terms if t.id == term_id)
            term.position = i + 1

        db.commit()

        # Return terms in new order
        return db.query(Term).filter(
            Term.study_set_id == study_set_id
        ).order_by(Term.position).all()
