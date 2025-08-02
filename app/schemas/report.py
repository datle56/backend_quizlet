from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReportBase(BaseModel):
    reported_entity_type: str = Field(..., description="Type of reported entity")
    reported_entity_id: int = Field(..., description="ID of reported entity")
    reason: str = Field(..., description="Reason for report")


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    status: str = Field(..., description="New status for the report")
    resolved_by_user_id: Optional[int] = Field(None, description="User ID who resolved the report")


class ReportResponse(ReportBase):
    id: int
    reported_by_user_id: int
    status: str
    resolved_by_user_id: Optional[int]
    reported_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    reports: list[ReportResponse]
    total: int
    pending_count: int
    resolved_count: int


class ReportStats(BaseModel):
    total_reports: int
    pending_reports: int
    resolved_reports: int
    reports_by_type: dict[str, int]
    reports_by_status: dict[str, int] 