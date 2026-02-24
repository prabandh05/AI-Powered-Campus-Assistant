from pathlib import Path
from typing import Callable
import os

import streamlit as st
from groq import Groq

from chatbot.rag_pipeline import RAGPipeline, RAGConfig


def _load_rag() -> RAGPipeline | None:
    try:
        config = RAGConfig()
        return RAGPipeline(config)
    except FileNotFoundError:
        return None


def _init_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


GROQ_CLIENT = _init_groq_client()


def _dummy_llm(prompt: str) -> str:
    """
    Fallback LLM: shows retrieved context without calling an external API.
    """
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
    """
    Use Groq hosted models to generate a grounded answer.
    Expects GROQ_API_KEY to be set in the environment.
    """
    if GROQ_CLIENT is None:
        return _dummy_llm(prompt)

    # Keep request size within Groq's token limits by truncating the prompt.
    # This is a simple character-based heuristic that works well enough for the MVP.
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
        return f"Error while calling Groq API: {e}\n\nFalling back to showing retrieved context.\n\n{_dummy_llm(prompt)}"


def main() -> None:
    st.set_page_config(page_title="AI-Powered Campus Assistant", layout="wide")
    st.title("AI-Powered Campus Assistant (MVP)")
    st.write(
        "Ask questions about your campus based on content scraped from the official website."
    )

    index_exists = Path("embeddings/faiss_index.bin").exists() and Path(
        "embeddings/text_chunks.npy"
    ).exists()

    # Decide which LLM function to use
    if GROQ_CLIENT is not None:
        model_answer_fn: Callable[[str], str] = _groq_llm
        llm_status = "groq"
    else:
        model_answer_fn = _dummy_llm
        llm_status = "dummy"

    with st.sidebar:
        st.header("Status")
        if index_exists:
            st.success("Vector index found.")
        else:
            st.error("Vector index not found.")
            st.markdown(
                """
1. Run the scraper:
   `python scraper/scraper.py --base-url https://your-college-site.edu`

2. Build the vector store:
   `python embeddings/vector_store.py`
"""
            )

        st.markdown("---")
        if llm_status == "groq":
            st.success("Groq LLM: configured via GROQ_API_KEY.")
        else:
            st.warning(
                "Groq LLM not configured. Using dummy context-only responses.\n\n"
                "Set environment variable GROQ_API_KEY to enable natural language answers."
            )

    if not index_exists:
        st.info("Please generate the vector store before using the chatbot.")
        return

    rag = _load_rag()
    if rag is None:
        st.error("Failed to load RAG pipeline.")
        return

    if "chat_history" not in st.session_state:
        # Each entry: (role, text, optional_context)
        st.session_state.chat_history: list[tuple[str, str, str | None]] = []

    show_context = st.checkbox("Show retrieved context for each answer", value=False)

    user_query = st.text_input("Enter your question")

    if st.button("Ask") and user_query.strip():
        with st.spinner("Thinking..."):
            if show_context:
                answer, context = rag.generate_answer_with_context(
                    user_query, model_answer_fn=model_answer_fn
                )
            else:
                answer = rag.generate_answer(
                    user_query, model_answer_fn=model_answer_fn
                )
                context = None

        st.session_state.chat_history.append(("You 👤", user_query, None))
        st.session_state.chat_history.append(("Assistant 🤖", answer, context))

    st.subheader("Conversation")
    for role, text, ctx in st.session_state.chat_history:
        st.markdown(f"**{role}:** {text}")
        if role == "Assistant" and ctx and show_context:
            with st.expander("View retrieved context"):
                st.markdown(f"```text\n{ctx}\n```")


if __name__ == "__main__":
    main()

