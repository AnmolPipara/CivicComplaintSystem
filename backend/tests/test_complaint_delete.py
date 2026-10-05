import pytest
from fastapi.testclient import TestClient
from main import app
from db.session import SessionLocal
from models import (
    User, Citizen, Admin, Department, Category, Complaint,
    ComplaintStatus, UserRole, Vote, ComplaintStatusHistory
)
from common.auth import get_password_hash, create_access_token

client = TestClient(app)

def test_complaint_delete_lifecycle():
    db = SessionLocal()
    try:
        # 1. Setup test citizen 1
        citizen1 = db.query(User).filter(User.email == "delete_citizen1@jansewa.org").first()
        if not citizen1:
            citizen1 = User(
                email="delete_citizen1@jansewa.org",
                password_hash=get_password_hash("password123"),
                full_name="Citizen One",
                role=UserRole.CITIZEN,
                is_active=True
            )
            db.add(citizen1)
            db.commit()
            db.refresh(citizen1)

        prof1 = db.query(Citizen).filter(Citizen.user_id == citizen1.id).first()
        if not prof1:
            prof1 = Citizen(user_id=citizen1.id, address="Street 1, Area 1", latitude=28.61, longitude=77.20)
            db.add(prof1)
            db.commit()
            db.refresh(prof1)

        # 2. Setup test citizen 2
        citizen2 = db.query(User).filter(User.email == "delete_citizen2@jansewa.org").first()
        if not citizen2:
            citizen2 = User(
                email="delete_citizen2@jansewa.org",
                password_hash=get_password_hash("password123"),
                full_name="Citizen Two",
                role=UserRole.CITIZEN,
                is_active=True
            )
            db.add(citizen2)
            db.commit()
            db.refresh(citizen2)

        prof2 = db.query(Citizen).filter(Citizen.user_id == citizen2.id).first()
        if not prof2:
            prof2 = Citizen(user_id=citizen2.id, address="Street 2, Area 2", latitude=28.62, longitude=77.21)
            db.add(prof2)
            db.commit()
            db.refresh(prof2)

        # 3. Setup admin
        admin_user = db.query(User).filter(User.email == "delete_admin@jansewa.org").first()
        if not admin_user:
            admin_user = User(
                email="delete_admin@jansewa.org",
                password_hash=get_password_hash("admin123"),
                full_name="Delete Admin",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        admin_prof = db.query(Admin).filter(Admin.user_id == admin_user.id).first()
        if not admin_prof:
            admin_prof = Admin(user_id=admin_user.id, permissions="all")
            db.add(admin_prof)
            db.commit()

        # Category
        category = db.query(Category).first()
        if not category:
            category = Category(name="pothole", display_name="Pothole Damage", base_severity=0.6)
            db.add(category)
            db.commit()
            db.refresh(category)

        # Create a pending complaint for citizen 1
        complaint1 = Complaint(
            citizen_id=prof1.id,
            category_id=category.id,
            location="Connaught Place, New Delhi",
            latitude=28.6315,
            longitude=77.2167,
            description="Testing complaint deletion pending status",
            status=ComplaintStatus.PENDING
        )
        db.add(complaint1)
        db.commit()
        db.refresh(complaint1)

        # Add a vote and status history to ensure cascade/clean deletion works
        vote = Vote(citizen_id=prof2.id, complaint_id=complaint1.id)
        db.add(vote)
        history = ComplaintStatusHistory(
            complaint_id=complaint1.id,
            previous_status=None,
            new_status=ComplaintStatus.PENDING,
            changed_by=citizen1.id,
            notes="Initial submission"
        )
        db.add(history)
        db.commit()

        cid1 = complaint1.id
        token_cit1 = create_access_token({"sub": str(citizen1.id), "role": "citizen"})
        token_cit2 = create_access_token({"sub": str(citizen2.id), "role": "citizen"})
        token_admin = create_access_token({"sub": str(admin_user.id), "role": "admin"})

        # A) Citizen 2 tries to delete Citizen 1's complaint -> Forbidden 403
        resp_forbid = client.delete(
            f"/api/complaints/{cid1}",
            headers={"Authorization": f"Bearer {token_cit2}"}
        )
        assert resp_forbid.status_code == 403

        # B) Citizen 1 successfully deletes their own pending complaint -> 200
        resp_del = client.delete(
            f"/api/complaints/{cid1}",
            headers={"Authorization": f"Bearer {token_cit1}"}
        )
        assert resp_del.status_code == 200
        assert resp_del.json()["id"] == cid1

        # Verify it's gone from database along with vote and history
        assert db.query(Complaint).filter(Complaint.id == cid1).first() is None
        assert db.query(Vote).filter(Vote.complaint_id == cid1).first() is None
        assert db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id == cid1).first() is None

        # Verify GET returns 404
        resp_get = client.get(
            f"/api/complaints/{cid1}",
            headers={"Authorization": f"Bearer {token_admin}"}
        )
        assert resp_get.status_code == 404

        # C) Create another complaint and delete via Admin endpoint /api/admin/complaints/{id}
        complaint2 = Complaint(
            citizen_id=prof1.id,
            category_id=category.id,
            location="Saket, New Delhi",
            latitude=28.5244,
            longitude=77.2185,
            description="Testing complaint deletion by admin",
            status=ComplaintStatus.WORKING
        )
        db.add(complaint2)
        db.commit()
        db.refresh(complaint2)
        cid2 = complaint2.id

        resp_admin_del = client.delete(
            f"/api/admin/complaints/{cid2}",
            headers={"Authorization": f"Bearer {token_admin}"}
        )
        assert resp_admin_del.status_code == 200
        assert resp_admin_del.json()["id"] == cid2
        assert db.query(Complaint).filter(Complaint.id == cid2).first() is None

    finally:
        db.close()
