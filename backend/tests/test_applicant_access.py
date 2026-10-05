import pytest
from fastapi.testclient import TestClient
from main import app
from db.session import SessionLocal
from models import User, Citizen, Admin, Department, Category, Complaint, ComplaintStatus, UserRole
from common.auth import get_password_hash, create_access_token

client = TestClient(app)

def test_applicant_visibility_admin_and_department():
    db = SessionLocal()
    try:
        # 1. Setup a test citizen who applies for a complaint
        citizen_user = db.query(User).filter(User.email == "test_applicant@jansewa.org").first()
        if not citizen_user:
            citizen_user = User(
                email="test_applicant@jansewa.org",
                phone="+919876543210",
                password_hash=get_password_hash("password123"),
                full_name="Rajesh Sharma",
                role=UserRole.CITIZEN,
                is_active=True
            )
            db.add(citizen_user)
            db.commit()
            db.refresh(citizen_user)

        citizen_prof = db.query(Citizen).filter(Citizen.user_id == citizen_user.id).first()
        if not citizen_prof:
            citizen_prof = Citizen(
                user_id=citizen_user.id,
                address="Flat 402, Green Park Apartments, Sector 12",
                latitude=28.6139,
                longitude=77.2090,
                preferred_notification_channels="email,push"
            )
            db.add(citizen_prof)
            db.commit()
            db.refresh(citizen_prof)

        # 2. Setup an admin user
        admin_user = db.query(User).filter(User.email == "test_admin@jansewa.org").first()
        if not admin_user:
            admin_user = User(
                email="test_admin@jansewa.org",
                phone="+919876500001",
                password_hash=get_password_hash("admin123"),
                full_name="Super Admin",
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

        # 3. Setup a department user
        dept_user = db.query(User).filter(User.email == "test_dept@jansewa.org").first()
        if not dept_user:
            dept_user = User(
                email="test_dept@jansewa.org",
                phone="+919876500002",
                password_hash=get_password_hash("dept123"),
                full_name="Water Department Officer",
                role=UserRole.DEPARTMENT,
                is_active=True
            )
            db.add(dept_user)
            db.commit()
            db.refresh(dept_user)

        dept_obj = db.query(Department).filter(Department.name == "water_dept").first()
        if not dept_obj:
            dept_obj = Department(
                name="water_dept",
                display_name="Water Supply & Sanitation",
                user_id=dept_user.id,
                email="water@city.gov"
            )
            db.add(dept_obj)
            db.commit()
            db.refresh(dept_obj)

        dept_admin_prof = db.query(Admin).filter(Admin.user_id == dept_user.id).first()
        if not dept_admin_prof:
            dept_admin_prof = Admin(user_id=dept_user.id, department_id=dept_obj.id, permissions="department")
            db.add(dept_admin_prof)
            db.commit()

        # 4. Setup a different citizen user (privacy test)
        other_citizen = db.query(User).filter(User.email == "other_citizen@jansewa.org").first()
        if not other_citizen:
            other_citizen = User(
                email="other_citizen@jansewa.org",
                phone="+919876500003",
                password_hash=get_password_hash("password123"),
                full_name="Other Citizen",
                role=UserRole.CITIZEN,
                is_active=True
            )
            db.add(other_citizen)
            db.commit()
            db.refresh(other_citizen)

        other_prof = db.query(Citizen).filter(Citizen.user_id == other_citizen.id).first()
        if not other_prof:
            other_prof = Citizen(
                user_id=other_citizen.id,
                address="Sector 14, City Area",
                latitude=28.6145,
                longitude=77.2095
            )
            db.add(other_prof)
            db.commit()
            db.refresh(other_prof)

        # 5. Setup Category & Complaint
        category = db.query(Category).first()
        if not category:
            category = Category(
                name="water_leakage",
                display_name="Water Leakage",
                department_id=dept_obj.id
            )
            db.add(category)
            db.commit()
            db.refresh(category)

        complaint = Complaint(
            citizen_id=citizen_prof.id,
            category_id=category.id,
            department_id=dept_obj.id,
            location="Connaught Place Outer Circle, New Delhi",
            latitude=28.6315,
            longitude=77.2167,
            description="Major pipeline burst causing severe road waterlogging",
            status=ComplaintStatus.PENDING
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        complaint_id = complaint.id

        # Generate tokens
        admin_token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role.value})
        dept_token = create_access_token({"sub": str(dept_user.id), "role": dept_user.role.value})
        other_token = create_access_token({"sub": str(other_citizen.id), "role": other_citizen.role.value})
        author_token = create_access_token({"sub": str(citizen_user.id), "role": citizen_user.role.value})

        # --- TEST 1: Admin access to complaint details ---
        res = client.get(f"/api/complaints/{complaint_id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Admin get complaint failed: {res.text}"
        data = res.json()
        assert "applicant" in data, "Applicant field missing from response"
        assert data["applicant"] is not None, "Applicant should not be None for Admin"
        assert data["applicant"]["full_name"] == "Rajesh Sharma"
        assert data["applicant"]["email"] == "test_applicant@jansewa.org"
        assert data["applicant"]["phone"] == "+919876543210"
        assert "Green Park Apartments" in data["applicant"]["address"]
        print("[PASS] Test 1: Admin sees applicant details on GET /api/complaints/{id}")

        # --- TEST 2: Department Admin access to complaint details ---
        res = client.get(f"/api/complaints/{complaint_id}", headers={"Authorization": f"Bearer {dept_token}"})
        assert res.status_code == 200, f"Dept get complaint failed: {res.text}"
        data = res.json()
        assert data["applicant"] is not None, "Applicant should not be None for Department Admin"
        assert data["applicant"]["full_name"] == "Rajesh Sharma"
        assert data["applicant"]["email"] == "test_applicant@jansewa.org"
        assert data["applicant"]["phone"] == "+919876543210"
        print("[PASS] Test 2: Department Admin sees applicant details on GET /api/complaints/{id}")

        # --- TEST 3: Admin dedicated applicant endpoint ---
        res = client.get(f"/api/admin/complaints/{complaint_id}/applicant", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        app_data = res.json()
        assert app_data["full_name"] == "Rajesh Sharma"
        assert app_data["email"] == "test_applicant@jansewa.org"
        print("[PASS] Test 3: Admin gets applicant details via /api/admin/complaints/{id}/applicant")

        # --- TEST 4: Department Admin dedicated applicant endpoint ---
        res = client.get(f"/api/admin/complaints/{complaint_id}/applicant", headers={"Authorization": f"Bearer {dept_token}"})
        assert res.status_code == 200
        app_data = res.json()
        assert app_data["full_name"] == "Rajesh Sharma"
        print("[PASS] Test 4: Department Admin gets applicant details via /api/admin/complaints/{id}/applicant")

        # --- TEST 5: Complaint applicant endpoint /api/complaints/{id}/applicant ---
        res = client.get(f"/api/complaints/{complaint_id}/applicant", headers={"Authorization": f"Bearer {dept_token}"})
        assert res.status_code == 200
        assert res.json()["full_name"] == "Rajesh Sharma"
        print("[PASS] Test 5: Department Admin gets applicant details via /api/complaints/{id}/applicant")

        # --- TEST 6: Author citizen gets their own details ---
        res = client.get(f"/api/complaints/{complaint_id}", headers={"Authorization": f"Bearer {author_token}"})
        assert res.status_code == 200
        assert res.json()["applicant"] is not None
        assert res.json()["applicant"]["full_name"] == "Rajesh Sharma"
        print("[PASS] Test 6: Complaint Author sees their applicant details")

        # --- TEST 7: Privacy test - Other citizen cannot see applicant details ---
        res = client.get(f"/api/complaints/{complaint_id}", headers={"Authorization": f"Bearer {other_token}"})
        assert res.status_code == 200
        # For other citizens, applicant MUST be None to protect privacy!
        assert res.json().get("applicant") is None, "Privacy leak: Other citizen should NOT see applicant details!"
        print("[PASS] Test 7: Privacy enforced: Other citizen cannot see applicant private contact details")

        # --- TEST 8: Other citizen blocked from direct applicant endpoint ---
        res = client.get(f"/api/complaints/{complaint_id}/applicant", headers={"Authorization": f"Bearer {other_token}"})
        assert res.status_code == 403, "Other citizen should be forbidden from accessing applicant endpoint"
        print("[PASS] Test 8: Privacy enforced: Other citizen gets 403 on /api/complaints/{id}/applicant")

        # --- TEST 9: Admin complaint list includes applicant ---
        res = client.get("/api/admin/complaints", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        comps = res.json()["complaints"]
        matching = [c for c in comps if c["id"] == complaint_id]
        assert len(matching) > 0
        assert matching[0]["applicant"] is not None
        assert matching[0]["applicant"]["full_name"] == "Rajesh Sharma"
        print("[PASS] Test 9: Admin complaint list includes applicant details")

        print("\nALL 9 APPLICANT ACCESS & PRIVACY TESTS PASSED SUCCESSFULLY!")
        return True

    finally:
        db.close()

if __name__ == "__main__":
    test_applicant_visibility_admin_and_department()
