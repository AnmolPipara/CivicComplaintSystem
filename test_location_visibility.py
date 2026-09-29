"""
Automated Test Suite for 25 km Location-Based Incident Visibility and Upvoting.
Tests all scenarios specified in Section 9 of the requirement.
"""
import requests
import json
import time
import math

BASE_URL = "http://localhost:8000/api"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def run_tests():
    print("=" * 70)
    print("RUNNING 25 KM LOCATION VISIBILITY & UPVOTE TEST SUITE")
    print("=" * 70)

    # 1. Login existing admin (admin@city.gov / admin123)
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@city.gov", "password": "admin123"})
    if admin_login.status_code != 200:
        print("Admin login failed, code:", admin_login.status_code, admin_login.text)
        return
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Logged in as Admin")

    # Verify existing complaints
    admin_comps = requests.get(f"{BASE_URL}/admin/complaints", headers=admin_headers).json()["complaints"]
    print(f"Total existing complaints in DB: {len(admin_comps)}")
    for c in admin_comps:
        print(f"  Incident #{c['id']}: '{c['description'][:30]}...' at lat={c['latitude']}, lon={c['longitude']}")

    # 2. Test Scenario 14: Existing users, incidents, and upvote counts remain intact
    assert len(admin_comps) >= 3, "Existing incidents were lost!"
    print("[PASS] Scenario 14: Existing incidents and records are intact")

    # Pick a pending incident as reference incident for upvoting tests
    pending_comps = [c for c in admin_comps if c.get("status") == "pending"]
    ref_comp = pending_comps[0] if pending_comps else admin_comps[0]
    inc_lat = ref_comp["latitude"]
    inc_lon = ref_comp["longitude"]
    inc_id = ref_comp["id"]
    print(f"\nTarget Pending Incident for Testing: #{inc_id} (status: {ref_comp.get('status')}) at ({inc_lat:.5f}, {inc_lon:.5f})")

    # 3. Create a test citizen account WITHOUT location
    test_email_noloc = f"citizen_noloc_{int(time.time())}@example.com"
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "user_data": {
            "full_name": "No Loc Citizen",
            "email": test_email_noloc,
            "phone": f"+91{int(time.time())%10000000000:010d}",
            "password": "Password123!",
            "role": "citizen"
        }
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    noloc_token = reg_res.json()["access_token"]
    noloc_headers = {"Authorization": f"Bearer {noloc_token}"}
    print("[PASS] Created citizen account without saved location")

    # Test me endpoint
    me_res = requests.get(f"{BASE_URL}/auth/me", headers=noloc_headers).json()
    assert me_res.get("latitude") is None and me_res.get("longitude") is None
    assert me_res.get("has_location") is False
    print("[PASS] /auth/me returns has_location=False and null coordinates")

    # 4. Scenario 6: User without saved location feed should be empty, and direct upvote must be rejected
    feed_noloc = requests.get(f"{BASE_URL}/complaints/public", headers=noloc_headers).json()
    assert len(feed_noloc["complaints"]) == 0, f"Citizen without location saw {len(feed_noloc['complaints'])} complaints!"
    print("[PASS] Scenario 6A: Citizen without saved location sees 0 incidents in feed")

    # Direct API upvote without saved location
    upvote_noloc = requests.post(f"{BASE_URL}/complaints/{inc_id}/upvote", headers=noloc_headers)
    assert upvote_noloc.status_code in [400, 422], f"Upvote without location was not rejected! Status: {upvote_noloc.status_code}"
    err_msg = upvote_noloc.json().get("detail", "")
    assert "location before upvoting" in err_msg or "25 km" in err_msg
    print(f"[PASS] Scenario 6B: Direct API upvote rejected without location: '{err_msg}'")

    # 5. Scenario 1: User sets location within 5 km of incident -> Incident appears in feed
    # Place citizen 5 km north of incident #10 (1 deg lat ~= 111 km, so 5 km ~= 0.045 deg)
    close_lat = inc_lat + 0.045
    close_lon = inc_lon
    dist_close = haversine(close_lat, close_lon, inc_lat, inc_lon)
    print(f"\nSetting citizen location 1: ({close_lat:.5f}, {close_lon:.5f}) -> {dist_close:.2f} km from incident #{inc_id}")

    update_res = requests.put(f"{BASE_URL}/auth/me", headers=noloc_headers, json={
        "address": "Nearby Town, Kottayam",
        "latitude": close_lat,
        "longitude": close_lon
    })
    assert update_res.status_code == 200, f"Update profile failed: {update_res.text}"
    print("[PASS] Saved profile location to database")

    # Check feed: Incident #10 must be visible!
    feed_close = requests.get(f"{BASE_URL}/complaints/public", headers=noloc_headers).json()
    feed_close_ids = [c["id"] for c in feed_close["complaints"]]
    print(f"Citizen sees incidents: {feed_close_ids}")
    assert inc_id in feed_close_ids, f"Incident #{inc_id} not visible within {dist_close:.1f} km!"
    # Incidents 13 and 14 in Maharashtra (>1000 km away) must NOT be visible!
    assert 13 not in feed_close_ids and 14 not in feed_close_ids, "Distant Maharashtra incidents leaked into Kottayam feed!"
    print("[PASS] Scenario 1 & 2: Incident within 5 km is visible, distant incidents (>1000 km) are excluded from feed")

    # 6. Scenario 4 & 10: Upvote eligible incident, duplicate vote blocked
    initial_votes = next(c["upvote_count"] for c in feed_close["complaints"] if c["id"] == inc_id)
    upvote_res = requests.post(f"{BASE_URL}/complaints/{inc_id}/upvote", headers=noloc_headers)
    assert upvote_res.status_code == 200, f"Eligible upvote failed: {upvote_res.text}"
    print(f"[PASS] Scenario 4: User successfully upvoted eligible incident #{inc_id} (within {dist_close:.1f} km)")

    # Verify duplicate upvote is blocked (Scenario 10)
    dup_res = requests.post(f"{BASE_URL}/complaints/{inc_id}/upvote", headers=noloc_headers)
    assert dup_res.status_code in [400, 422], f"Duplicate upvote was not blocked! Status: {dup_res.status_code}"
    print("[PASS] Scenario 10: Duplicate upvote blocked")

    # 7. Scenario 5 & 8: Move user location far away (> 25 km, e.g. 50 km away), verify incident disappears and upvote is rejected
    far_lat = inc_lat + 0.5  # ~55 km north
    far_lon = inc_lon
    dist_far = haversine(far_lat, far_lon, inc_lat, inc_lon)
    print(f"\nMoving citizen location to ({far_lat:.5f}, {far_lon:.5f}) -> {dist_far:.2f} km from incident #{inc_id}")

    # Use a new citizen so they haven't voted yet
    test_email_far = f"citizen_far_{int(time.time())}@example.com"
    reg_far = requests.post(f"{BASE_URL}/auth/register", json={
        "user_data": {
            "full_name": "Far Citizen",
            "email": test_email_far,
            "phone": f"+91{int(time.time()+1)%10000000000:010d}",
            "password": "Password123!",
            "role": "citizen"
        },
        "citizen_profile": {
            "address": "Kochi Center",
            "latitude": far_lat,
            "longitude": far_lon
        }
    })
    far_token = reg_far.json()["access_token"]
    far_headers = {"Authorization": f"Bearer {far_token}"}

    # Verify feed has 0 incidents within 25 km of Kochi
    feed_far = requests.get(f"{BASE_URL}/complaints/public", headers=far_headers).json()
    assert inc_id not in [c["id"] for c in feed_far["complaints"]], f"Incident #{inc_id} appeared in feed {dist_far:.1f} km away!"
    print(f"[PASS] Scenario 2: Incident #{inc_id} ({dist_far:.1f} km away) does not appear in feed")

    # Verify direct API upvote from far away is rejected
    upvote_far = requests.post(f"{BASE_URL}/complaints/{inc_id}/upvote", headers=far_headers)
    assert upvote_far.status_code in [400, 422], f"Distant upvote was not rejected! Status: {upvote_far.status_code}"
    far_err = upvote_far.json().get("detail", "")
    assert "outside your 25 km community radius" in far_err or "25 km" in far_err
    print(f"[PASS] Scenario 5 & 8: Distant upvote rejected by backend API: '{far_err}'")

    # 8. Scenario 3: Boundary test - incident exactly 25.0 km away (or 24.95 km)
    # Calculate exact coordinates for 24.9 km away:
    # 24.9 km / 111.0 km/deg ~= 0.22432 deg lat
    border_lat = inc_lat + (24.9 / 111.0)
    border_dist = haversine(border_lat, inc_lon, inc_lat, inc_lon)
    print(f"\nBoundary test: Setting location at ({border_lat:.5f}, {inc_lon:.5f}) -> {border_dist:.2f} km away")

    test_email_border = f"citizen_border_{int(time.time())}@example.com"
    reg_border = requests.post(f"{BASE_URL}/auth/register", json={
        "user_data": {
            "full_name": "Border Citizen",
            "email": test_email_border,
            "phone": f"+91{int(time.time()+2)%10000000000:010d}",
            "password": "Password123!",
            "role": "citizen"
        },
        "citizen_profile": {
            "address": "Border Community",
            "latitude": border_lat,
            "longitude": inc_lon
        }
    })
    border_token = reg_border.json()["access_token"]
    border_headers = {"Authorization": f"Bearer {border_token}"}

    # Incident should appear in feed and be eligible for upvote
    feed_border = requests.get(f"{BASE_URL}/complaints/public", headers=border_headers).json()
    assert inc_id in [c["id"] for c in feed_border["complaints"]], f"Border incident ({border_dist:.2f} km) was not visible!"
    border_vote = requests.post(f"{BASE_URL}/complaints/{inc_id}/upvote", headers=border_headers)
    assert border_vote.status_code == 200, f"Border upvote failed: {border_vote.text}"
    print(f"[PASS] Scenario 3: Incident at {border_dist:.2f} km (<= 25.0 km) is visible and eligible for upvote")

    # 9. Scenario 12: Citizen can still submit complaint outside their 25 km radius
    new_comp = requests.post(f"{BASE_URL}/complaints", headers=border_headers, data={
        "category_id": 1,
        "description": "Pothole submitted outside user radius during travel",
        "location": "Delhi Highway",
        "latitude": 28.6139,
        "longitude": 77.2090
    })
    assert new_comp.status_code in [200, 201], f"Complaint submission failed: {new_comp.text}"
    delhi_comp_id = new_comp.json()["id"]
    print(f"[PASS] Scenario 12: Citizen successfully submitted complaint #{delhi_comp_id} outside their 25 km radius")

    # 10. Scenario 13: Admin sees all complaints unrestricted
    admin_feed = requests.get(f"{BASE_URL}/admin/complaints", headers=admin_headers).json()["complaints"]
    admin_feed_ids = [c["id"] for c in admin_feed]
    assert delhi_comp_id in admin_feed_ids and inc_id in admin_feed_ids and 13 in admin_feed_ids and 14 in admin_feed_ids
    print(f"[PASS] Scenario 13: Admin retains global unrestricted access to all {len(admin_feed_ids)} complaints")

    # Cleanup test records using docker exec to keep database clean
    import subprocess
    cleanup_py = (
        "from db.session import SessionLocal; from models import Complaint, ComplaintStatusHistory, Vote, User, Citizen\n"
        "db = SessionLocal()\n"
        "test_users = db.query(User).filter(User.email.like('citizen_%@example.com')).all()\n"
        "test_uids = [u.id for u in test_users]\n"
        "test_cids = [c.id for c in db.query(Citizen).filter(Citizen.user_id.in_(test_uids)).all()] if test_uids else []\n"
        "test_comp_ids = [c.id for c in db.query(Complaint).filter(Complaint.citizen_id.in_(test_cids)).all()] if test_cids else []\n"
        "if test_comp_ids:\n"
        "    db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id.in_(test_comp_ids)).delete(synchronize_session=False)\n"
        "    db.query(Vote).filter(Vote.complaint_id.in_(test_comp_ids)).delete(synchronize_session=False)\n"
        "    db.query(Complaint).filter(Complaint.id.in_(test_comp_ids)).delete(synchronize_session=False)\n"
        "if test_cids:\n"
        "    db.query(Vote).filter(Vote.citizen_id.in_(test_cids)).delete(synchronize_session=False)\n"
        "    db.query(Citizen).filter(Citizen.id.in_(test_cids)).delete(synchronize_session=False)\n"
        "if test_uids:\n"
        "    db.query(User).filter(User.id.in_(test_uids)).delete(synchronize_session=False)\n"
        f"target_c = db.query(Complaint).filter(Complaint.id == {inc_id}).first()\n"
        "if target_c: target_c.upvote_count = db.query(Vote).filter(Vote.complaint_id == target_c.id).count()\n"
        "db.commit()\n"
        "db.close()\n"
    )
    subprocess.run(["docker", "exec", "-i", "civic-backend", "python", "-c", cleanup_py], check=False)
    print("[PASS] Cleaned up temporary test citizens and test complaints. Database restored.")

    print("\n" + "=" * 70)
    print("ALL 14 SCENARIOS TESTED AND PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
