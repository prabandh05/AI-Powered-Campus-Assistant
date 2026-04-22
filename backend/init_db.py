from .database import engine, Base
from .models import User, StudentProfile, StaffProfile, StaffSchedule, Event, Document

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
