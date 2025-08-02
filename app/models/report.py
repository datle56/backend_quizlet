from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reported_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_entity_type = Column(String(50), nullable=False)
    reported_entity_id = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"))
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True)) 