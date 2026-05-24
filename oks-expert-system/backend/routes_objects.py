from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/objects", tags=["objects"])


@router.get("", response_model=List[schemas.ObjectResponse])
def get_objects(
    status: Optional[models.ObjectStatus] = None,
    object_type: Optional[str] = None,
    contractor_id: Optional[int] = None,
    responsible_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all objects with optional filtering"""
    query = db.query(models.Object)
    
    if status:
        query = query.filter(models.Object.status == status)
    if object_type:
        query = query.filter(models.Object.object_type == object_type)
    if contractor_id:
        query = query.filter(models.Object.contractor_id == contractor_id)
    if responsible_id:
        query = query.filter(models.Object.responsible_id == responsible_id)
    
    return query.all()


@router.get("/{object_id}", response_model=schemas.ObjectResponse)
def get_object(object_id: int, db: Session = Depends(get_db)):
    """Get a specific object by ID"""
    obj = db.query(models.Object).filter(models.Object.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@router.post("", response_model=schemas.ObjectResponse)
def create_object(
    obj_data: schemas.ObjectCreate,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new object"""
    # Convert coordinates to PostGIS geography point
    location = None
    if obj_data.longitude and obj_data.latitude:
        location = func.ST_GeogFromText(
            f"SRID=4326;POINT({obj_data.longitude} {obj_data.latitude})"
        )
    
    db_obj = models.Object(
        name=obj_data.name,
        address=obj_data.address,
        status=obj_data.status,
        object_type=obj_data.object_type,
        contractor_id=obj_data.contractor_id,
        responsible_id=obj_data.responsible_id,
        completion_date=obj_data.completion_date,
        warranty_until=obj_data.warranty_until,
        area_sqm=obj_data.area_sqm,
        floor_count=obj_data.floor_count,
        build_year=obj_data.build_year,
        metadata=obj_data.metadata or {},
        location=location
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


@router.put("/{object_id}", response_model=schemas.ObjectResponse)
def update_object(
    object_id: int,
    obj_data: schemas.ObjectBase,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing object"""
    db_obj = db.query(models.Object).filter(models.Object.id == object_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # Update fields
    for field, value in obj_data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


@router.delete("/{object_id}")
def delete_object(
    object_id: int,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an object"""
    db_obj = db.query(models.Object).filter(models.Object.id == object_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    db.delete(db_obj)
    db.commit()
    
    return {"message": "Object deleted successfully"}


@router.get("/{object_id}/documents", response_model=List[schemas.DocumentResponse])
def get_object_documents(object_id: int, db: Session = Depends(get_db)):
    """Get all documents for an object"""
    obj = db.query(models.Object).filter(models.Object.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    return obj.documents


@router.get("/{object_id}/defects", response_model=List[schemas.DefectResponse])
def get_object_defects(object_id: int, db: Session = Depends(get_db)):
    """Get all defects for an object"""
    obj = db.query(models.Object).filter(models.Object.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    return obj.defects


@router.get("/{object_id}/tasks", response_model=List[schemas.TaskResponse])
def get_object_tasks(object_id: int, db: Session = Depends(get_db)):
    """Get all tasks for an object"""
    obj = db.query(models.Object).filter(models.Object.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    return obj.tasks


@router.get("/nearby")
def get_nearby_objects(
    longitude: float = Query(..., description="Longitude"),
    latitude: float = Query(..., description="Latitude"),
    radius_meters: int = Query(1000, description="Search radius in meters"),
    db: Session = Depends(get_db)
):
    """Get objects within a radius of a point"""
    point_wkt = f"SRID=4326;POINT({longitude} {latitude})"
    
    objects = db.query(models.Object).filter(
        func.ST_DWithin(
            models.Object.location,
            func.ST_GeogFromText(point_wkt),
            radius_meters
        )
    ).all()
    
    return objects
