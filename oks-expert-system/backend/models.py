from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, DECIMAL, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, GEOGRAPHY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles in the system"""
    администратор = "администратор"
    руководитель_проекта = "руководитель_проекта"
    инженер_окс = "инженер_окс"
    инженер_эксплуатации = "инженер_эксплуатации"
    подрядчик = "подрядчик"
    аудит = "аудит"


class ObjectStatus(str, enum.Enum):
    """Object lifecycle status"""
    строится = "строится"
    сдан = "сдан"
    на_гарантии = "на_гарантии"
    эксплуатация = "эксплуатация"
    аварийный = "аварийный"


class TaskStatus(str, enum.Enum):
    """Task status"""
    новая = "новая"
    в_работе = "в_работе"
    на_согласовании = "на_согласовании"
    выполнена = "выполнена"
    просрочена = "просрочена"


class DefectPriority(str, enum.Enum):
    """Defect priority levels"""
    низкий = "низкий"
    средний = "средний"
    высокий = "высокий"
    критический = "критический"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    objects_responsible = relationship("Object", foreign_keys="Object.responsible_id", back_populates="responsible")
    objects_contractor = relationship("Object", foreign_keys="Object.contractor_id", back_populates="contractor")
    defects_detected = relationship("Defect", foreign_keys="Defect.detected_by", back_populates="detector")
    defects_assigned = relationship("Defect", foreign_keys="Defect.assigned_to", back_populates="assignee")
    tasks_created = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")


class Object(Base):
    """Construction/Operation object model with geospatial data"""
    __tablename__ = "objects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=False)
    status = Column(SQLEnum(ObjectStatus), nullable=False, default=ObjectStatus.эксплуатация)
    object_type = Column(String(100))
    contractor_id = Column(Integer, ForeignKey("users.id"))
    responsible_id = Column(Integer, ForeignKey("users.id"))
    completion_date = Column(Date)
    warranty_until = Column(Date)
    location = Column(GEOGRAPHY('POINT', 4326))  # WGS84 coordinates
    boundary = Column(GEOGRAPHY('POLYGON', 4326))  # Property boundary
    area_sqm = Column(DECIMAL(10, 2))
    floor_count = Column(Integer)
    build_year = Column(Integer)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contractor = relationship("User", foreign_keys=[contractor_id], back_populates="objects_contractor")
    responsible = relationship("User", foreign_keys=[responsible_id], back_populates="objects_responsible")
    documents = relationship("Document", back_populates="object", cascade="all, delete-orphan")
    defects = relationship("Defect", back_populates="object", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="object", cascade="all, delete-orphan")
    field_reports = relationship("FieldReport", back_populates="object", cascade="all, delete-orphan")


class Document(Base):
    """Document model for project documentation"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    doc_type = Column(String(100), nullable=False)  # проектная, исполнительная, паспорт, журнал
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    version = Column(Integer, default=1)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSONB, default={})
    
    # Relationships
    object = relationship("Object", back_populates="documents")


class Defect(Base):
    """Defect/Issue model"""
    __tablename__ = "defects"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(DefectPriority), nullable=False, default=DefectPriority.средний)
    status = Column(String(50), default="открыт")
    location_point = Column(GEOGRAPHY('POINT', 4326))
    detected_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    photos = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})
    
    # Relationships
    object = relationship("Object", back_populates="defects")
    detector = relationship("User", foreign_keys=[detected_by], back_populates="defects_detected")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="defects_assigned")
    tasks = relationship("Task", back_populates="defect")


class Task(Base):
    """Task model for work assignments"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    defect_id = Column(Integer, ForeignKey("defects.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.новая)
    priority = Column(String(50), default="средний")
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    due_date = Column(Date)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    object = relationship("Object", back_populates="tasks")
    defect = relationship("Defect", back_populates="tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="tasks_created")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="tasks_assigned")


class FieldReport(Base):
    """Field report model for mobile inspections"""
    __tablename__ = "field_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    report_date = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(GEOGRAPHY('POINT', 4326))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    voice_note_path = Column(String(500))
    photos = Column(JSONB, default=[])
    videos = Column(JSONB, default=[])
    qr_code = Column(String(100))
    status = Column(String(50), default="черновик")
    synced = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSONB, default={})
    
    # Relationships
    object = relationship("Object", back_populates="field_reports")


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """Audit log for tracking changes"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
