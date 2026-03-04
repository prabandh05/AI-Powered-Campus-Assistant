import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

from chatbot.rag_pipeline import RAGPipeline, RAGConfig
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Campus Assistant API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration & Initialization ---

def _init_groq_client() -> Optional[Groq]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None

GROQ_CLIENT = _init_groq_client()

def _load_rag() -> Optional[RAGPipeline]:
    try:
        config = RAGConfig()
        return RAGPipeline(config)
    except FileNotFoundError:
        return None

RAG_PIPELINE = _load_rag()

# --- LLM Functions ---

def _dummy_llm(prompt: str) -> str:
    try:
        context_part = prompt.split("Context:", 1)[1]
        question_part = context_part.split("Question:", 1)[1]
    except IndexError:
        return prompt

    context_only = context_part.split("Question:", 1)[0].strip()
    question_only = question_part.split("Answer:", 1)[0].strip()
    context_snippet = context_only[:600] + ("..." if len(context_only) > 600 else "")

    return (
        f"Question I understood:\n{question_only}\n\n"
        f"Here is a relevant snippet from the official website content:\n\n"
        f"{context_snippet}\n\n"
        "This dummy mode only shows retrieved context. "
        "Set GROQ_API_KEY to enable natural language answers."
    )

def _groq_llm(prompt: str) -> str:
    if GROQ_CLIENT is None:
        return _dummy_llm(prompt)

    max_chars = 6000
    if len(prompt) > max_chars:
        prompt = prompt[:max_chars]

    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful campus assistant. "
                        "Follow the instructions in the prompt and answer ONLY using the given context."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error while calling Groq API: {e}\n\n{_dummy_llm(prompt)}"

# --- API Models & Endpoints ---

class ChatRequest(BaseModel):
    message: str
    show_context: bool = False

class ChatResponse(BaseModel):
    answer: str
    context: Optional[str] = None

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_ready": RAG_PIPELINE is not None,
        "groq_ready": GROQ_CLIENT is not None
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if RAG_PIPELINE is None:
        raise HTTPException(status_code=503, detail="RAG Pipeline not initialized. Check server logs.")

    model_answer_fn = _groq_llm if GROQ_CLIENT else _dummy_llm

    try:
        if request.show_context:
            answer, context = RAG_PIPELINE.generate_answer_with_context(
                request.message, model_answer_fn=model_answer_fn
            )
        else:
            answer = RAG_PIPELINE.generate_answer(
                request.message, model_answer_fn=model_answer_fn
            )
            context = None
        
        return ChatResponse(answer=answer, context=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Serve Frontend ---

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
