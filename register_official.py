import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server():
    for _ in range(20):
        try:
            resp = requests.get(f"{BASE_URL}/")
            if resp.status_code == 200:
                print("Server online!")
                return True
        except:
            print("Waiting for server...")
            time.sleep(3)
    return False

def register_users():
    users = [
        {"username": "student", "email": "student@dsce.edu.in", "password": "password123", "role": "student"},
        {"username": "staff", "email": "staff@dsce.edu.in", "password": "password123", "role": "staff"},
        {"username": "admin", "email": "admin@dsce.edu.in", "password": "password123", "role": "admin"}
    ]
    
    for user in users:
        try:
            resp = requests.post(f"{BASE_URL}/auth/register", params=user)
            print(f"Registering {user['username']}: {resp.status_code} - {resp.json()}")
        except Exception as e:
            print(f"Failed to register {user['username']}: {e}")

if __name__ == "__main__":
    if wait_for_server():
        register_users()
    else:
        print("Server timed out.")
