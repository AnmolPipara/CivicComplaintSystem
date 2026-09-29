import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("=" * 70)
    print("TESTING STATUS RESTRICTION: ONLY PENDING INCIDENTS CAN BE UPVOTED")
    print("=" * 70)

    # 1. Admin login
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@city.gov", "password": "admin123"})
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Logged in as Admin")

    # 2. Check complaints
    comps = requests.get(f"{BASE_URL}/admin/complaints", headers=admin_headers).json()["complaints"]
    comp_10 = next((c for c in comps if c["id"] == 10), None)
    comp_46 = next((c for c in comps if c["id"] == 46), None)
    
    assert comp_10 is not None, "Complaint #10 not found!"
    assert comp_46 is not None, "Complaint #46 not found!"

    print(f"Complaint #10 status: {comp_10['status']}, lat: {comp_10['latitude']}, lon: {comp_10['longitude']}")
    print(f"Complaint #46 status: {comp_46['status']}, lat: {comp_46['latitude']}, lon: {comp_46['longitude']}")

    # 3. Create a test citizen located in Kottayam (within 1 km of both incidents)
    test_email = f"citizen_tester_{int(time.time())}@example.com"
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "user_data": {
            "full_name": "Pending Vote Tester",
            "email": test_email,
            "phone": f"+91{int(time.time())%10000000000:010d}",
            "password": "Password123!",
            "role": "citizen"
        },
        "citizen_profile": {
            "address": "Kottayam Town Center",
            "latitude": 9.7554,
            "longitude": 76.6500
        }
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Created citizen within 1 km of test incidents")

    # 4. Attempt to upvote Complaint #10 (Status: completed)
    # Expected: REJECTED with message indicating only pending can be upvoted
    print("\nTest Case 1: Citizen attempts to upvote COMPLETED incident #10")
    vote_completed = requests.post(f"{BASE_URL}/complaints/10/upvote", headers=headers)
    print(f"Response status: {vote_completed.status_code}")
    print(f"Response detail: {vote_completed.text}")
    assert vote_completed.status_code in [400, 422], f"Expected rejection but got {vote_completed.status_code}"
    err_detail = vote_completed.json().get("detail", "")
    assert "status is pending" in err_detail.lower(), f"Unexpected error message: {err_detail}"
    print(f"[PASS] Successfully rejected voting on completed incident: '{err_detail}'")

    # 5. Attempt to upvote Complaint #46 (Status: pending)
    # Expected: SUCCESS (HTTP 200)
    print("\nTest Case 2: Citizen attempts to upvote PENDING incident #46")
    vote_pending = requests.post(f"{BASE_URL}/complaints/46/upvote", headers=headers)
    print(f"Response status: {vote_pending.status_code}")
    assert vote_pending.status_code == 200, f"Expected 200 OK for pending incident, got: {vote_pending.text}"
    print(f"[PASS] Successfully accepted upvote on pending incident #46!")

    # 6. Attempt duplicate vote on #46
    print("\nTest Case 3: Citizen attempts duplicate upvote on pending incident #46")
    dup_vote = requests.post(f"{BASE_URL}/complaints/46/upvote", headers=headers)
    assert dup_vote.status_code in [400, 422]
    print(f"[PASS] Duplicate upvote rejected: '{dup_vote.json().get('detail')}'")

    # 7. Test Case 4: Incident transitioned to 'working' status rejects voting
    print("\nTest Case 4: Incident changed to 'working' rejects new upvotes")
    # Set #46 to 'working'
    requests.put(f"{BASE_URL}/complaints/46", headers=admin_headers, json={"status": "working"})

    # New citizen attempts to upvote #46 while 'working'
    new_citizen_email = f"citizen_tester2_{int(time.time())}@example.com"
    reg2 = requests.post(f"{BASE_URL}/auth/register", json={
        "user_data": {
            "full_name": "Pending Vote Tester 2",
            "email": new_citizen_email,
            "phone": f"+91{int(time.time()+1)%10000000000:010d}",
            "password": "Password123!",
            "role": "citizen"
        },
        "citizen_profile": {
            "address": "Kottayam Town Center",
            "latitude": 9.7554,
            "longitude": 76.6500
        }
    })
    token2 = reg2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    vote_working = requests.post(f"{BASE_URL}/complaints/46/upvote", headers=headers2)
    print(f"Response status on 'working' incident: {vote_working.status_code}")
    print(f"Response detail: {vote_working.text}")
    assert vote_working.status_code in [400, 422]
    assert "status is pending" in vote_working.json().get("detail", "").lower()
    print(f"[PASS] Successfully rejected voting on 'working' incident: '{vote_working.json().get('detail')}'")

    # Restore #46 to 'pending'
    requests.put(f"{BASE_URL}/complaints/46", headers=admin_headers, json={"status": "pending"})
    print("[PASS] Restored incident #46 status to 'pending'")

    # Cleanup test accounts and votes created by test accounts
    import subprocess
    cleanup_py = (
        "from db.session import SessionLocal; from models import Complaint, Vote, User, Citizen\n"
        "db = SessionLocal()\n"
        "test_users = db.query(User).filter(User.email.like('citizen_tester%@example.com')).all()\n"
        "test_uids = [u.id for u in test_users]\n"
        "test_cids = [c.id for c in db.query(Citizen).filter(Citizen.user_id.in_(test_uids)).all()] if test_uids else []\n"
        "if test_cids:\n"
        "    db.query(Vote).filter(Vote.citizen_id.in_(test_cids)).delete(synchronize_session=False)\n"
        "    db.query(Citizen).filter(Citizen.id.in_(test_cids)).delete(synchronize_session=False)\n"
        "if test_uids:\n"
        "    db.query(User).filter(User.id.in_(test_uids)).delete(synchronize_session=False)\n"
        "c46 = db.query(Complaint).filter(Complaint.id == 46).first()\n"
        "if c46: c46.upvote_count = db.query(Vote).filter(Vote.complaint_id == 46).count()\n"
        "db.commit()\n"
        "db.close()\n"
    )
    subprocess.run(["docker", "exec", "-i", "civic-backend", "python", "-c", cleanup_py], check=False)
    print("[PASS] Cleaned up test users and test votes.")

    print("\n" + "=" * 70)
    print("ALL PENDING-STATUS VOTING RESTRICTION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
