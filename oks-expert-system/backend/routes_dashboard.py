from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Total objects
    total_objects = db.query(models.Object).count()
    
    # Objects by status
    objects_by_status = {}
    for status in models.ObjectStatus:
        count = db.query(models.Object).filter(
            models.Object.status == status
        ).count()
        objects_by_status[status.value] = count
    
    # Open defects
    open_defects = db.query(models.Defect).filter(
        models.Defect.status == "открыт"
    ).count()
    
    # Critical defects
    critical_defects = db.query(models.Defect).filter(
        models.Defect.priority == models.DefectPriority.критический,
        models.Defect.status == "открыт"
    ).count()
    
    # Overdue tasks
    today = date.today()
    overdue_tasks = db.query(models.Task).filter(
        models.Task.status != models.TaskStatus.выполнена,
        models.Task.due_date < today
    ).count()
    
    # Expiring warranties (within 90 days)
    warranty_threshold = today + timedelta(days=90)
    expiring_warranties = db.query(models.Object).filter(
        models.Object.warranty_until != None,
        models.Object.warranty_until <= warranty_threshold,
        models.Object.warranty_until >= today
    ).count()
    
    # Contractors load (tasks per contractor)
    contractors_load = {}
    contractors = db.query(models.User).filter(
        models.User.role == models.UserRole.подрядчик
    ).all()
    
    for contractor in contractors:
        active_tasks = db.query(models.Task).filter(
            models.Task.assigned_to == contractor.id,
            models.Task.status.in_([models.TaskStatus.новая, models.TaskStatus.в_работе])
        ).count()
        contractors_load[contractor.full_name] = active_tasks
    
    return schemas.DashboardStats(
        total_objects=total_objects,
        objects_by_status=objects_by_status,
        open_defects=open_defects,
        critical_defects=critical_defects,
        overdue_tasks=overdue_tasks,
        expiring_warranties=expiring_warranties,
        contractors_load=contractors_load
    )


@router.get("/map-objects")
def get_map_objects(
    status: str = None,
    object_type: str = None,
    db: Session = Depends(get_db)
):
    """Get objects for map display with coordinates"""
    query = db.query(
        models.Object.id,
        models.Object.name,
        models.Object.address,
        models.Object.status,
        models.Object.object_type,
        models.Object.area_sqm,
        models.Object.floor_count,
        models.Object.warranty_until,
        func.ST_AsText(models.Object.location).label('location')
    )
    
    if status:
        query = query.filter(models.Object.status == status)
    if object_type:
        query = query.filter(models.Object.object_type == object_type)
    
    results = []
    for row in query.all():
        # Parse location from WKT format
        longitude = None
        latitude = None
        if row.location:
            # Format: POINT(longitude latitude)
            coords = row.location.replace("POINT(", "").replace(")", "").split()
            if len(coords) == 2:
                longitude = float(coords[0])
                latitude = float(coords[1])
        
        results.append({
            "id": row.id,
            "name": row.name,
            "address": row.address,
            "status": row.status.value if hasattr(row.status, 'value') else row.status,
            "object_type": row.object_type,
            "area_sqm": float(row.area_sqm) if row.area_sqm else None,
            "floor_count": row.floor_count,
            "warranty_until": str(row.warranty_until) if row.warranty_until else None,
            "longitude": longitude,
            "latitude": latitude
        })
    
    return results


@router.get("/recent-defects")
def get_recent_defects(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent defects for dashboard"""
    defects = db.query(
        models.Defect.id,
        models.Defect.title,
        models.Defect.priority,
        models.Defect.status,
        models.Defect.detected_at,
        models.Object.name.label('object_name')
    ).join(
        models.Object
    ).order_by(
        models.Defect.detected_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": d.id,
            "title": d.title,
            "priority": d.priority.value if hasattr(d.priority, 'value') else d.priority,
            "status": d.status,
            "detected_at": str(d.detected_at),
            "object_name": d.object_name
        }
        for d in defects
    ]


@router.get("/overdue-tasks")
def get_overdue_tasks(db: Session = Depends(get_db)):
    """Get overdue tasks for dashboard"""
    today = date.today()
    tasks = db.query(
        models.Task.id,
        models.Task.title,
        models.Task.due_date,
        models.Task.status,
        models.Object.name.label('object_name'),
        models.User.full_name.label('assignee_name')
    ).join(
        models.Object
    ).outerjoin(
        models.User, models.Task.assigned_to == models.User.id
    ).filter(
        models.Task.status != models.TaskStatus.выполнена,
        models.Task.due_date < today
    ).all()
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "due_date": str(t.due_date),
            "status": t.status.value if hasattr(t.status, 'value') else t.status,
            "object_name": t.object_name,
            "assignee_name": t.assignee_name
        }
        for t in tasks
    ]
