import requests
import random
import os

BASE_URL = "http://localhost:8000/api"
r = random.randint(1000, 9999)

def login(email, password):
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def register(email, role="citizen"):
    data = {
        "email": email,
        "password": "password123",
        "full_name": f"{role} User",
        "role": role,
        "phone": str(random.randint(1000000000, 9999999999))
    }
    res = requests.post(f"{BASE_URL}/auth/register", json={"user_data": data})
    if res.status_code in [200, 201]:
        return login(email, "password123")
    return None

print("--- Starting E2E API Test ---")

# 1. Register users
c1_email = f"cit1_{r}@example.com"
c2_email = f"cit2_{r}@example.com"
admin_email = f"adm1_{r}@example.com"
dept_email = f"dep1_{r}@example.com"

c1_token = register(c1_email, "citizen")
c2_token = register(c2_email, "citizen")
admin_token = register(admin_email, "admin")
dept_token = register(dept_email, "department")

if not (c1_token and c2_token and admin_token and dept_token):
    print("Failed to register users.")
    exit(1)

admin_headers = {"Authorization": f"Bearer {admin_token}"}
res = requests.get(f"{BASE_URL}/admin/departments", headers=admin_headers)
depts = res.json()
if not any(d.get('display_name') == 'Public Works' for d in depts):
    requests.post(f"{BASE_URL}/admin/departments", json={"name": f"PW_{r}", "display_name": "Public Works", "description": "Roads"}, headers=admin_headers)
    res = requests.get(f"{BASE_URL}/admin/departments", headers=admin_headers)

dept_id = res.json()[0]['id']

res = requests.get(f"{BASE_URL}/admin/categories", headers=admin_headers)
cats = res.json()
if not cats:
    requests.post(f"{BASE_URL}/admin/categories", json={"name": f"pot_{r}", "display_name": "Potholes", "base_severity": 0.5}, headers=admin_headers)
    res = requests.get(f"{BASE_URL}/admin/categories", headers=admin_headers)
cat_id = res.json()[0]['id']

# Citizen creates complaint (Form data)
c1_headers = {"Authorization": f"Bearer {c1_token}"}
complaint_data = {
    "category_id": str(cat_id),
    "location": "Main Street",
    "description": "Large pothole on the main street"
}
res = requests.post(f"{BASE_URL}/complaints", data=complaint_data, headers=c1_headers)
if res.status_code in [200, 201]:
    print("[PASS] Citizen 1 created complaint")
    comp_id = res.json()["id"]
else:
    print("[FAIL] Citizen 1 failed to create complaint:", res.text)
    exit(1)

c2_headers = {"Authorization": f"Bearer {c2_token}"}
res = requests.post(f"{BASE_URL}/complaints/{comp_id}/upvote", headers=c2_headers)
if res.status_code == 200:
    print("[PASS] Citizen 2 upvoted")
else:
    print("[FAIL] Upvote failed:", res.text)

res = requests.post(f"{BASE_URL}/complaints/{comp_id}/upvote", headers=c2_headers)
if res.status_code == 400:
    print("[PASS] Duplicate upvote rejected")
else:
    print("[FAIL] Duplicate upvote not rejected:", res.status_code)

res = requests.put(f"{BASE_URL}/admin/complaints/{comp_id}/assign", params={"department_id": dept_id}, headers=admin_headers)
if res.status_code == 200:
    print("[PASS] Admin assigned complaint")
else:
    print("[FAIL] Admin assignment failed:", res.text)

# Tie dept_user to dept_id directly in DB via docker exec
me_res = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {dept_token}"})
dept_user_id = me_res.json()["id"]
os.system(f'docker exec civic-postgres psql -U user -d civic_complaints -c "UPDATE admins SET department_id = {dept_id} WHERE user_id = {dept_user_id};"')

dept_headers = {"Authorization": f"Bearer {dept_token}"}
res = requests.put(f"{BASE_URL}/complaints/{comp_id}", json={"status": "working"}, headers=dept_headers)
if res.status_code == 200:
    print("[PASS] Department updated status to WORKING")
else:
    print("[FAIL] Department update failed:", res.text)

res = requests.put(f"{BASE_URL}/complaints/{comp_id}", json={"status": "completed"}, headers=dept_headers)
if res.status_code == 200:
    print("[PASS] Department updated status to COMPLETED")
else:
    print("[FAIL] Department update failed:", res.text)

c1_res = requests.get(f"{BASE_URL}/complaints/{comp_id}", headers=c1_headers)
if c1_res.json()["status"] == "completed":
    print("[PASS] Citizen sees COMPLETED status")
else:
    print("[FAIL] Citizen status is incorrect:", c1_res.json())

# Cleanup: delete the test complaint and votes so it does not pollute the real user feed
os.system(f'docker exec civic-postgres psql -U user -d civic_complaints -c "DELETE FROM votes WHERE complaint_id = {comp_id}; DELETE FROM complaint_status_history WHERE complaint_id = {comp_id}; DELETE FROM complaints WHERE id = {comp_id};"')
print("[PASS] Cleaned up test complaint", comp_id)

print("--- E2E API Test Complete ---")
