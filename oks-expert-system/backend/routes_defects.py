from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/defects", tags=["defects"])


@router.get("", response_model=List[schemas.DefectResponse])
def get_defects(
    status: str = None,
    priority: models.DefectPriority = None,
    object_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all defects with optional filtering"""
    query = db.query(models.Defect)
    
    if status:
        query = query.filter(models.Defect.status == status)
    if priority:
        query = query.filter(models.Defect.priority == priority)
    if object_id:
        query = query.filter(models.Defect.object_id == object_id)
    
    return query.all()


@router.get("/{defect_id}", response_model=schemas.DefectResponse)
def get_defect(defect_id: int, db: Session = Depends(get_db)):
    """Get a specific defect by ID"""
    defect = db.query(models.Defect).filter(models.Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    return defect


@router.post("", response_model=schemas.DefectResponse)
def create_defect(
    defect_data: schemas.DefectCreate,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new defect"""
    # Convert coordinates to PostGIS geography point
    location_point = None
    if defect_data.longitude and defect_data.latitude:
        location_point = f"SRID=4326;POINT({defect_data.longitude} {defect_data.latitude})"
    
    db_defect = models.Defect(
        title=defect_data.title,
        description=defect_data.description,
        priority=defect_data.priority,
        object_id=defect_data.object_id,
        assigned_to=defect_data.assigned_to,
        detected_by=current_user.id,
        location_point=location_point
    )
    
    db.add(db_defect)
    db.commit()
    db.refresh(db_defect)
    
    return db_defect


@router.put("/{defect_id}", response_model=schemas.DefectResponse)
def update_defect(
    defect_id: int,
    status: str = None,
    assigned_to: int = None,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db)
):
    """Update a defect"""
    db_defect = db.query(models.Defect).filter(models.Defect.id == defect_id).first()
    if not db_defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    if status:
        db_defect.status = status
        if status == "закрыт":
            from datetime import datetime
            db_defect.resolved_at = datetime.now()
    
    if assigned_to:
        db_defect.assigned_to = assigned_to
    
    db.commit()
    db.refresh(db_defect)
    
    return db_defect


@router.delete("/{defect_id}")
def delete_defect(
    defect_id: int,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a defect"""
    db_defect = db.query(models.Defect).filter(models.Defect.id == defect_id).first()
    if not db_defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    db.delete(db_defect)
    db.commit()
    
    return {"message": "Defect deleted successfully"}
