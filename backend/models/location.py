from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    landmark = Column(String(255), nullable=True)
    area_name = Column(String(100), nullable=True, index=True)
    city = Column(String(100), default="Mumbai", nullable=False)
    state = Column(String(100), default="Maharashtra", nullable=False)
    pincode = Column(String(10), nullable=True, index=True)
    is_sensitive_zone = Column(Integer, default=0)  # 0=normal, 1=near hospital, 2=near school, 3=high footfall
    created_at = Column(Float, default=0)  # Using float for timestamp for trie sorting
    
    complaints = relationship("Complaint", back_populates="location")
    
    __table_args__ = (
        Index("ix_locations_coordinates", "latitude", "longitude"),
        Index("ix_locations_area_city", "area_name", "city"),
    )

    def calculate_distance(self, other_lat: float, other_lon: float) -> float:
        """Calculate Haversine distance in kilometers"""
        import math
        R = 6371  # Earth's radius in km
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other_lat), math.radians(other_lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c