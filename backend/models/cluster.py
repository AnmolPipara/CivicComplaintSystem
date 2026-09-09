from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=1.0, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    complaint_count = Column(Integer, default=0, nullable=False)
    created_at = Column(Float, default=0)  # timestamp
    updated_at = Column(Float, default=0)  # timestamp
    
    category = relationship("Category")
    complaints = relationship("Complaint", back_populates="cluster")
    
    __table_args__ = (
        Index("ix_clusters_center", "center_latitude", "center_longitude"),
        Index("ix_clusters_category", "category_id"),
    )