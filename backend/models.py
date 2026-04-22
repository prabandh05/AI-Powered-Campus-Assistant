from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # student, staff, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    staff_profile = relationship("StaffProfile", back_populates="user", uselist=False)

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    usn = Column(String, unique=True, index=True)
    dept = Column(String)
    semester = Column(Integer)
    cgpa = Column(Integer)  # User said cgpa, might be float in reality
    subjects = Column(JSON)
    marks = Column(JSON)
    completed_courses = Column(JSON)

    user = relationship("User", back_populates="student_profile")

class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    name = Column(String)
    dept = Column(String)
    designation = Column(String)
    availability_status = Column(Boolean, default=True)

    user = relationship("User", back_populates="staff_profile")
    schedule = relationship("StaffSchedule", back_populates="staff")

class StaffSchedule(Base):
    __tablename__ = "staff_schedule"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_profiles.user_id"))
    day = Column(String)  # Monday, Tuesday, etc.
    start_time = Column(String)
    end_time = Column(String)

    staff = relationship("StaffProfile", back_populates="schedule")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    category = Column(String)  # hackathon, workshop, etc.
    file_path = Column(String, nullable=True)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)
    tags = Column(String)  # Or JSON
    file_path = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
