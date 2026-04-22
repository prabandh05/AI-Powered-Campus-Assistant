import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import subprocess
import re


class RAGEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.vector_db_path = "data/vector_db"
        os.makedirs(self.vector_db_path, exist_ok=True)
        self.load_index()

    def _clean_text(self, text: str) -> str:
        """Remove noise: extra whitespace, URLs, empty lines."""
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 75) -> List[str]:
        """
        Split text into overlapping chunks by word count.
        - Smaller chunks (300 words) = more precise retrieval
        - 75-word overlap = context continuity between chunks
        """
        text = self._clean_text(text)
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            # Only keep chunks with real content (>20 words)
            if len(chunk.split()) > 20:
                chunks.append(chunk)
            i += chunk_size - overlap
        return chunks

    def chunk_by_paragraph(self, text: str, max_chunk_words: int = 400) -> List[str]:
        """
        Smart paragraph-aware chunking:
        1. Split text into paragraphs (double newline).
        2. Group small paragraphs together into chunks up to max_chunk_words.
        3. Split oversized paragraphs using word-based chunking.
        """
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_words = 0

        for para in paragraphs:
            para = self._clean_text(para)
            if not para or len(para.split()) < 5:
                continue

            para_words = len(para.split())

            if para_words > max_chunk_words:
                # Flush what we have
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_words = 0
                # Split oversized paragraph
                chunks.extend(self.chunk_text(para, chunk_size=300, overlap=75))
            elif current_words + para_words > max_chunk_words:
                # Flush current chunk and start new one
                chunks.append(" ".join(current_chunk))
                current_chunk = [para]
                current_words = para_words
            else:
                current_chunk.append(para)
                current_words += para_words

        # Flush remaining
        if current_chunk:
            combined = " ".join(current_chunk)
            if len(combined.split()) > 20:
                chunks.append(combined)

        return chunks

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF (using pdftotext) or plain text files."""
        if file_path.endswith(".pdf"):
            try:
                result = subprocess.run(
                    ["pdftotext", file_path, "-"],
                    capture_output=True, text=True, timeout=30
                )
                return result.stdout
            except Exception as e:
                print(f"PDF extraction error: {e}")
                return ""
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

    def build_full_index(self, file_path: str) -> None:
        """
        FULL RE-INDEX: Reads the main campus knowledge file,
        chunks it properly, embeds everything, and saves a fresh FAISS index.
        This is the "training" step.
        """
        print(f"[RAG] Full index build from: {file_path}")
        text = self.extract_text(file_path)
        if not text.strip():
            print("[RAG] ERROR: File is empty!")
            return

        # Use smart paragraph-aware chunking
        new_chunks = self.chunk_by_paragraph(text, max_chunk_words=400)
        print(f"[RAG] Created {len(new_chunks)} chunks from {len(text)} chars")

        if not new_chunks:
            print("[RAG] ERROR: No valid chunks created!")
            return

        self.chunks = new_chunks

        # Batch encode for efficiency
        print("[RAG] Encoding embeddings...")
        embeddings = self.model.encode(self.chunks, show_progress_bar=True, batch_size=64)

        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine similarity on normalized vectors

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))

        # Save
        faiss.write_index(self.index, os.path.join(self.vector_db_path, "faiss.index"))
        np.save(os.path.join(self.vector_db_path, "chunks.npy"), np.array(self.chunks, dtype=object))
        print(f"[RAG] Index saved: {self.index.ntotal} vectors, {len(self.chunks)} chunks")

    def index_data(self, file_path: str) -> None:
        """
        INCREMENTAL INDEX: Adds new data to the existing index.
        Used for admin uploads (snippets, PDFs).
        """
        text = self.extract_text(file_path)
        if not text.strip():
            print(f"[RAG] Skipping empty file: {file_path}")
            return

        new_chunks = self.chunk_by_paragraph(text, max_chunk_words=400)
        if not new_chunks:
            # Fallback: treat the whole text as one chunk if it's short
            if len(text.split()) > 10:
                new_chunks = [self._clean_text(text)]
            else:
                return

        self.chunks.extend(new_chunks)
        embeddings = self.model.encode(new_chunks, batch_size=64)

        dimension = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatIP(dimension)

        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))

        # Save updated index
        faiss.write_index(self.index, os.path.join(self.vector_db_path, "faiss.index"))
        np.save(os.path.join(self.vector_db_path, "chunks.npy"), np.array(self.chunks, dtype=object))
        print(f"[RAG] Added {len(new_chunks)} chunks. Total: {len(self.chunks)}")

    def load_index(self) -> bool:
        """Load existing FAISS index and chunks from disk."""
        index_path = os.path.join(self.vector_db_path, "faiss.index")
        chunks_path = os.path.join(self.vector_db_path, "chunks.npy")
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            self.index = faiss.read_index(index_path)
            self.chunks = np.load(chunks_path, allow_pickle=True).tolist()
            print(f"[RAG] Loaded index: {self.index.ntotal} vectors, {len(self.chunks)} chunks")
            return True
        print("[RAG] No existing index found.")
        return False

    def search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search for the most relevant chunks given a query.
        Returns top_k results ranked by cosine similarity.
        """
        if not self.index or self.index.ntotal == 0:
            print("[RAG] WARNING: Index is empty!")
            return []

        query_vector = self.model.encode([query])
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector.astype('float32'), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results


if __name__ == "__main__":
    rag = RAGEngine()

    # Full rebuild from scraped website data
    corpus_path = "data/campus_knowledge.txt"
    if os.path.exists(corpus_path):
        rag.build_full_index(corpus_path)

        # Quick test
        print("\n--- TEST QUERIES ---")
        for q in [
            "Who is the principal of DSCE?",
            "What are the placement statistics?",
            "Tell me about CSE department",
            "What are the admission requirements?",
            "Tell me about the campus facilities",
        ]:
            results = rag.search(q, top_k=3)
            print(f"\nQ: {q}")
            for r in results:
                print(f"  -> {r[:150]}...")
    else:
        print(f"[ERROR] {corpus_path} not found!")
