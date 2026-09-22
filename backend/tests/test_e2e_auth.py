import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("Starting E2E Authentication Tests...")
    
    unique_id = uuid.uuid4().hex[:8]
    user_email = f"testuser_{unique_id}@example.com"
    user_phone = f"99999{unique_id[:5]}"
    user_password = "SecurePassword123!"
    
    # 1. Register a new citizen
    print(f"\n[1] Registering new user: {user_email}")
    register_data = {
        "email": user_email,
        "phone": user_phone,
        "full_name": "Test Citizen",
        "password": user_password,
        "role": "citizen"
    }
    
    res = httpx.post(f"{BASE_URL}/api/auth/register", json={"user_data": register_data})
    
    if res.status_code != 200:
        print(f"FAILED Registration! Status: {res.status_code}")
        print(res.text)
        return False
        
    print("SUCCESS: Registration successful.")
    data = res.json()
    assert "access_token" in data
    
    # 2. Login
    print(f"\n[2] Logging in user: {user_email}")
    login_data = {
        "email": user_email,
        "password": user_password
    }
    res = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if res.status_code != 200:
        print(f"FAILED Login! Status: {res.status_code}")
        print(res.text)
        return False
        
    print("SUCCESS: Login successful.")
    data = res.json()
    access_token = data["access_token"]
    
    # 3. Access Protected API (/api/auth/me)
    print("\n[3] Accessing protected API endpoint /api/auth/me")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = httpx.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if res.status_code != 200:
        print(f"FAILED Protected API access! Status: {res.status_code}")
        print(res.text)
        return False
        
    print("SUCCESS: Accessed protected API successfully.")
    user_data = res.json()
    print(f"User Data: {user_data['email']}, Role: {user_data['role']}")
    
    print("\nALL TESTS PASSED!")
    return True

if __name__ == "__main__":
    run_tests()
