from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.report import (
    ReportCreate, ReportResponse, ReportListResponse, ReportStats
)
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/", response_model=ReportResponse)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new report"""
    # Check if user has already reported this entity
    existing_report = ReportService.check_existing_report(
        db, current_user.id, report_data.reported_entity_type, report_data.reported_entity_id
    )
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reported this content"
        )
    
    report = ReportService.create_report(
        db, current_user.id, report_data.reported_entity_type, 
        report_data.reported_entity_id, report_data.reason
    )
    
    return ReportResponse.model_validate(report)


@router.get("/", response_model=ReportListResponse)
def get_reports(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reports (admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    reports = ReportService.get_reports(db, skip, limit, status, entity_type)
    
    # Get statistics
    stats = ReportService.get_report_stats(db)
    
    return ReportListResponse(
        reports=[ReportResponse.model_validate(report) for report in reports],
        total=stats["total_reports"],
        pending_count=stats["pending_reports"],
        resolved_count=stats["resolved_reports"]
    )


@router.get("/stats", response_model=ReportStats)
def get_report_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report statistics (admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = ReportService.get_report_stats(db)
    return ReportStats.model_validate(stats)


@router.get("/my-reports", response_model=List[ReportResponse])
def get_my_reports(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reports created by the current user"""
    reports = ReportService.get_user_reports(db, current_user.id, skip, limit)
    return [ReportResponse.model_validate(report) for report in reports]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific report by ID"""
    report = ReportService.get_report_by_id(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Users can only view their own reports, unless they're admin
    # TODO: Add admin role check
    # if report.reported_by_user_id != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Access denied")
    
    return ReportResponse.model_validate(report)


@router.put("/{report_id}/resolve", response_model=ReportResponse)
def resolve_report(
    report_id: int,
    status: str = Query(..., description="New status for the report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve a report (admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    valid_statuses = ["pending", "reviewed", "resolved", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    report = ReportService.resolve_report(db, report_id, current_user.id, status)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return ReportResponse.model_validate(report)


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[ReportResponse])
def get_entity_reports(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reports for a specific entity (admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    reports = ReportService.get_entity_reports(db, entity_type, entity_id)
    return [ReportResponse.model_validate(report) for report in reports]


@router.post("/bulk-resolve", response_model=dict)
def bulk_resolve_reports(
    report_ids: List[int],
    status: str = Query(..., description="New status for the reports"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve multiple reports at once (admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    valid_statuses = ["pending", "reviewed", "resolved", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    count = ReportService.bulk_resolve_reports(db, report_ids, current_user.id, status)
    return {"message": f"Resolved {count} reports"}


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a report (admin only)"""
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    report = ReportService.get_report_by_id(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()
    return None 