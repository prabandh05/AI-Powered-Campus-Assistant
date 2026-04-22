import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    # 1. Register a new student
    print("Registering user...")
    resp = requests.post(
        f"{BASE_URL}/auth/register",
        params={
            "username": "api_tester",
            "email": "api@dsce.edu.in",
            "password": "password123",
            "role": "student"
        }
    )
    print(f"Register Response: {resp.status_code}, {resp.json()}")

    # 2. Login
    print("Logging in...")
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "api_tester",
            "password": "password123"
        }
    )
    print(f"Login Response: {resp.status_code}")
    token_data = resp.json()
    token = token_data["access_token"]

    # 3. Access protected route
    print("Accessing /student/me...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/student/me", headers=headers)
    print(f"Protected Response (expected 404 since no profile yet): {resp.status_code}, {resp.json()}")

if __name__ == "__main__":
    # Wait a bit for server to start
    time.sleep(2)
    test_api()
