from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from app.models.folder import Folder, FolderStudySet
from app.models.study_set import StudySet
from app.schemas.folder import FolderCreate, FolderUpdate
from fastapi import HTTPException, status


class FolderService:
    @staticmethod
    def create_folder(db: Session, folder_data: FolderCreate, user_id: int) -> Folder:
        """Tạo thư mục mới"""
        # Lấy position cao nhất hiện tại
        max_position = db.query(func.max(Folder.position)).filter(
            Folder.user_id == user_id
        ).scalar() or 0
        
        folder = Folder(
            **folder_data.model_dump(),
            user_id=user_id,
            position=max_position + 1
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder

    @staticmethod
    def get_folder_by_id(db: Session, folder_id: int, user_id: int) -> Optional[Folder]:
        """Lấy thư mục theo ID và user_id"""
        return db.query(Folder).filter(
            and_(Folder.id == folder_id, Folder.user_id == user_id)
        ).first()

    @staticmethod
    def get_public_folder_by_id(db: Session, folder_id: int) -> Optional[Folder]:
        """Lấy thư mục public theo ID (không cần user_id)"""
        return db.query(Folder).filter(
            and_(Folder.id == folder_id, Folder.is_public == True)
        ).first()

    @staticmethod
    def get_user_folders(db: Session, user_id: int) -> List[Folder]:
        """Lấy tất cả thư mục của user"""
        return db.query(Folder).filter(
            Folder.user_id == user_id
        ).order_by(Folder.position).all()

    @staticmethod
    def get_public_folders(db: Session, limit: int = 50, offset: int = 0) -> List[Folder]:
        """Lấy danh sách thư mục public"""
        return db.query(Folder).filter(
            Folder.is_public == True
        ).order_by(Folder.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_folder(db: Session, folder_id: int, folder_data: FolderUpdate, user_id: int) -> Optional[Folder]:
        """Cập nhật thư mục"""
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        if not folder:
            return None
        
        update_data = folder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(folder, field, value)
        
        db.commit()
        db.refresh(folder)
        return folder

    @staticmethod
    def toggle_folder_public(db: Session, folder_id: int, user_id: int, is_public: bool) -> Optional[Folder]:
        """Chuyển đổi trạng thái public/private của folder"""
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        if not folder:
            return None
        
        folder.is_public = is_public
        db.commit()
        db.refresh(folder)
        return folder

    @staticmethod
    def delete_folder(db: Session, folder_id: int, user_id: int) -> bool:
        """Xóa thư mục"""
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        if not folder:
            return False
        
        db.delete(folder)
        db.commit()
        return True

    @staticmethod
    def reorder_folders(db: Session, folder_ids: List[int], user_id: int) -> bool:
        """Sắp xếp lại thứ tự thư mục"""
        # Kiểm tra tất cả folder_ids thuộc về user
        folders = db.query(Folder).filter(
            and_(Folder.id.in_(folder_ids), Folder.user_id == user_id)
        ).all()
        
        if len(folders) != len(folder_ids):
            return False
        
        # Cập nhật position
        for position, folder_id in enumerate(folder_ids, 1):
            folder = next((f for f in folders if f.id == folder_id), None)
            if folder:
                folder.position = position
        
        db.commit()
        return True

    @staticmethod
    def add_study_set_to_folder(db: Session, folder_id: int, study_set_id: int, user_id: int) -> bool:
        """Thêm study set vào thư mục"""
        # Kiểm tra folder thuộc về user
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        if not folder:
            return False
        
        # Kiểm tra study set tồn tại và thuộc về user
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()
        if not study_set:
            return False
        
        # Kiểm tra đã tồn tại trong folder chưa
        existing = db.query(FolderStudySet).filter(
            and_(FolderStudySet.folder_id == folder_id, FolderStudySet.study_set_id == study_set_id)
        ).first()
        if existing:
            return True  # Đã tồn tại, coi như thành công
        
        folder_study_set = FolderStudySet(
            folder_id=folder_id,
            study_set_id=study_set_id
        )
        db.add(folder_study_set)
        db.commit()
        return True

    @staticmethod
    def remove_study_set_from_folder(db: Session, folder_id: int, study_set_id: int, user_id: int) -> bool:
        """Xóa study set khỏi thư mục"""
        # Kiểm tra folder thuộc về user
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        if not folder:
            return False
        
        folder_study_set = db.query(FolderStudySet).filter(
            and_(FolderStudySet.folder_id == folder_id, FolderStudySet.study_set_id == study_set_id)
        ).first()
        
        if not folder_study_set:
            return False
        
        db.delete(folder_study_set)
        db.commit()
        return True

    @staticmethod
    def get_study_sets_in_folder(db: Session, folder_id: int, user_id: int) -> List[dict]:
        """Lấy danh sách study sets trong thư mục (cho user sở hữu)"""
        # Kiểm tra folder thuộc về user
        folder = FolderService.get_folder_by_id(db, folder_id, user_id)
        if not folder:
            return []
        
        study_sets = db.query(StudySet, FolderStudySet.added_at).join(
            FolderStudySet, StudySet.id == FolderStudySet.study_set_id
        ).filter(
            FolderStudySet.folder_id == folder_id
        ).order_by(FolderStudySet.added_at.desc()).all()
        
        result = []
        for study_set, added_at in study_sets:
            result.append({
                "id": study_set.id,
                "title": study_set.title,
                "description": study_set.description,
                "terms_count": study_set.terms_count,
                "color": getattr(study_set, "color", None),
                "is_public": study_set.is_public,
                "added_at": added_at
            })
        
        return result

    @staticmethod
    def get_public_study_sets_in_folder(db: Session, folder_id: int) -> List[dict]:
        """Lấy danh sách study sets public trong thư mục (cho public access)"""
        # Kiểm tra folder là public
        folder = FolderService.get_public_folder_by_id(db, folder_id)
        if not folder:
            return []
        
        study_sets = db.query(StudySet, FolderStudySet.added_at).join(
            FolderStudySet, StudySet.id == FolderStudySet.study_set_id
        ).filter(
            and_(
                FolderStudySet.folder_id == folder_id,
                StudySet.is_public == True
            )
        ).order_by(FolderStudySet.added_at.desc()).all()
        
        result = []
        for study_set, added_at in study_sets:
            result.append({
                "id": study_set.id,
                "title": study_set.title,
                "description": study_set.description,
                "terms_count": study_set.terms_count,
                "color": getattr(study_set, "color", None),
                "is_public": study_set.is_public,
                "added_at": added_at
            })
        
        return result

    @staticmethod
    def move_study_set_to_folder(db: Session, study_set_id: int, target_folder_id: int, user_id: int) -> bool:
        """Di chuyển study set sang thư mục khác"""
        # Kiểm tra study set thuộc về user
        study_set = db.query(StudySet).filter(
            and_(StudySet.id == study_set_id, StudySet.user_id == user_id)
        ).first()
        if not study_set:
            return False
        
        # Kiểm tra target folder thuộc về user
        target_folder = FolderService.get_folder_by_id(db, target_folder_id, user_id)
        if not target_folder:
            return False
        
        # Xóa khỏi tất cả folder hiện tại
        db.query(FolderStudySet).filter(
            FolderStudySet.study_set_id == study_set_id
        ).delete()
        
        # Thêm vào folder mới
        folder_study_set = FolderStudySet(
            folder_id=target_folder_id,
            study_set_id=study_set_id
        )
        db.add(folder_study_set)
        db.commit()
        return True

    @staticmethod
    def get_folder_with_study_sets_count(db: Session, folder: Folder) -> dict:
        """Lấy thông tin folder với số lượng study sets"""
        study_sets_count = db.query(FolderStudySet).filter(
            FolderStudySet.folder_id == folder.id
        ).count()
        
        folder_dict = {
            "id": folder.id,
            "name": folder.name,
            "description": folder.description,
            "color": folder.color,
            "icon": folder.icon,
            "user_id": folder.user_id,
            "is_public": folder.is_public,
            "position": folder.position,
            "study_sets_count": study_sets_count,
            "created_at": folder.created_at,
            "updated_at": folder.updated_at
        }
        
        return folder_dict 