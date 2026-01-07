import requests
import sys

BASE_URL = "http://localhost:5000/api"

def test_auth():
    username = "testuser_debug"
    email = "testuser_debug@example.com"
    password = "password123"

    print(f"Testing with: {username}, {email}, {password}")

    # 1. Register
    print("1. Registering...")
    # Clean up first if possible, but we don't have delete endpoint exposed usually
    # Just try to register. If it fails due to existing, we try login anyway.
    
    reg_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/register", json=reg_data)
        print(f"Register Response: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Register Request Failed: {e}")
        return

    # 2. Login
    print("2. Logging in...")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login Response: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200 and resp.json().get('success'):
            print("SUCCESS: Login worked via API.")
        else:
            print("FAILURE: Login failed via API.")
            
    except Exception as e:
        print(f"Login Request Failed: {e}")

if __name__ == "__main__":
    test_auth()
