from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict
from datetime import datetime
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate


class ReportService:
    
    @staticmethod
    def create_report(
        db: Session, 
        reported_by_user_id: int, 
        reported_entity_type: str, 
        reported_entity_id: int, 
        reason: str
    ) -> Report:
        """Create a new report"""
        report = Report(
            reported_by_user_id=reported_by_user_id,
            reported_entity_type=reported_entity_type,
            reported_entity_id=reported_entity_id,
            reason=reason
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    
    @staticmethod
    def get_reports(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> List[Report]:
        """Get reports with optional filtering"""
        query = db.query(Report)
        
        if status:
            query = query.filter(Report.status == status)
        
        if entity_type:
            query = query.filter(Report.reported_entity_type == entity_type)
        
        return query.order_by(desc(Report.reported_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_report_by_id(db: Session, report_id: int) -> Optional[Report]:
        """Get a specific report by ID"""
        return db.query(Report).filter(Report.id == report_id).first()
    
    @staticmethod
    def resolve_report(
        db: Session, 
        report_id: int, 
        resolved_by_user_id: int, 
        status: str
    ) -> Optional[Report]:
        """Resolve a report"""
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if report:
            report.status = status
            report.resolved_by_user_id = resolved_by_user_id
            report.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(report)
        
        return report
    
    @staticmethod
    def get_report_stats(db: Session) -> Dict:
        """Get report statistics"""
        total = db.query(Report).count()
        pending = db.query(Report).filter(Report.status == "pending").count()
        resolved = db.query(Report).filter(Report.status == "resolved").count()
        
        # Get reports by type
        type_stats = db.query(
            Report.reported_entity_type,
            func.count(Report.id).label('count')
        ).group_by(Report.reported_entity_type).all()
        
        reports_by_type = {stat.reported_entity_type: stat.count for stat in type_stats}
        
        # Get reports by status
        status_stats = db.query(
            Report.status,
            func.count(Report.id).label('count')
        ).group_by(Report.status).all()
        
        reports_by_status = {stat.status: stat.count for stat in status_stats}
        
        return {
            "total_reports": total,
            "pending_reports": pending,
            "resolved_reports": resolved,
            "reports_by_type": reports_by_type,
            "reports_by_status": reports_by_status
        }
    
    @staticmethod
    def get_user_reports(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """Get reports created by a specific user"""
        return db.query(Report).filter(
            Report.reported_by_user_id == user_id
        ).order_by(desc(Report.reported_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def check_existing_report(
        db: Session, 
        reported_by_user_id: int, 
        reported_entity_type: str, 
        reported_entity_id: int
    ) -> Optional[Report]:
        """Check if user has already reported this entity"""
        return db.query(Report).filter(
            Report.reported_by_user_id == reported_by_user_id,
            Report.reported_entity_type == reported_entity_type,
            Report.reported_entity_id == reported_entity_id,
            Report.status.in_(["pending", "reviewed"])
        ).first()
    
    @staticmethod
    def get_entity_reports(
        db: Session, 
        entity_type: str, 
        entity_id: int
    ) -> List[Report]:
        """Get all reports for a specific entity"""
        return db.query(Report).filter(
            Report.reported_entity_type == entity_type,
            Report.reported_entity_id == entity_id
        ).order_by(desc(Report.reported_at)).all()
    
    @staticmethod
    def bulk_resolve_reports(
        db: Session, 
        report_ids: List[int], 
        resolved_by_user_id: int, 
        status: str
    ) -> int:
        """Resolve multiple reports at once"""
        result = db.query(Report).filter(
            Report.id.in_(report_ids)
        ).update({
            "status": status,
            "resolved_by_user_id": resolved_by_user_id,
            "resolved_at": datetime.utcnow()
        })
        
        db.commit()
        return result 