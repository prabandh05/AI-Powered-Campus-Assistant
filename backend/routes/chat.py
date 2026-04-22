from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, StaffProfile
from ..core.rag_engine import RAGEngine
from ..core.query_router import QueryRouter
from ..config import GROQ_API_KEY
import requests
import re

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize engines
rag_engine = RAGEngine()
query_router = QueryRouter(GROQ_API_KEY)


def search_faculty_by_name(query: str, db: Session):
    """Extract a faculty name from the query and search the database."""
    q = query.lower()
    
    # Get all staff profiles
    all_staff = db.query(StaffProfile).all()
    if not all_staff:
        return None
    
    # Try to match any staff name mentioned in the query
    matched = []
    for s in all_staff:
        name_lower = s.name.lower().strip()
        # Check if the staff name appears in the query
        if name_lower in q or any(part in q for part in name_lower.split() if len(part) > 2):
            matched.append({
                "name": s.name,
                "dept": s.dept,
                "designation": s.designation,
                "available": s.availability_status,
                "schedule": [
                    {"day": sc.day, "start": sc.start_time, "end": sc.end_time}
                    for sc in s.schedule
                ]
            })
    
    # If no specific name match, return all faculty info
    if not matched:
        for s in all_staff:
            matched.append({
                "name": s.name,
                "dept": s.dept,
                "designation": s.designation,
                "available": s.availability_status,
                "schedule": [
                    {"day": sc.day, "start": sc.start_time, "end": sc.end_time}
                    for sc in s.schedule
                ]
            })
    
    return matched


@router.post("/query")
def chat_query(query: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Classify Query
    intent = query_router.classify(query)
    print(f"Intent: {intent}")

    context = ""
    sql_data = None

    # 2. Retrieve Data based on intent
    if intent in ["SQL", "HYBRID"]:
        # Student marks / profile
        if any(kw in query.lower() for kw in ["marks", "my data", "cgpa", "usn", "semester", "my profile"]):
            if current_user.student_profile:
                sql_data = {
                    "role": "student",
                    "usn": current_user.student_profile.usn,
                    "dept": current_user.student_profile.dept,
                    "semester": current_user.student_profile.semester,
                    "cgpa": current_user.student_profile.cgpa,
                    "marks": current_user.student_profile.marks,
                    "subjects": current_user.student_profile.subjects,
                }
            else:
                sql_data = "No student profile found for this user."

        # Faculty availability — name-based search
        if any(kw in query.lower() for kw in [
            "available", "schedule", "faculty", "teacher", "professor",
            "staff", "meet", "mam", "sir", "ma'am", "madam"
        ]):
            faculty_results = search_faculty_by_name(query, db)
            if faculty_results:
                sql_data = {"faculty_data": faculty_results}
            else:
                sql_data = "No faculty data found in the system."

    # ALWAYS search RAG for knowledge queries and hybrid
    if intent in ["RAG", "HYBRID"]:
        rag_results = rag_engine.search(query, top_k=5)
        context = "\n---\n".join(rag_results)

    # 3. Generate Final Response using Groq LLM
    system_prompt = f"""You are the official AI assistant for Dayananda Sagar College of Engineering (DSCE), Bangalore.
Your role is to answer questions about DSCE using ONLY the verified information provided below.

RULES:
1. Answer based on the provided context. Do NOT make up information.
2. If the context does not contain enough info, say "I don't have enough information about that in my database."
3. Be concise, professional, and helpful.
4. Format your answers clearly using bullet points or paragraphs.
5. When citing specifics (names, numbers, dates), only use what appears in the context.
6. For faculty availability questions:
   - Show the faculty name, department, designation
   - Show if they are currently available (true/false)
   - Show their schedule (day, start time, end time)
   - If available=true, say they are currently available for meetings
   - If no schedule slots exist, mention they haven't set their available hours yet

USER ROLE: {current_user.role}

{f'DATABASE RESULTS (structured data): {sql_data}' if sql_data else ''}

CAMPUS KNOWLEDGE (from verified sources):
{context if context else 'No relevant campus knowledge found for this query.'}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    import time
    last_error = None
    for attempt in range(3):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, timeout=20
            )
            data = response.json()

            if "choices" in data:
                ai_response = data['choices'][0]['message']['content']
                return {
                    "answer": ai_response,
                    "intent": intent,
                    "sources": "RAG + SQL" if intent == "HYBRID" else intent
                }
            elif "error" in data:
                last_error = data["error"].get("message", str(data["error"]))
                if "rate_limit" in last_error.lower() or response.status_code == 429:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
            else:
                last_error = f"Unexpected response: {data}"
                break
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    return {
        "answer": f"I'm having trouble connecting to the AI engine right now. Error: {last_error}",
        "intent": intent,
        "sources": "error"
    }
