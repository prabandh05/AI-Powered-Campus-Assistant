from backend.database import SessionLocal
from backend.models import User, StudentProfile
import json

def test_insert_fetch():
    db = SessionLocal()
    try:
        # 1. Create a test student user
        new_user = User(
            username="tester_student",
            email="test@dsce.edu.in",
            password_hash="fakehash",
            role="student"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created: {new_user.username} (ID: {new_user.id})")

        # 2. Add student profile
        new_profile = StudentProfile(
            user_id=new_user.id,
            usn="1DS22CS001",
            dept="CSE",
            semester=4,
            cgpa=9,
            subjects=["DSA", "DBMS", "OS"],
            marks={"DSA": 85, "DBMS": 90},
            completed_courses=["Maths", "Physics"]
        )
        db.add(new_profile)
        db.commit()
        print(f"Profile created for USN: {new_profile.usn}")

        # 3. Fetch and verify
        fetched_user = db.query(User).filter(User.username == "tester_student").first()
        print(f"Fetched User: {fetched_user.username}, Role: {fetched_user.role}")
        print(f"Fetched USN: {fetched_user.student_profile.usn}")
        print(f"Fetched Marks: {fetched_user.student_profile.marks}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_insert_fetch()
