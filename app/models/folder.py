from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(20), nullable=True)  # Màu sắc thư mục
    icon = Column(String(50), nullable=True)   # Biểu tượng thư mục
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=False)  # Thêm trường public/private
    position = Column(Integer, default=0)  # Thứ tự sắp xếp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="folders")
    study_sets = relationship("FolderStudySet", back_populates="folder", cascade="all, delete-orphan")


class FolderStudySet(Base):
    __tablename__ = "folder_study_sets"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=False, index=True)
    study_set_id = Column(Integer, ForeignKey("study_sets.id"), nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    folder = relationship("Folder", back_populates="study_sets")
    study_set = relationship("StudySet") 