from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.folder import Folder, FolderStudySet
from app.models.study_set import StudySet
from app.schemas.folder import FolderCreate, FolderUpdate
from fastapi import HTTPException, status


class FolderService:
    @staticmethod
    def create_folder(db: Session, folder_data: FolderCreate, user_id: int) -> Folder:
        """Create a new folder for user"""
        folder = Folder(
            name=folder_data.name,
            user_id=user_id
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder

    @staticmethod
    def get_user_folders(db: Session, user_id: int) -> list[Folder]:
        """Get all folders for a user"""
        folders = db.query(Folder).filter(Folder.user_id == user_id).all()
        return folders

    @staticmethod
    def get_folder_by_id(db: Session, folder_id: int, user_id: int) -> Folder:
        """Get folder by ID, ensuring user owns it"""
        folder = db.query(Folder).filter(
            and_(Folder.id == folder_id, Folder.user_id == user_id)
        ).first()
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        return folder

    @staticmethod
    def update_folder(db: Session, folder_id: int, folder_data: FolderUpdate, user_id: int) -> Folder:
        """Update folder"""
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        
        update_data = folder_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(folder, field, value)
        
        db.commit()
        db.refresh(folder)
        return folder

    @staticmethod
    def delete_folder(db: Session, folder_id: int, user_id: int) -> bool:
        """Delete folder and all its study set associations"""
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        
        # Delete all study set associations first
        db.query(FolderStudySet).filter(FolderStudySet.folder_id == folder_id).delete()
        
        # Delete the folder
        db.delete(folder)
        db.commit()
        return True

    @staticmethod
    def add_study_set_to_folder(db: Session, folder_id: int, study_set_id: int, user_id: int) -> FolderStudySet:
        """Add study set to folder"""
        # Verify folder belongs to user
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        
        # Verify study set exists and belongs to user
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()
        if not study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found"
            )
        
        # Check if already exists
        existing = db.query(FolderStudySet).filter(
            and_(FolderStudySet.folder_id == folder_id, FolderStudySet.study_set_id == study_set_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Study set already in folder"
            )
        
        folder_study_set = FolderStudySet(
            folder_id=folder_id,
            study_set_id=study_set_id
        )
        db.add(folder_study_set)
        db.commit()
        db.refresh(folder_study_set)
        return folder_study_set

    @staticmethod
    def remove_study_set_from_folder(db: Session, folder_id: int, study_set_id: int, user_id: int) -> bool:
        """Remove study set from folder"""
        # Verify folder belongs to user
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        
        # Find and delete the association
        folder_study_set = db.query(FolderStudySet).filter(
            and_(FolderStudySet.folder_id == folder_id, FolderStudySet.study_set_id == study_set_id)
        ).first()
        
        if not folder_study_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study set not found in folder"
            )
        
        db.delete(folder_study_set)
        db.commit()
        return True

    @staticmethod
    def get_folder_with_study_sets(db: Session, folder_id: int, user_id: int) -> dict:
        """Get folder with its study sets"""
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        
        # Get study sets in this folder
        study_sets = db.query(StudySet).join(FolderStudySet).filter(
            FolderStudySet.folder_id == folder_id
        ).all()
        
        return {
            "folder": folder,
            "study_sets": study_sets
        } 