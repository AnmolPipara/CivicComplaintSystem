from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    head_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Float, default=0)  # timestamp
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    
    user = relationship("User", back_populates="department_profile", uselist=False)
    complaints = relationship("Complaint", back_populates="department")
    categories = relationship("Category", back_populates="department")