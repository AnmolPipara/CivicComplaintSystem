import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float, Boolean, Index
from sqlalchemy.orm import relationship
from .base import Base


class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    PRIORITIZED = "prioritized"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class PriorityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    
    description = Column(Text, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.SUBMITTED, nullable=False, index=True)
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.LOW, nullable=False, index=True)
    priority_score = Column(Float, default=0.0, nullable=False)
    
    evidence_urls = Column(Text, nullable=True)  # JSON array of URLs
    upvote_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    
    citizen = relationship("Citizen", back_populates="complaints")
    category = relationship("Category", back_populates="complaints")
    location = relationship("Location", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    votes = relationship("Vote", back_populates="complaint")
    status_history = relationship("ComplaintStatusHistory", back_populates="complaint", order_by="ComplaintStatusHistory.created_at")
    notifications = relationship("Notification", back_populates="complaint")
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True, index=True)
    cluster = relationship("Cluster", back_populates="complaints")

    __table_args__ = (
        Index("ix_complaints_status_priority_created", "status", "priority", "created_at"),
        Index("ix_complaints_citizen_status", "citizen_id", "status"),
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    base_severity = Column(Float, default=0.5, nullable=False)  # 0-1 normalized severity
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    complaints = relationship("Complaint", back_populates="category")
    department = relationship("Department", back_populates="categories")


class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    previous_status = Column(Enum(ComplaintStatus), nullable=True)
    new_status = Column(Enum(ComplaintStatus), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    complaint = relationship("Complaint", back_populates="status_history")