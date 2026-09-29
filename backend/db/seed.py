#!/usr/bin/env python3
"""
Seed script to populate initial data for development.
Run with: python -m db.seed
"""
import os
from dotenv import load_dotenv
load_dotenv()

from db.session import SessionLocal, engine, Base
from models import (
    User, Citizen, Admin, Department, Category,
    UserRole, ComplaintStatus
)
from common.auth import get_password_hash

# Seed passwords from environment (defaults are for development only)
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
SEED_DEPT_PASSWORD = os.getenv("SEED_DEPT_PASSWORD", "dept123")
SEED_CITIZEN_PASSWORD = os.getenv("SEED_CITIZEN_PASSWORD", "citizen123")


def seed_database():
    db = SessionLocal()
    
    try:
        # Create departments
        departments = [
            Department(
                name="road_maintenance",
                display_name="Road Maintenance Department",
                description="Handles potholes, road damage, and infrastructure repair",
                email="roads@city.gov",
                phone="+91-22-1234-5678",
                head_name="Rajesh Kumar",
                is_active=True,
                created_at=1700000000
            ),
            Department(
                name="sanitation",
                display_name="Sanitation Department",
                description="Handles garbage collection, waste management, and cleanliness",
                email="sanitation@city.gov",
                phone="+91-22-1234-5679",
                head_name="Priya Sharma",
                is_active=True,
                created_at=1700000000
            ),
            Department(
                name="water_supply",
                display_name="Water Supply Department",
                description="Handles water leakage, supply issues, and quality concerns",
                email="water@city.gov",
                phone="+91-22-1234-5680",
                head_name="Amit Patel",
                is_active=True,
                created_at=1700000000
            ),
            Department(
                name="electrical",
                display_name="Electrical Department",
                description="Handles streetlights, power lines, and electrical infrastructure",
                email="electrical@city.gov",
                phone="+91-22-1234-5681",
                head_name="Sunita Reddy",
                is_active=True,
                created_at=1700000000
            ),
            Department(
                name="sewerage",
                display_name="Sewerage Department",
                description="Handles sewage overflow, drainage, and wastewater management",
                email="sewerage@city.gov",
                phone="+91-22-1234-5682",
                head_name="Vikram Singh",
                is_active=True,
                created_at=1700000000
            ),
        ]
        
        for dept in departments:
            existing = db.query(Department).filter(Department.name == dept.name).first()
            if not existing:
                db.add(dept)
        
        db.flush()
        
        # Get department IDs
        dept_map = {d.name: d.id for d in db.query(Department).all()}
        
        # Create categories
        categories = [
            Category(
                name="pothole",
                display_name="Pothole / Road Damage",
                description="Potholes, cracks, and road surface damage",
                icon="road",
                base_severity=0.7,
                department_id=dept_map.get("road_maintenance"),
                is_active=True
            ),
            Category(
                name="garbage",
                display_name="Garbage / Waste",
                description="Uncollected garbage, overflowing bins, illegal dumping",
                icon="trash",
                base_severity=0.4,
                department_id=dept_map.get("sanitation"),
                is_active=True
            ),
            Category(
                name="water_leakage",
                display_name="Water Leakage",
                description="Leaking pipes, water main breaks, low pressure",
                icon="water",
                base_severity=0.6,
                department_id=dept_map.get("water_supply"),
                is_active=True
            ),
            Category(
                name="streetlight",
                display_name="Streetlight Issue",
                description="Broken, flickering, or missing streetlights",
                icon="lightbulb",
                base_severity=0.5,
                department_id=dept_map.get("electrical"),
                is_active=True
            ),
            Category(
                name="sewage_overflow",
                display_name="Sewage Overflow",
                description="Sewage backup, overflowing manholes, drainage issues",
                icon="alert-triangle",
                base_severity=0.9,
                department_id=dept_map.get("sewerage"),
                is_active=True
            ),
            Category(
                name="traffic_signal",
                display_name="Traffic Signal",
                description="Malfunctioning traffic lights, missing signage",
                icon="traffic-light",
                base_severity=0.6,
                department_id=dept_map.get("electrical"),
                is_active=True
            ),
            Category(
                name="footpath",
                display_name="Footpath / Sidewalk",
                description="Broken footpaths, encroachment, accessibility issues",
                icon="footprints",
                base_severity=0.4,
                department_id=dept_map.get("road_maintenance"),
                is_active=True
            ),
            Category(
                name="drainage",
                display_name="Drainage / Waterlogging",
                description="Clogged drains, waterlogging after rain",
                icon="droplet",
                base_severity=0.6,
                department_id=dept_map.get("sewerage"),
                is_active=True
            ),
        ]
        
        for cat in categories:
            existing = db.query(Category).filter(Category.name == cat.name).first()
            if not existing:
                db.add(cat)
        
        # Create admin user
        admin_user = db.query(User).filter(User.email == "admin@city.gov").first()
        if not admin_user:
            admin_user = User(
                email="admin@city.gov",
                phone="+91-9876543210",
                password_hash=get_password_hash(SEED_ADMIN_PASSWORD),
                full_name="City Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.flush()
            
            admin_profile = Admin(
                user_id=admin_user.id,
                permissions="all"
            )
            db.add(admin_profile)
        
        # Create department users
        dept_users = [
            ("roads@city.gov", "Road Dept Head", UserRole.DEPARTMENT, dept_map.get("road_maintenance")),
            ("sanitation@city.gov", "Sanitation Dept Head", UserRole.DEPARTMENT, dept_map.get("sanitation")),
            ("water@city.gov", "Water Dept Head", UserRole.DEPARTMENT, dept_map.get("water_supply")),
            ("electrical@city.gov", "Electrical Dept Head", UserRole.DEPARTMENT, dept_map.get("electrical")),
            ("sewerage@city.gov", "Sewerage Dept Head", UserRole.DEPARTMENT, dept_map.get("sewerage")),
        ]
        
        for email, name, role, dept_id in dept_users:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    password_hash=get_password_hash(SEED_DEPT_PASSWORD),
                    full_name=name,
                    role=role,
                    is_active=True
                )
                db.add(user)
                db.flush()
                
            admin_profile = db.query(Admin).filter(Admin.user_id == user.id).first()
            if not admin_profile:
                admin_profile = Admin(
                    user_id=user.id,
                    department_id=dept_id,
                    permissions="dept"
                )
                db.add(admin_profile)
            elif admin_profile.department_id != dept_id:
                admin_profile.department_id = dept_id
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Create tables first
    Base.metadata.create_all(bind=engine)
    seed_database()