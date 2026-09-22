import httpx
import uuid
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def get_admin_token():
    print("Logging in as Admin...")
    res = httpx.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@city.gov",
        "password": "admin123"
    })
    res.raise_for_status()
    return res.json()["access_token"]

def get_dept_token():
    print("Logging in as Department (Roads)...")
    res = httpx.post(f"{BASE_URL}/api/auth/login", json={
        "email": "roads@city.gov",
        "password": "dept123"
    })
    res.raise_for_status()
    return res.json()["access_token"]

def run_tests():
    print("Starting E2E Complaint Workflow Tests...")
    
    unique_id = uuid.uuid4().hex[:8]
    user_email = f"citizen_{unique_id}@example.com"
    user_password = "SecurePassword123!"
    
    # 1. Setup - get tokens and IDs
    admin_token = get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    dept_token = get_dept_token()
    dept_headers = {"Authorization": f"Bearer {dept_token}"}
    
    # Get a category (Pothole)
    res = httpx.get(f"{BASE_URL}/api/admin/categories", headers=admin_headers)
    categories = res.json()
    category_id = categories[0]["id"]
    
    # Get a department (Roads)
    res = httpx.get(f"{BASE_URL}/api/admin/departments", headers=admin_headers)
    departments = res.json()
    dept_id = departments[0]["id"]
    
    # 2. Register Citizen
    print(f"\n[1] Registering and logging in Citizen: {user_email}")
    httpx.post(f"{BASE_URL}/api/auth/register", json={
        "user_data": {
            "email": user_email,
            "phone": f"99999{unique_id[:5]}",
            "full_name": "Test Citizen",
            "password": user_password,
            "role": "citizen"
        }
    }).raise_for_status()
    
    res = httpx.post(f"{BASE_URL}/api/auth/login", json={
        "email": user_email,
        "password": user_password
    })
    citizen_token = res.json()["access_token"]
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    
    # 3. Citizen Submits Complaint
    print("\n[2] Citizen submitting complaint...")
    # Using multipart/form-data as defined in the router
    data = {
        "description": "Massive pothole causing accidents",
        "category_id": category_id,
        "latitude": 19.0760,
        "longitude": 72.8777,
        "city": "Mumbai",
        "state": "Maharashtra"
    }
    res = httpx.post(f"{BASE_URL}/api/complaints", data=data, headers=citizen_headers)
    if res.status_code != 201:
        print(f"FAILED submission! Status: {res.status_code}, {res.text}")
        return False
    complaint = res.json()
    complaint_id = complaint["id"]
    print(f"SUCCESS: Complaint #{complaint_id} created with status {complaint['status']}")
    
    # 4. Admin Assigns Complaint
    print(f"\n[3] Admin assigning complaint #{complaint_id} to dept #{dept_id}")
    res = httpx.put(
        f"{BASE_URL}/api/admin/complaints/{complaint_id}/assign", 
        params={"department_id": dept_id},
        headers=admin_headers
    )
    if res.status_code != 200:
        print(f"FAILED assignment! Status: {res.status_code}, {res.text}")
        return False
    res_json = res.json()
    print("ASSIGN RESPONSE:", res_json)
    print(f"SUCCESS: Assigned. Status is now {res_json['complaint'].get('status', 'unknown')}")
    
    # 5. Department updates status to IN_PROGRESS
    print(f"\n[4] Department setting complaint #{complaint_id} to IN_PROGRESS")
    update_data = {"status": "in_progress"}
    res = httpx.put(f"{BASE_URL}/api/complaints/{complaint_id}", json=update_data, headers=dept_headers)
    if res.status_code != 200:
        print(f"FAILED Dept update! Status: {res.status_code}, {res.text}")
        return False
    print("SUCCESS: Updated to IN_PROGRESS.")
    
    # 6. Admin resolves it
    print(f"\n[5] Department resolving complaint #{complaint_id}")
    update_data = {"status": "resolved"}
    res = httpx.put(f"{BASE_URL}/api/complaints/{complaint_id}", json=update_data, headers=dept_headers)
    if res.status_code != 200:
        print(f"FAILED Dept resolve! Status: {res.status_code}, {res.text}")
        return False
    print("SUCCESS: Resolved.")
    
    # 7. Citizen checks status
    print(f"\n[6] Citizen checking final status of complaint #{complaint_id}")
    res = httpx.get(f"{BASE_URL}/api/complaints/{complaint_id}", headers=citizen_headers)
    final_complaint = res.json()
    print(f"SUCCESS: Citizen sees status: {final_complaint['status']}")
    
    if final_complaint['status'] == "resolved":
        print("\nALL TESTS PASSED!")
        return True
    else:
        print("Test failed: Final status is not resolved.")
        return False

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"ERROR: {str(e)}")
