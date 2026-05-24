from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import models
from database import get_db

# Security scheme
security = HTTPBearer()


# Pydantic schemas for API requests/responses
class UserBase(BaseModel):
    email: str
    full_name: str
    role: models.UserRole
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ObjectBase(BaseModel):
    name: str
    address: str
    status: models.ObjectStatus
    object_type: Optional[str] = None
    contractor_id: Optional[int] = None
    responsible_id: Optional[int] = None
    completion_date: Optional[date] = None
    warranty_until: Optional[date] = None
    area_sqm: Optional[float] = None
    floor_count: Optional[int] = None
    build_year: Optional[int] = None
    metadata: Optional[dict] = {}


class ObjectCreate(ObjectBase):
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class ObjectResponse(ObjectBase):
    id: int
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DefectBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: models.DefectPriority
    object_id: int


class DefectCreate(DefectBase):
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    assigned_to: Optional[int] = None


class DefectResponse(DefectBase):
    id: int
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    photos: list = []
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    object_id: int
    defect_id: Optional[int] = None
    priority: Optional[str] = "средний"
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    status: models.TaskStatus
    created_by: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FieldReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    object_id: int


class FieldReportCreate(FieldReportBase):
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    photos: Optional[List[str]] = []
    videos: Optional[List[str]] = []


class FieldReportResponse(FieldReportBase):
    id: int
    report_date: datetime
    location: Optional[str] = None
    voice_note_path: Optional[str] = None
    photos: list = []
    videos: list = []
    qr_code: Optional[str] = None
    status: str
    synced: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    name: str
    doc_type: str
    object_id: int


class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    version: int
    uploaded_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_objects: int
    objects_by_status: dict
    open_defects: int
    critical_defects: int
    overdue_tasks: int
    expiring_warranties: int
    contractors_load: dict


# Helper functions
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Get current authenticated user from JWT token"""
    # Simplified authentication - in production, verify JWT token
    # For demo purposes, return first admin user
    user = db.query(models.User).filter(
        models.User.email == "admin@oks.ru"
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
