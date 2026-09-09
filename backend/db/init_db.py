from db.session import engine, Base
from models import User, Citizen, Admin, Department, Category, Location, Complaint, Vote, Notification, Cluster, ComplaintStatusHistory


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_db():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully")


if __name__ == "__main__":
    init_db()