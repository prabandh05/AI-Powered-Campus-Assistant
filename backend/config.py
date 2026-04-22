"""
Central configuration loader.
Reads secrets from .env and exposes them to the rest of the app.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env in the project root

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    print("[CONFIG] WARNING: GROQ_API_KEY not found in .env — LLM features will fail.")
