from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator
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


class ComplaintBase(BaseModel):
    description: str
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