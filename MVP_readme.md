📌 Project Overview

The AI-Powered Campus Assistant is a Retrieval-Augmented Generation (RAG)-based chatbot designed to answer student queries using official college website content.

The system scrapes the college website, processes the data into semantic embeddings, stores them in a vector database, and retrieves relevant information to generate grounded responses using a Large Language Model (LLM).

⚠️ This MVP focuses only on:

Website data retrieval

Grounded responses

Basic chatbot interface

No personalization.
No real-time integration.
No ML training.

🎯 Problem Statement

Students often struggle to find accurate and timely information about:

College rules

Procedures

Forms

Notices

Academic updates

Information is scattered across web pages, leading to confusion and delays.

This system centralizes access through a natural language chatbot.

🧠 System Architecture (MVP)
College Website
      ↓
Web Scraper
      ↓
Text Cleaning
      ↓
Chunking
      ↓
Embeddings (Sentence Transformers)
      ↓
Vector Database (FAISS)
      ↓
LLM (via API)
      ↓
Streamlit Chat Interface
⚙️ Tech Stack
Backend

Python

Data Processing

BeautifulSoup

Requests

LangChain (Text Splitter)

Sentence-Transformers

Vector Database

FAISS

LLM

OpenAI API / Groq / Local Model

Frontend

Streamlit

🏗️ MVP Scope
Included

Scrape official college website pages

Extract and clean text

Create semantic embeddings

Store embeddings in FAISS

Retrieve top relevant chunks

Generate grounded response via LLM

Basic Streamlit chatbot UI

Controlled hallucination (strict prompt template)

Excluded (For Now)

PDF scraping

Real-time faculty availability

Timetable integration

Personalized recommendations

ML training on exam papers

Admin panel

Database for user accounts

📂 Project Structure
campus-assistant/
│
├── scraper/
│   └── scraper.py
│
├── data/
│   └── website_text.txt
│
├── embeddings/
│   └── vector_store.py
│
├── chatbot/
│   └── rag_pipeline.py
│
├── app.py
├── requirements.txt
└── README.md
🛠️ Implementation Plan
Phase 1 – Data Collection

 Identify base domain

 Crawl internal links only

 Extract text content

 Remove navigation junk

 Save consolidated text

Phase 2 – Text Processing

 Clean extracted text

 Split into chunks (500–800 tokens)

 Store chunks in list format

Phase 3 – Embeddings & Vector Store

 Generate embeddings using SentenceTransformer

 Initialize FAISS index

 Store vectors

 Save index locally

Phase 4 – Query Pipeline

 Convert user query to embedding

 Perform similarity search (top-k)

 Retrieve relevant chunks

 Inject into LLM prompt

 Return grounded answer

Phase 5 – Frontend

 Build Streamlit UI

 Add input field

 Display responses

 Add loading indicator

 Handle "no result found" case

🔒 Hallucination Control Strategy

Prompt Template:

You are a campus assistant.
Answer ONLY using the provided context.
If the answer is not found in the context, reply:
"The information is not available on the official website."

This ensures:

No fake answers

No guessing

No fabricated rules

📊 Evaluation Strategy

We will test using:

20 predefined campus-related questions

Accuracy check (Is answer grounded in website?)

Response time measurement

Failure case analysis

🚀 Future Scope (Post-MVP)

These features are NOT part of current submission but planned:

1️⃣ Structured Institutional Knowledge Base

Manual data collection from departments

Verified documents repository

Admin-approved content

2️⃣ Automated Real-Time Data Agent

Scheduled crawler

Daily website/blog monitoring

Auto-update vector database

Version tracking in Google Drive

3️⃣ Advanced Features

Faculty availability tracking

Timetable API integration

Event notifications

Student personalization

Academic recommendation system

ML models trained on past exam papers

4️⃣ Multi-Agent Architecture

Scraping Agent

Validation Agent

Retrieval Agent

Academic Recommendation Agent