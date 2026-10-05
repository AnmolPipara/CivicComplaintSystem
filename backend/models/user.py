import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    DEPARTMENT = "department"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CITIZEN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    citizen_profile = relationship("Citizen", back_populates="user", uselist=False)
    admin_profile = relationship("Admin", back_populates="user", uselist=False)
    department_profile = relationship("Department", back_populates="user", uselist=False)

    @property
    def address(self):
        return self.citizen_profile.address if self.citizen_profile else None

    @property
    def latitude(self):
        return self.citizen_profile.latitude if self.citizen_profile else None

    @property
    def longitude(self):
        return self.citizen_profile.longitude if self.citizen_profile else None

    @property
    def has_location(self) -> bool:
        return bool(self.latitude is not None and self.longitude is not None)


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    preferred_notification_channels = Column(String(100), default="email,push")

    user = relationship("User", back_populates="citizen_profile")
    complaints = relationship("Complaint", back_populates="citizen")
    votes = relationship("Vote", back_populates="citizen")

    @property
    def full_name(self):
        return self.user.full_name if self.user else None

    @property
    def email(self):
        return self.user.email if self.user else None

    @property
    def phone(self):
        return self.user.phone if self.user else None

    @property
    def registered_at(self):
        return self.user.created_at if self.user else None


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    department_id = Column(Integer, nullable=True)
    permissions = Column(String(500), default="all")

    user = relationship("User", back_populates="admin_profile")