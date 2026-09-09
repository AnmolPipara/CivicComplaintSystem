from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .base import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    citizen = relationship("Citizen", back_populates="votes")
    complaint = relationship("Complaint", back_populates="votes")
    
    __table_args__ = (
        UniqueConstraint("citizen_id", "complaint_id", name="uq_citizen_complaint_vote"),
        Index("ix_votes_complaint_created", "complaint_id", "created_at"),
    )