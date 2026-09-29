"""
Automated Test for Citizen Email Notifications:
1. Complaint Registered
2. Complaint Started Working
3. Complaint Completed
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("=" * 70)
    print("TESTING CITIZEN EMAIL NOTIFICATIONS (REGISTERED, WORKING, COMPLETED)")
    print("=" * 70)

    # 1. Admin login
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@city.gov", "password": "admin123"})
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Logged in as Admin")

    # 2. Register a new test citizen with a unique citizen email
    timestamp_id = int(time.time())
    citizen_email = f"citizen_mail_{timestamp_id}@example.com"
    citizen_name = f"Citizen Mail Tester {timestamp_id}"
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "user_data": {
            "full_name": citizen_name,
            "email": citizen_email,
            "phone": f"+91{timestamp_id%10000000000:010d}",
            "password": "Password123!",
            "role": "citizen"
        },
        "citizen_profile": {
            "address": "Kottayam Central",
            "latitude": 9.7554,
            "longitude": 76.6500
        }
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    citizen_token = reg_res.json()["access_token"]
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    print(f"[PASS] Registered citizen: {citizen_name} ({citizen_email})")

    # 3. Step 1: Citizen submits a complaint -> Triggers "registered" email
    print("\n--- STEP 1: COMPLAINT REGISTRATION ---")
    create_res = requests.post(f"{BASE_URL}/complaints", headers=citizen_headers, data={
        "category_id": 1,
        "description": "Streetlight flickering and broken near hospital gate",
        "location": "Civil Hospital Road, Ward 4",
        "latitude": 9.7560,
        "longitude": 76.6510
    })
    assert create_res.status_code in [200, 201], f"Complaint creation failed: {create_res.text}"
    complaint_data = create_res.json()
    complaint_id = complaint_data["id"]
    print(f"[PASS] Created complaint #{complaint_id} with status '{complaint_data['status']}'")

    # Allow background task to process
    time.sleep(1)

    # Check email notifications log via admin API
    emails_res = requests.get(f"{BASE_URL}/admin/notifications/emails", headers=admin_headers)
    assert emails_res.status_code == 200, f"Failed to get email logs: {emails_res.text}"
    emails = emails_res.json()["emails"]
    
    reg_email = next((e for e in emails if e["complaint_id"] == complaint_id and e["event_type"] == "registered"), None)
    assert reg_email is not None, f"Registered email not found for complaint #{complaint_id} in {emails}!"
    assert reg_email["recipient_email"] == citizen_email
    assert "Complaint Registered" in reg_email["subject"]
    print(f"[PASS] Email 1 Sent on Registration:")
    print(f"       To: {reg_email['recipient_email']}")
    print(f"       Subject: {reg_email['subject']}")
    print(f"       Delivery Mode: {reg_email['delivered_via']}")

    # 4. Step 2: Admin updates complaint status to "working" -> Triggers "working" email
    print("\n--- STEP 2: STATUS UPDATED TO 'WORKING' ---")
    work_res = requests.put(f"{BASE_URL}/complaints/{complaint_id}", headers=admin_headers, json={"status": "working"})
    assert work_res.status_code == 200, f"Status update to working failed: {work_res.text}"
    assert work_res.json()["status"] == "working"
    print(f"[PASS] Updated complaint #{complaint_id} status to 'working'")

    time.sleep(1)

    emails_res2 = requests.get(f"{BASE_URL}/admin/notifications/emails", headers=admin_headers)
    emails2 = emails_res2.json()["emails"]
    work_email = next((e for e in emails2 if e["complaint_id"] == complaint_id and e["event_type"] == "working"), None)
    assert work_email is not None, f"Work In Progress email not found for complaint #{complaint_id}!"
    assert work_email["recipient_email"] == citizen_email
    assert "Work Started" in work_email["subject"] or "Working" in work_email["subject"]
    print(f"[PASS] Email 2 Sent on Work Started:")
    print(f"       To: {work_email['recipient_email']}")
    print(f"       Subject: {work_email['subject']}")
    print(f"       Delivery Mode: {work_email['delivered_via']}")

    # 5. Step 3: Admin updates complaint status to "completed" -> Triggers "completed" email
    print("\n--- STEP 3: STATUS UPDATED TO 'COMPLETED' ---")
    comp_res = requests.put(f"{BASE_URL}/complaints/{complaint_id}", headers=admin_headers, json={"status": "completed"})
    assert comp_res.status_code == 200, f"Status update to completed failed: {comp_res.text}"
    assert comp_res.json()["status"] == "completed"
    print(f"[PASS] Updated complaint #{complaint_id} status to 'completed'")

    time.sleep(1)

    emails_res3 = requests.get(f"{BASE_URL}/admin/notifications/emails", headers=admin_headers)
    emails3 = emails_res3.json()["emails"]
    comp_email = next((e for e in emails3 if e["complaint_id"] == complaint_id and e["event_type"] == "completed"), None)
    assert comp_email is not None, f"Completed email not found for complaint #{complaint_id}!"
    assert comp_email["recipient_email"] == citizen_email
    assert "Resolved" in comp_email["subject"] or "Completed" in comp_email["subject"]
    print(f"[PASS] Email 3 Sent on Resolution / Completion:")
    print(f"       To: {comp_email['recipient_email']}")
    print(f"       Subject: {comp_email['subject']}")
    print(f"       Delivery Mode: {comp_email['delivered_via']}")

    # 6. Clean up the test complaint and test citizen account
    import subprocess
    cleanup_py = (
        "from db.session import SessionLocal; from models import Complaint, ComplaintStatusHistory, Vote, User, Citizen\n"
        "db = SessionLocal()\n"
        f"db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id == {complaint_id}).delete(synchronize_session=False)\n"
        f"db.query(Vote).filter(Vote.complaint_id == {complaint_id}).delete(synchronize_session=False)\n"
        f"db.query(Complaint).filter(Complaint.id == {complaint_id}).delete(synchronize_session=False)\n"
        f"u = db.query(User).filter(User.email == '{citizen_email}').first()\n"
        "if u:\n"
        "    db.query(Citizen).filter(Citizen.user_id == u.id).delete(synchronize_session=False)\n"
        "    db.delete(u)\n"
        "db.commit()\n"
        "db.close()\n"
    )
    subprocess.run(["docker", "exec", "-i", "civic-backend", "python", "-c", cleanup_py], check=False)
    print(f"[PASS] Cleaned up temporary test complaint #{complaint_id} and user '{citizen_email}'")

    print("\n" + "=" * 70)
    print("ALL 3 EMAIL NOTIFICATION WORKFLOWS TESTED AND PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
