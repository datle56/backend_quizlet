from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class StudySet(Base):
    __tablename__ = "study_sets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    terms_count = Column(Integer, default=0)
    language_from = Column(String(10), nullable=True)  # e.g., 'en', 'vi'
    language_to = Column(String(10), nullable=True)
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="study_sets")
    terms = relationship("Term", back_populates="study_set", cascade="all, delete-orphan")
    versions = relationship("StudySetVersion", back_populates="study_set", cascade="all, delete-orphan")


class Term(Base):
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    study_set_id = Column(Integer, ForeignKey("study_sets.id"), nullable=False, index=True)
    term = Column(String(500), nullable=False)
    definition = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    position = Column(Integer, default=0)

    # Relationships
    study_set = relationship("StudySet", back_populates="terms")


class StudySetVersion(Base):
    __tablename__ = "study_set_versions"

    id = Column(Integer, primary_key=True, index=True)
    study_set_id = Column(Integer, ForeignKey("study_sets.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    changes_summary = Column(Text, nullable=True)

    # Relationships
    study_set = relationship("StudySet", back_populates="versions")
    user = relationship("User") 