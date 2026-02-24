## AI-Powered Campus Assistant (MVP)

This project is a **Retrieval-Augmented Generation (RAG)** chatbot that answers student queries using content scraped from an official college website (example used: `https://www.dsce.edu.in/`).

Key goals:
- **Grounded answers**: answers are generated only from retrieved website context (or from a small curated facts layer).
- **Low hallucination**: if the info is not present in the provided context, the assistant replies with a safe fallback.
- **MVP today, scalable later**: modular structure (scraping → indexing → retrieval → UI) so you can extend it.

### Project Structure

- `scraper/scraper.py`: Crawls the college website and saves cleaned text into `data/website_text.txt`.
- `embeddings/vector_store.py`: Builds sentence-transformer embeddings and a FAISS vector index from the scraped text.
- `chatbot/rag_pipeline.py`: Retrieval pipeline (semantic search + keyword fallback) and strict grounding prompt.
- `chatbot/facts_store.py`: Small **structured facts layer** (location / facilities / fees / examinations) for very precise, low-hallucination answers.
- `app.py`: Streamlit-based chatbot UI that uses the RAG pipeline.
- `requirements.txt`: Python dependencies for the MVP.
- `about_project.txt`: Full end-to-end explanation of how the system works.

### Features

- **Website scraping (MVP)**: internal-link crawler + visible text extraction.
- **Vector search**: sentence-transformer embeddings + FAISS similarity search.
- **Hybrid retrieval (lightweight)**: semantic retrieval + keyword fallback for better recall.
- **Hallucination control**:
  - strict prompt rule: “answer ONLY using provided context”
  - safe fallback response when context doesn’t contain the answer
  - structured facts for critical intents
- **Streamlit UI**:
  - simple chat interface
  - optional “Show retrieved context” debugging view

### Requirements

- Python 3.10+ recommended
- Windows (PowerShell) commands below; works on macOS/Linux with equivalent shell commands

### Installation (from scratch)

1. **Clone / open the project folder**

2. **Create and activate a virtual environment (recommended)**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Quickstart (end-to-end)

1. **Scrape the official website**

   ```bash
   python scraper/scraper.py --base-url https://www.dsce.edu.in/ --max-pages 150
   ```

   This creates `data/website_text.txt`.

2. **Build the vector store (embeddings + FAISS index)**

   ```bash
   python embeddings/vector_store.py
   ```

   This creates:

   - `embeddings/faiss_index.bin`
   - `embeddings/text_chunks.npy`

3. **Set Groq API key (for natural-language answers)**

This app supports Groq for the LLM step.

- **PowerShell (temporary for current terminal session)**:

  ```powershell
  $env:GROQ_API_KEY = "YOUR_GROQ_KEY_HERE"
  ```

- **Windows (permanent user environment variable)**:
  - Search “Environment Variables” → “Edit the system environment variables”
  - “Environment Variables…” → under “User variables” → “New…”
  - Name: `GROQ_API_KEY`
  - Value: your Groq key
  - Re-open your terminal after saving

If `GROQ_API_KEY` is not set, the app will run in a **dummy mode** that shows retrieved context but does not generate fluent answers.

4. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

   Open the displayed local URL in your browser to chat with the assistant.

### How answers are produced (very short)

When you ask a question:
1. The pipeline first checks `chatbot/facts_store.py` for critical intents (location/facilities/fees/exams).
2. If no fact matches, it retrieves relevant chunks from the website corpus using:
   - semantic similarity search (FAISS embeddings)
   - keyword fallback if semantic scores are low
3. The retrieved context is injected into a strict prompt and sent to Groq.

### Using “Show retrieved context”

In the UI, enable:
- **Show retrieved context for each answer**

This will display the exact website chunks that were provided to the model. This is useful for:
- verifying grounding
- debugging why a question returned “not available”

### Common Tasks

#### Re-scrape and rebuild the index (recommended when content changes)

```bash
python scraper/scraper.py --base-url https://www.dsce.edu.in/ --max-pages 150
python embeddings/vector_store.py
```

#### Clean rebuild (delete existing data/index first)

PowerShell:

```powershell
Remove-Item -Force -ErrorAction SilentlyContinue data\website_text.txt
Remove-Item -Force -ErrorAction SilentlyContinue embeddings\faiss_index.bin
Remove-Item -Force -ErrorAction SilentlyContinue embeddings\text_chunks.npy
python scraper/scraper.py --base-url https://www.dsce.edu.in/ --max-pages 150
python embeddings/vector_store.py
```

### Troubleshooting

#### Groq error: 413 / “Request too large … tokens per minute”

Cause:
- The prompt (context + question) is too large for the selected Groq tier/limits.

What this project does:
- Truncates the prompt before sending it to Groq to stay within limits.

If you still hit limits:
- Reduce `--max-pages` (smaller dataset can reduce chunk size/noise)
- Ask more specific questions (improves retrieval precision)

#### Answers say “The information is not available…”

This is expected when:
- the retrieved context does not contain a clear answer, or
- the website doesn’t have that info in the scraped pages.

Use “Show retrieved context” to confirm whether the relevant content is being retrieved.

### Notes / Limitations (MVP)

- Scraper currently targets **HTML pages** only (no PDFs).
- Crawling is limited by `--max-pages` to keep the MVP fast.
- Chunking is simple paragraph-based splitting; later you can improve it (HTML-aware chunking, hybrid BM25, etc.).

### Deep Explanation

See `about_project.txt` for a detailed end-to-end explanation of:
- scraping/parsing/cleaning
- chunking/embedding/indexing
- retrieval and hallucination control
- Groq integration
- Streamlit UI flow

### LLM / Model Configuration

- Default Groq model used in `app.py`: `llama-3.1-8b-instant`
- To change the model, update the `model=` parameter inside `_groq_llm()` in `app.py`.

