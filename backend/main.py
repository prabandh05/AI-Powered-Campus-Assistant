from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .auth import create_access_token, verify_password, get_password_hash, get_current_user, check_role
from .models import User, StudentProfile, StaffProfile, StaffSchedule, Document
from .routes import chat
from datetime import timedelta, datetime
import shutil
import os

app = FastAPI(title="Campus AI OS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat.router)

@app.post("/auth/register")
def register(username: str, email: str, password: str, role: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-create empty profile depends on role
    if role == "student":
        profile = StudentProfile(user_id=new_user.id, usn=f"USN_{new_user.id}", dept="TBD", semester=1, cgpa=0, subjects=[], marks={}, completed_courses=[])
        db.add(profile)
    elif role == "staff":
        profile = StaffProfile(user_id=new_user.id, name=username, dept="TBD", designation="Lecturer")
        db.add(profile)
    db.commit()
    
    return {"message": "User created successfully", "userId": new_user.id}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.get("/student/me")
def get_student_data(current_user: User = Depends(check_role(["student"]))):
    if not current_user.student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return {
        "username": current_user.username,
        "usn": current_user.student_profile.usn,
        "dept": current_user.student_profile.dept,
        "semester": current_user.student_profile.semester,
        "cgpa": current_user.student_profile.cgpa,
        "subjects": current_user.student_profile.subjects,
        "marks": current_user.student_profile.marks
    }

# --- STAFF ENDPOINTS ---
@app.get("/staff/me")
def get_staff_data(current_user: User = Depends(check_role(["staff"]))):
    if not current_user.staff_profile:
        raise HTTPException(status_code=404, detail="Staff profile not found")
    return {
        "name": current_user.staff_profile.name,
        "dept": current_user.staff_profile.dept,
        "designation": current_user.staff_profile.designation,
        "availability": current_user.staff_profile.availability_status,
        "schedule": [{"day": s.day, "start": s.start_time, "end": s.end_time} for s in current_user.staff_profile.schedule]
    }

@app.post("/staff/availability")
def toggle_availability(status: bool, current_user: User = Depends(check_role(["staff"])), db: Session = Depends(get_db)):
    current_user.staff_profile.availability_status = status
    db.commit()
    return {"message": f"Availability set to {status}"}

@app.post("/staff/schedule")
def add_schedule(day: str, start: str, end: str, current_user: User = Depends(check_role(["staff"])), db: Session = Depends(get_db)):
    new_slot = StaffSchedule(staff_id=current_user.id, day=day, start_time=start, end_time=end)
    db.add(new_slot)
    db.commit()
    return {"message": "Schedule slot added"}

@app.post("/staff/update_profile")
def update_staff_profile(name: str = None, dept: str = None, designation: str = None, current_user: User = Depends(check_role(["staff"])), db: Session = Depends(get_db)):
    if not current_user.staff_profile:
        raise HTTPException(status_code=404, detail="Staff profile not found")
    if name:
        current_user.staff_profile.name = name
    if dept:
        current_user.staff_profile.dept = dept
    if designation:
        current_user.staff_profile.designation = designation
    db.commit()
    return {"message": "Profile updated"}

# --- ADMIN ENDPOINTS ---
@app.post("/admin/upload")
async def admin_upload(file: UploadFile = File(...), current_user: User = Depends(check_role(["admin"])), db: Session = Depends(get_db)):
    upload_dir = "data/documents"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to SQL
    new_doc = Document(title=file.filename, category="Admin Upload", tags="manual", file_path=file_path, uploaded_by=current_user.id)
    db.add(new_doc)
    db.commit()
    
    # Trigger RAG re-indexing (Optional: could be async)
    from .routes.chat import rag_engine
    rag_engine.index_data(file_path)
    
    return {"message": f"File {file.filename} uploaded and indexed."}

@app.get("/admin/users")
def get_users(current_user: User = Depends(check_role(["admin"])), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]

@app.post("/admin/add_text_data")
async def add_text_data(title: str, content: str, category: str, current_user: User = Depends(check_role(["admin"])), db: Session = Depends(get_db)):
    upload_dir = "data/documents"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Sanitize title for filename
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_')]).rstrip()
    filename = f"{safe_title}.txt"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Save/Update in SQL
    doc = db.query(Document).filter(Document.title == title).first()
    if not doc:
        doc = Document(title=title, category=category, tags="manual", file_path=file_path, uploaded_by=current_user.id)
        db.add(doc)
    else:
        doc.file_path = file_path
        doc.category = category
        doc.uploaded_at = datetime.utcnow()
    
    db.commit()
    
    # Index the data
    from .routes.chat import rag_engine
    rag_engine.index_data(file_path)
    
    return {"message": f"Knowledge '{title}' added/updated and indexed."}

@app.get("/admin/documents")
def list_documents(current_user: User = Depends(check_role(["admin"])), db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [{
        "id": d.id,
        "title": d.title,
        "category": d.category,
        "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M")
    } for d in docs]

@app.get("/")
def read_root():
    return {"message": "Welcome to Campus AI OS Backend"}
