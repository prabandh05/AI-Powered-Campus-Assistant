## AI-Powered Campus Assistant (MVP)

This MVP is a Retrieval-Augmented Generation (RAG) chatbot that answers student queries using content scraped from the official college website.

### Project Structure

- `scraper/scraper.py`: Crawls the college website and saves cleaned text into `data/website_text.txt`.
- `embeddings/vector_store.py`: Builds sentence-transformer embeddings and a FAISS vector index from the scraped text.
- `chatbot/rag_pipeline.py`: Implements the retrieval and prompt-building logic for grounded answers.
- `app.py`: Streamlit-based chatbot UI that uses the RAG pipeline.
- `requirements.txt`: Python dependencies for the MVP.

### Setup

1. **Create and activate a virtual environment (recommended)**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Pipeline

1. **Scrape the official website**

   ```bash
   python scraper/scraper.py --base-url https://your-college-site.edu
   ```

   This creates `data/website_text.txt`.

2. **Build the vector store**

   ```bash
   python embeddings/vector_store.py
   ```

   This creates:

   - `embeddings/faiss_index.bin`
   - `embeddings/text_chunks.npy`

3. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

   Open the displayed local URL in your browser to chat with the assistant.

### Swapping in a Real LLM (Future)

The current MVP uses a simple placeholder LLM function so it runs without API keys.  
To integrate a real model (OpenAI, Groq, local), replace `_dummy_llm` in `app.py` with a function that:

1. Accepts a single `prompt: str`
2. Returns the generated answer as `str`

and pass it into `main(model_answer_fn=your_llm_fn)`.

