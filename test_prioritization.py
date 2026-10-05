import requests
import random
import os
import math
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://localhost:8000/api"
r = random.randint(10000, 99999)

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

def run_tests():
    print("=================================================================")
    print("=== Comprehensive Civic Complaint Prioritization Test Suite ===")
    print("=================================================================")
    
    # 1. Setup Auth
    c1_token = register(f"cit1_{r}@test.com", "citizen")
    c2_token = register(f"cit2_{r}@test.com", "citizen")
    adm_token = register(f"adm_{r}@test.com", "admin")
    
    assert c1_token, "Failed to register citizen 1"
    assert c2_token, "Failed to register citizen 2"
    assert adm_token, "Failed to register admin"
    
    c1_headers = {"Authorization": f"Bearer {c1_token}"}
    c2_headers = {"Authorization": f"Bearer {c2_token}"}
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    # Set community location for 25km distance check in upvoting
    requests.put(f"{BASE_URL}/auth/profile", json={"address": "Connaught Place, Delhi", "latitude": 28.6315, "longitude": 77.2167}, headers=c1_headers)
    requests.put(f"{BASE_URL}/auth/profile", json={"address": "Connaught Place, Delhi", "latitude": 28.6320, "longitude": 77.2170}, headers=c2_headers)
    
    # Get categories
    res = requests.get(f"{BASE_URL}/admin/categories", headers=adm_headers)
    assert res.status_code == 200
    cats = res.json()
    pothole_cat = next((c for c in cats if "pothole" in c["name"].lower() or "pot" in c["name"].lower()), cats[0])
    sewage_cat = next((c for c in cats if "sewage" in c["name"].lower()), cats[0])
    garbage_cat = next((c for c in cats if "garbage" in c["name"].lower() or "waste" in c["name"].lower()), cats[0])
    traffic_cat = next((c for c in cats if "traffic" in c["name"].lower() or "electric" in c["name"].lower()), cats[0])
    
    created_ids = []
    
    try:
        # TEST 1: Vague Pothole Baseline
        print("\n--- Test 1: Vague Description & Category Baseline (Road Pothole) ---")
        pothole_data = {
            "description": "pothole",
            "category_id": str(pothole_cat["id"]),
            "location": "Sector 4 Main Road",
            "latitude": "28.6318",
            "longitude": "77.2168"
        }
        res1 = requests.post(f"{BASE_URL}/complaints", data=pothole_data, headers=c1_headers)
        assert res1.status_code == 201, f"Failed: {res1.text}"
        comp1 = res1.json()
        created_ids.append(comp1["id"])
        
        print(f"Created #{comp1['id']}: Vague pothole")
        print(f"  Severity: {comp1['severity_score']} (Baseline: 40)")
        print(f"  Impact: {comp1['impact_score']} (Baseline: 35)")
        print(f"  Urgency: {comp1['urgency_score']} (Baseline: 35)")
        print(f"  Priority Score: {comp1['priority_score']}")
        print(f"  Needs Review: {comp1['needs_human_review']}")
        print(f"  Confidence: {comp1['assessment_confidence']}")
        print(f"  Reason: {comp1['assessment_reason']}")
        
        # Verify 0-100 range and vague pothole small-to-medium baseline
        assert 0 <= comp1["severity_score"] <= 100
        assert 0 <= comp1["impact_score"] <= 100
        assert 0 <= comp1["urgency_score"] <= 100
        assert comp1["severity_score"] <= 50, f"Vague pothole severity {comp1['severity_score']} exceeds small-to-medium baseline"
        assert comp1["needs_human_review"] is True, "Vague report must be flagged for human review"
        print("[PASS] Test 1 passed: Vague pothole received small-to-medium baseline and review flag")

        # TEST 2: Empty Description Baseline
        print("\n--- Test 2: Empty Description Baseline ---")
        empty_data = {
            "description": "",
            "category_id": str(garbage_cat["id"]),
            "location": "Near Central Market"
        }
        res_empty = requests.post(f"{BASE_URL}/complaints", data=empty_data, headers=c1_headers)
        assert res_empty.status_code == 201, f"Failed: {res_empty.text}"
        comp_empty = res_empty.json()
        created_ids.append(comp_empty["id"])
        print(f"Created #{comp_empty['id']}: Empty description garbage")
        print(f"  Severity: {comp_empty['severity_score']}")
        print(f"  Confidence: {comp_empty['assessment_confidence']}")
        print(f"  Needs Review: {comp_empty['needs_human_review']}")
        assert comp_empty["needs_human_review"] is True
        assert comp_empty["assessment_confidence"] in ["low", "uncertain"]
        print("[PASS] Test 2 passed: Empty description handled safely with baseline and review flag")

        # TEST 3: Detailed Description & High Severity Hazard
        print("\n--- Test 3: Detailed Description & Severe Hazard Detection ---")
        sewage_data = {
            "description": "Massive untreated sewage overflow erupting onto pedestrian walkways outside the District Hospital entrance. Immediate biohazard with thousands of daily visitors exposed to foul toxic water.",
            "category_id": str(sewage_cat["id"]),
            "location": "District Hospital Gate 1"
        }
        res2 = requests.post(f"{BASE_URL}/complaints", data=sewage_data, headers=c1_headers)
        assert res2.status_code == 201, f"Failed: {res2.text}"
        comp2 = res2.json()
        created_ids.append(comp2["id"])
        
        print(f"Created #{comp2['id']}: Severe Sewage Overflow")
        print(f"  Severity: {comp2['severity_score']}")
        print(f"  Impact: {comp2['impact_score']}")
        print(f"  Urgency: {comp2['urgency_score']}")
        print(f"  Priority Score: {comp2['priority_score']}")
        print(f"  Priority Level: {comp2['priority_level']}")
        
        assert comp2["severity_score"] >= 65, "Detailed sewage hazard must have high severity"
        assert comp2["impact_score"] >= 60, "Hospital impact must be significant"
        print("[PASS] Test 3 passed: Detailed severe hazard evaluated accurately")

        # TEST 4: Automatic Safety Hazard Escalation
        print("\n--- Test 4: Immediate Safety Hazard Trigger ---")
        live_wire_data = {
            "description": "Live electric cable snapped and hanging directly over active school bus stop sparking on wet road. Extreme life threatening electrocution hazard!",
            "category_id": str(traffic_cat["id"]),
            "location": "St. Mary School Bus Bay"
        }
        res_wire = requests.post(f"{BASE_URL}/complaints", data=live_wire_data, headers=c1_headers)
        assert res_wire.status_code == 201, f"Failed: {res_wire.text}"
        comp_wire = res_wire.json()
        created_ids.append(comp_wire["id"])
        
        print(f"Created #{comp_wire['id']}: Live Wire Hazard")
        print(f"  Priority Score: {comp_wire['priority_score']}")
        print(f"  Priority Level: {comp_wire['priority_level']}")
        print(f"  Safety Escalated: {comp_wire['is_safety_escalated']}")
        print(f"  Needs Review: {comp_wire['needs_human_review']}")
        
        assert comp_wire["is_safety_escalated"] is True or comp_wire["priority_level"] == "critical"
        assert comp_wire["needs_human_review"] is True
        print("[PASS] Test 4 passed: Immediate safety hazard triggered escalation and review flag")

        # TEST 5: Exact Mathematical Verification of Priority Formula & Upvote Dynamism
        print("\n--- Test 5: Exact Weighted Formula & Upvote Recalculation ---")
        sev = comp1["severity_score"]
        imp = comp1["impact_score"]
        urg = comp1["urgency_score"]
        init_priority = comp1["priority_score"]
        
        # At 0 upvotes: citizenSupport = 0
        expected_init = (sev * 0.40) + (imp * 0.25) + (urg * 0.20) + (0.0 * 0.15)
        print(f"  Initial Calculated: {expected_init:.2f}, Stored: {init_priority:.2f}")
        assert abs(init_priority - expected_init) < 0.1, "Initial priority does not match formula"
        
        # Record AI snapshot before upvote
        ai_sev_before = comp1.get("ai_severity_score")
        
        # Upvote by Citizen 2
        vote_res = requests.post(f"{BASE_URL}/complaints/{comp1['id']}/upvote", headers=c2_headers)
        assert vote_res.status_code == 200
        
        # Fetch updated complaint
        get_res = requests.get(f"{BASE_URL}/complaints/{comp1['id']}", headers=c1_headers)
        comp1_upvoted = get_res.json()
        upvoted_priority = comp1_upvoted["priority_score"]
        
        # Mathematical verification of 1 upvote with targetVotes=50:
        # supportScore = 100 * (log(1 + 1) / log(1 + 50)) = 100 * (0.6931 / 3.9318) = 17.6298
        # supportComponent = 17.6298 * 0.15 = 2.644
        expected_support = 100.0 * (math.log(2) / math.log(51))
        expected_upvoted = expected_init + (expected_support * 0.15)
        print(f"  After 1 vote: Expected {expected_upvoted:.2f}, Got {upvoted_priority:.2f}")
        assert abs(upvoted_priority - expected_upvoted) < 0.15, "Upvoted score mismatch with logarithmic support formula"
        
        # Confirm that AI snapshot was NOT mutated and LLM was NOT recalled
        assert comp1_upvoted.get("ai_severity_score") == ai_sev_before
        print("[PASS] Test 5 passed: Weighted formula verified, upvote updated score without LLM call")

        # TEST 6: Single Vote Constraint (No duplicate votes from same citizen)
        print("\n--- Test 6: Single Vote Constraint Verification ---")
        dup_vote = requests.post(f"{BASE_URL}/complaints/{comp1['id']}/upvote", headers=c2_headers)
        assert dup_vote.status_code in [400, 422], f"Citizen was able to upvote twice! Status: {dup_vote.status_code}"
        print("[PASS] Test 6 passed: Duplicate upvote prevented (HTTP 422 Validation Error)")

        # TEST 7: Admin Override & Triage Workflow
        print("\n--- Test 7: Admin Triage & Assessment Correction ---")
        override_payload = {
            "severity_score": 90,
            "impact_score": 85,
            "urgency_score": 80,
            "is_safety_escalated": True,
            "needs_human_review": False,
            "admin_override_reason": "Verified on-site by Senior City Engineer."
        }
        override_res = requests.put(
            f"{BASE_URL}/admin/complaints/{comp1['id']}/assessment",
            json=override_payload,
            headers=adm_headers
        )
        assert override_res.status_code == 200, f"Override failed: {override_res.text}"
        comp1_ov = override_res.json()
        print(f"  Admin Override Applied: {comp1_ov['admin_override']}")
        print(f"  New Severity: {comp1_ov['severity_score']}")
        print(f"  Original AI Severity Persisted: {comp1_ov.get('ai_severity_score')}")
        print(f"  New Priority Score: {comp1_ov['priority_score']}")
        print(f"  Priority Level: {comp1_ov['priority_level']}")
        
        assert comp1_ov["admin_override"] is True
        assert comp1_ov["priority_level"] == "critical"
        assert comp1_ov["is_safety_escalated"] is True
        assert comp1_ov["needs_human_review"] is False
        assert comp1_ov["ai_severity_score"] is not None, "Original AI assessment must be persisted separately"
        print("[PASS] Test 7 passed: Admin override persisted separately with audit note")

        # TEST 8: Admin Re-assessment Endpoint
        print("\n--- Test 8: Admin AI Re-evaluation Trigger ---")
        reassess_res = requests.post(f"{BASE_URL}/admin/complaints/{comp1['id']}/reassess", headers=adm_headers)
        assert reassess_res.status_code == 200, f"Reassess failed: {reassess_res.text}"
        comp1_reassessed = reassess_res.json()
        print(f"  Re-assessed Status: {comp1_reassessed['assessment_status']}")
        print(f"  New Score: {comp1_reassessed['priority_score']}")
        print("[PASS] Test 8 passed: Admin can re-run AI evaluation on demand")

        # TEST 9: Admin Dashboard KPI Priority Stats & Filtering
        print("\n--- Test 9: Admin Dashboard KPI Stats & Filtering ---")
        stats_res = requests.get(f"{BASE_URL}/admin/dashboard/stats", headers=adm_headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        print("  By Priority breakdown:", stats.get("by_priority"))
        print("  Critical Count:", stats.get("critical_count"))
        print("  Needs Review Count:", stats.get("needs_review_count"))
        assert "by_priority" in stats
        assert "critical_count" in stats
        assert "needs_review_count" in stats
        
        # Test filtering by priority_level
        filter_res = requests.get(f"{BASE_URL}/admin/complaints?priority_level=critical", headers=adm_headers)
        assert filter_res.status_code == 200
        critical_list = filter_res.json()["complaints"]
        for c in critical_list:
            assert c["priority_level"] == "critical"
        print(f"  Filtered critical complaints count: {len(critical_list)}")
        
        # Test sorting by priority_score
        sort_res = requests.get(f"{BASE_URL}/admin/complaints?sort_by=priority_score&sort_order=desc", headers=adm_headers)
        assert sort_res.status_code == 200
        sorted_list = sort_res.json()["complaints"]
        scores = [c["priority_score"] for c in sorted_list if c["priority_score"] is not None]
        assert scores == sorted(scores, reverse=True), "Complaints not sorted by priority_score descending"
        print("  Sorted by priority_score descending successfully verified")
        print("[PASS] Test 9 passed: Admin stats and priority filtering verified")

        # TEST 10: Preserving Existing Public & Citizen Workflows
        print("\n--- Test 10: Regression Check (Existing Citizen & Public Endpoints) ---")
        pub_res = requests.get(f"{BASE_URL}/complaints/public")
        assert pub_res.status_code == 200, "Public feed failed"
        pub_data = pub_res.json()
        assert "complaints" in pub_data
        
        # Verify status update workflow
        status_res = requests.put(
            f"{BASE_URL}/complaints/{comp1['id']}",
            json={"status": "working"},
            headers=adm_headers
        )
        assert status_res.status_code == 200, f"Status update failed: {status_res.text}"
        assert status_res.json()["status"] == "working"
        print("[PASS] Test 10 passed: Existing status transitions and public feed intact")

    finally:
        print("\nCleaning up test complaints...")
        import subprocess
        for cid in created_ids:
            subprocess.run(
                ["docker", "exec", "civic-postgres", "psql", "-U", "user", "-d", "civic_complaints", "-c",
                 f"DELETE FROM votes WHERE complaint_id = {cid}; DELETE FROM complaint_status_history WHERE complaint_id = {cid}; DELETE FROM complaints WHERE id = {cid};"],
                capture_output=True
            )
        print("Cleanup complete.")

    print("\n=================================================================")
    print("=== ALL 10 TESTS PASSED WITH 100% SUCCESS! ===")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
