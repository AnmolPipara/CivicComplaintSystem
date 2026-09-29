from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator, field_serializer
from enum import Enum
import json


class UserRole(str, Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    DEPARTMENT = "department"


class ComplaintStatus(str, Enum):
    PENDING = "pending"
    WORKING = "working"
    COMPLETED = "completed"


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CITIZEN


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_location: bool = False
    
    class Config:
        from_attributes = True

    @field_serializer('created_at', check_fields=False)
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


class CitizenProfile(BaseModel):
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferred_notification_channels: Optional[str] = "email,push"


class AdminProfile(BaseModel):
    department_id: Optional[int] = None


class CategoryBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    base_severity: float = Field(default=0.5, ge=0.0, le=1.0)
    department_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

    @field_serializer('created_at', check_fields=False)
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")


class ComplaintBase(BaseModel):
    description: Optional[str] = ""
    category_id: int
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    evidence_urls: Optional[List[str]] = []

    @model_validator(mode='before')
    @classmethod
    def parse_evidence_urls(cls, data):
        if isinstance(data, dict) and 'evidence_urls' in data:
            val = data['evidence_urls']
            if isinstance(val, str):
                try:
                    data['evidence_urls'] = eval(val) if val.startswith('[') else json.loads(val)
                except Exception:
                    data['evidence_urls'] = []
        elif hasattr(data, 'evidence_urls'):
            val = getattr(data, 'evidence_urls')
            if isinstance(val, str):
                try:
                    setattr(data, 'evidence_urls', eval(val) if val.startswith('[') else json.loads(val))
                except Exception:
                    setattr(data, 'evidence_urls', [])
        return data


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    department_id: Optional[int] = None
    description: Optional[str] = None


class ComplaintStatusHistoryResponse(BaseModel):
    id: int
    previous_status: Optional[ComplaintStatus]
    new_status: ComplaintStatus
    changed_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

    @field_serializer('created_at', check_fields=False)
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")


class ComplaintResponse(ComplaintBase):
    id: int
    citizen_id: int
    department_id: Optional[int]
    status: ComplaintStatus
    upvote_count: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    category: Optional[CategoryResponse] = None
    status_history: List[ComplaintStatusHistoryResponse] = []
    
    # Priority & Assessment fields
    severity_score: Optional[int] = None
    impact_score: Optional[int] = None
    urgency_score: Optional[int] = None
    priority_score: Optional[float] = None
    priority_level: Optional[str] = None
    assessment_status: Optional[str] = "pending"
    assessment_reason: Optional[str] = None
    assessment_confidence: Optional[str] = None
    missing_information: Optional[List[str]] = []
    needs_human_review: Optional[bool] = False
    is_safety_escalated: Optional[bool] = False
    ai_severity_score: Optional[int] = None
    ai_impact_score: Optional[int] = None
    ai_urgency_score: Optional[int] = None
    ai_reason: Optional[str] = None
    admin_override: Optional[bool] = False
    admin_override_reason: Optional[str] = None
    user_voted: Optional[bool] = False
    
    class Config:
        from_attributes = True

    @field_serializer('created_at', 'updated_at', 'resolved_at', 'assigned_at', 'started_at', check_fields=False)
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")


class AssessmentOverrideRequest(BaseModel):
    severity_score: Optional[int] = Field(None, ge=0, le=100)
    impact_score: Optional[int] = Field(None, ge=0, le=100)
    urgency_score: Optional[int] = Field(None, ge=0, le=100)
    is_safety_escalated: Optional[bool] = None
    needs_human_review: Optional[bool] = None
    admin_notes: Optional[str] = None


class ComplaintListResponse(BaseModel):
    complaints: List[ComplaintResponse]
    total: int
    page: int
    page_size: int


class DepartmentBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    head_name: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: float
    
    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    complaint_id: int


class VoteResponse(BaseModel):
    id: int
    citizen_id: int
    complaint_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True