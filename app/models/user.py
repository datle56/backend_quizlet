from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_premium = Column(Boolean, default=False)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    total_study_sets_created = Column(Integer, default=0)
    total_terms_learned = Column(Integer, default=0)

    # Relationships
    study_sets = relationship("StudySet", back_populates="user")
    folders = relationship("Folder", back_populates="user") 