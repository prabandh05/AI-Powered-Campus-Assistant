# 🎓 Campus AI Operating System

> An AI-Powered Role-Based Campus Assistant for Dayananda Sagar College of Engineering (DSCE), Bangalore

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-4285F4?logo=meta&logoColor=white)](https://github.com/facebookresearch/faiss)

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Future Scope](#future-scope)

---

## Overview

Campus AI OS is a **hybrid intelligence system** that combines:

- **SQL Database** for structured data (student profiles, faculty schedules, availability)
- **RAG (Retrieval-Augmented Generation)** for unstructured campus knowledge (placement stats, admission rules, department info)
- **LLM (Large Language Model)** for natural language answer generation

The system serves three user roles — **Student**, **Faculty**, and **Admin** — each with tailored dashboards and AI-assisted features.

### Why Not Just Use ChatGPT?

| Problem | Why LLM Alone Fails | Our Solution |
|---|---|---|
| "What are my marks?" | LLM doesn't know your data | SQL database lookup |
| "Is Shreya available?" | LLM can't track schedules | Real-time DB query |
| "What are attendance rules?" | LLM may hallucinate | RAG with verified data |
| "Tell me about placements" | LLM has no DSCE data | Vector search on scraped content |

---

## System Architecture

```
┌──────────────────────────────────────────────────┐
│              React Frontend (Vite)                │
│         ChatGPT-like dark theme interface         │
└─────────────────────┬────────────────────────────┘
                      │ REST API (HTTP)
┌─────────────────────▼────────────────────────────┐
│              FastAPI Backend                      │
│                                                   │
│  ┌─────────────┐  ┌────────────────────────────┐ │
│  │ Auth (JWT)   │  │ Query Router               │ │
│  │ Role Guards  │  │ SQL ← Exact Data           │ │
│  └──────┬──────┘  │ RAG ← Knowledge            │ │
│         │         │ HYBRID ← Both               │ │
│         │         └───┬──────────┬──────────────┘ │
│         │             │          │                │
│  ┌──────▼─────┐ ┌─────▼───┐ ┌───▼────────────┐  │
│  │  SQLite    │ │ FAISS   │ │ Groq LLM API   │  │
│  │  Database  │ │ Vector  │ │ (Llama-3.1-8b) │  │
│  │            │ │ Store   │ │                 │  │
│  │ Users      │ │ 224     │ │ Generates final │  │
│  │ Profiles   │ │ chunks  │ │ grounded answer │  │
│  │ Schedules  │ │         │ │                 │  │
│  └────────────┘ └─────────┘ └─────────────────┘  │
└──────────────────────────────────────────────────┘
```

### RAG Pipeline

```
 College Website ──→ Web Scraper ──→ Raw Data (1.3 MB)
                                         │
                                    Data Cleaner (90% noise removed)
                                         │
                                    Clean Data (347 KB)
                                         │
                                    Paragraph-Aware Chunker
                                         │
                                    224 Text Chunks
                                         │
                                    Sentence-Transformers
                                    (all-MiniLM-L6-v2)
                                         │
                                    384-dim Vectors
                                         │
                                    FAISS Index
                                    (Cosine Similarity)
```

---

## Technology Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.12** | Core programming language |
| **FastAPI** | REST API framework (async, auto-docs) |
| **Uvicorn** | ASGI server |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Lightweight relational database |
| **python-jose** | JWT token generation & verification |
| **passlib** | Password hashing (pbkdf2_sha256) |

### AI / ML
| Technology | Purpose |
|---|---|
| **sentence-transformers** | Text → 384-dim vector embeddings |
| **all-MiniLM-L6-v2** | Embedding model (fast, accurate) |
| **FAISS** | Vector similarity search (Facebook AI) |
| **Groq API** | LLM inference (Llama-3.1-8b-instant) |
| **PyTorch** | Deep learning backend |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | Component-based UI library |
| **Vite 8** | Fast build tool and dev server |
| **Vanilla CSS** | Custom dark theme (no framework) |

### Data Pipeline
| Technology | Purpose |
|---|---|
| **BeautifulSoup4** | Web scraping and HTML parsing |
| **Custom Cleaner** | Removes 90% navigation noise |
| **Paragraph Chunker** | Semantic text splitting |

---

## Features

### 🎓 Student Dashboard
- AI chat assistant for any campus question
- Personal profile view (USN, department, CGPA, marks)
- Suggestion chips for quick queries

### 👩‍🏫 Faculty Hub
- **Editable Profile** — Update name, department, designation
- **Availability Toggle** — Mark yourself as available/unavailable for meetings
- **Consultation Hours** — Set when students can meet you (day + time slots)

### 🛠️ Admin Command Center
- **⚡ Snap Knowledge** — Inject quick facts into the AI brain instantly
- **📄 Formal Entry** — Add structured knowledge with title, category, content
- **📁 File Upload** — Upload PDF/TXT files for bulk indexing
- **📊 System Dashboard** — View all registered users and indexed documents

### 💬 AI Chat (All Roles)
- ChatGPT-like interface with dark theme
- Thinking animation during response generation
- Source attribution (RAG / SQL / HYBRID)
- Faculty name-based availability search
- Retry logic with exponential backoff for API rate limits

---

## Project Structure

```
Campus/
├── .env                          # GROQ_API_KEY
├── requirements.txt              # Python dependencies
├── about.txt                     # Detailed project documentation
├── README.md                     # This file
│
├── backend/                      # FastAPI Server
│   ├── config.py                 # Environment variable loader
│   ├── database.py               # SQLAlchemy engine & session
│   ├── models.py                 # ORM models (User, Profile, etc.)
│   ├── auth.py                   # JWT auth & role-based guards
│   ├── main.py                   # All REST API endpoints
│   ├── core/
│   │   ├── rag_engine.py         # FAISS indexing & semantic search
│   │   └── query_router.py       # Intent classifier (SQL/RAG/HYBRID)
│   └── routes/
│       └── chat.py               # Chat endpoint → Router → LLM
│
├── frontend-react/               # React UI (Vite)
│   ├── src/
│   │   ├── App.jsx               # All components
│   │   ├── api.js                # Backend API client
│   │   └── index.css             # Premium dark theme
│   └── dist/                     # Production build
│
├── scraper/                      # Data Pipeline
│   ├── scraper.py                # DSCE website crawler
│   ├── clean_data.py             # Data cleaning (90% noise removal)
│   └── rebuild_index.py          # FAISS index builder
│
└── data/                         # Persistent Storage
    ├── campus.db                 # SQLite database
    ├── campus_knowledge.txt      # Raw scraped data (1.3 MB)
    ├── campus_clean.txt          # Cleaned data (347 KB)
    ├── vector_db/                # FAISS index files
    └── documents/                # Admin-uploaded files
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+ (tested on 3.12)
- Node.js 18+ (tested on 20.20)
- A Groq API key (free at [console.groq.com](https://console.groq.com))

### Step 1: Clone & Set Up Python Environment

```bash
# Create and activate virtual environment
python3 -m venv ai-env
source ai-env/bin/activate   # Linux/Mac
# ai-env\Scripts\activate    # Windows

# Install Python dependencies
cd Campus
pip install -r requirements.txt
```

### Step 2: Configure the API Key

Create a `.env` file in the project root:

```bash
GROQ_API_KEY="gsk_your_groq_api_key_here"
```

### Step 3: Set Up React Frontend

```bash
cd frontend-react
npm install
```

### Step 4: Build the Knowledge Base (First Time Only)

```bash
# Clean the raw scraped data
python3 scraper/clean_data.py

# Build the FAISS vector index
python3 scraper/rebuild_index.py
```

This creates the vector database from the scraped DSCE website data.

---

## Running the Application

### Terminal 1 — Backend Server

```bash
source ai-env/bin/activate
cd Campus
uvicorn backend.main:app --port 8000 --reload
```

### Terminal 2 — React Frontend

```bash
cd Campus/frontend-react
npm run dev
```

### Access the App

| Service | URL |
|---|---|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

### Default Test Flow

1. **Register** a new account (choose Student/Faculty/Admin role)
2. **Login** with your credentials
3. **Chat** — Ask any question about DSCE
4. **Faculty** — Edit profile, set availability, add consultation hours
5. **Admin** — Add knowledge, upload documents, view system status

---

## How It Works

### Query Processing Flow

```
User: "When can I meet Shreya mam?"
         │
         ▼
  ┌─────────────────┐
  │  Query Router    │ ← Detects "meet" + "mam" → HYBRID
  └────────┬────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  ┌──────┐  ┌──────┐
  │ SQL  │  │ RAG  │
  │      │  │      │
  │Search│  │Search│
  │"Shre-│  │top-5 │
  │ya" in│  │chunks│
  │Staff │  │      │
  └──┬───┘  └──┬───┘
     │         │
     └────┬────┘
          │
  ┌───────▼────────┐
  │   Groq LLM     │
  │ (Llama-3.1-8b) │
  │                 │
  │ System prompt:  │
  │ - User role     │
  │ - SQL results   │
  │ - RAG context   │
  │ - Anti-halluc.  │
  │   rules         │
  └───────┬────────┘
          │
          ▼
  "Shreya is available. You can meet her on
   Monday from 10:00 AM to 11:30 AM.
   She is in the ISE department."
```

### Data Pipeline Flow

```
DSCE Website → Scraper → Raw Text (50K lines)
                              │
                         Data Cleaner (removes 90% noise)
                              │
                         Clean Text (4.9K lines)
                              │
                         Chunk by Paragraphs (224 chunks)
                              │
                         Embed (all-MiniLM-L6-v2)
                              │
                         FAISS Index (cosine similarity)
                              │
                         Ready for search!
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login (returns JWT token) |

### Chat
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/chat/query` | Any role | Ask a question to the AI |

### Student
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/student/me` | Student | Get own profile |

### Faculty
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/staff/me` | Staff | Get own profile |
| POST | `/staff/availability` | Staff | Toggle availability |
| POST | `/staff/schedule` | Staff | Add consultation hours |
| POST | `/staff/update_profile` | Staff | Edit name/dept/designation |

### Admin
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/admin/add_text_data` | Admin | Add knowledge entry |
| POST | `/admin/upload` | Admin | Upload PDF/TXT file |
| GET | `/admin/users` | Admin | List all users |
| GET | `/admin/documents` | Admin | List indexed documents |

---

## Future Scope

- 🔄 **Conversation Memory** — Multi-turn context for follow-up questions
- 📅 **Calendar View** — Visual weekly schedule for faculty
- 🐳 **Docker Deployment** — Containerized production setup
- 📱 **Mobile PWA** — Responsive design for mobile access
- 🔔 **Notifications** — Real-time event and notice alerts
- 🌐 **Multi-language** — Kannada and Hindi support
- 📊 **Analytics** — Admin dashboard with usage metrics
- 🔗 **ERP Integration** — Connect with college ERP system

---

## License

This project was developed as part of AIML coursework at DSCE, Bangalore.

---

