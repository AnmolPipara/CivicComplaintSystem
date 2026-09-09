from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    DEPARTMENT = "department"


class ComplaintStatus(str, Enum):
    SUBMITTED = "submitted"
    PRIORITIZED = "prioritized"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


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
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


class CitizenProfile(BaseModel):
    address: Optional[str] = None
    preferred_notification_channels: str = "email,push"


class AdminProfile(BaseModel):
    department_id: Optional[int] = None
    permissions: str = "all"


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


class LocationBase(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    landmark: Optional[str] = None
    area_name: Optional[str] = None
    city: str = "Mumbai"
    state: str = "Maharashtra"
    pincode: Optional[str] = None
    is_sensitive_zone: int = 0


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int
    created_at: float
    
    class Config:
        from_attributes = True


class ComplaintBase(BaseModel):
    description: str
    category_id: int
    location_id: int
    evidence_urls: Optional[List[str]] = []


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    priority: Optional[PriorityLevel] = None
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


class ComplaintResponse(ComplaintBase):
    id: int
    citizen_id: int
    department_id: Optional[int]
    status: ComplaintStatus
    priority: PriorityLevel
    priority_score: float
    upvote_count: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    category: Optional[CategoryResponse] = None
    location: Optional[LocationResponse] = None
    status_history: List[ComplaintStatusHistoryResponse] = []
    
    class Config:
        from_attributes = True


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


class NotificationBase(BaseModel):
    channel: NotificationChannel
    subject: Optional[str] = None
    message: str


class NotificationCreate(NotificationBase):
    recipient_id: int
    complaint_id: Optional[int] = None


class NotificationResponse(NotificationBase):
    id: int
    recipient_id: int
    complaint_id: Optional[int]
    status: str
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClusterBase(BaseModel):
    name: Optional[str] = None
    center_latitude: float
    center_longitude: float
    radius_km: float = 1.0
    category_id: Optional[int] = None


class ClusterCreate(ClusterBase):
    pass


class ClusterResponse(ClusterBase):
    id: int
    complaint_count: int
    created_at: float
    updated_at: float
    
    class Config:
        from_attributes = True


class PriorityCalculationRequest(BaseModel):
    category_id: int
    location_id: int
    upvote_count: int = 0
    created_at: datetime


class PriorityCalculationResponse(BaseModel):
    priority: PriorityLevel
    priority_score: float
    severity_score: float
    location_score: float
    ageing_score: float
    vote_score: float