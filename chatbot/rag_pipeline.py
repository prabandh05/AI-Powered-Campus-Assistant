from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from embeddings.vector_store import DEFAULT_MODEL_NAME, load_index_and_texts


PROMPT_TEMPLATE = """You are a campus assistant.
Answer ONLY using the provided context.
If the answer is not found in the context, reply:
"The information is not available on the official website."

Context:
{context}

Question:
{question}

Answer:"""


@dataclass
class RAGConfig:
    index_path: Path = Path("embeddings/faiss_index.bin")
    texts_path: Path = Path("embeddings/text_chunks.npy")
    model_name: str = DEFAULT_MODEL_NAME
    # Use fewer chunks by default to keep prompts small for hosted APIs.
    top_k: int = 3


class RAGPipeline:
    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()

        if not self.config.index_path.exists() or not self.config.texts_path.exists():
            raise FileNotFoundError(
                "Vector index or text chunks not found. "
                "Run the vector store creation step first."
            )

        self.index, self.texts = load_index_and_texts(
            self.config.index_path, self.config.texts_path
        )
        self.encoder = SentenceTransformer(self.config.model_name)

    def retrieve(self, query: str) -> Tuple[List[str], List[float]]:
        """Return top-k context chunks and their similarity scores.

        Uses embedding-based retrieval first and falls back to a simple
        keyword search over the corpus when similarity scores are low.
        """
        query_vec = self.encoder.encode([query], convert_to_numpy=True).astype(
            "float32"
        )
        faiss.normalize_L2(query_vec)
        scores, indices = self.index.search(query_vec, self.config.top_k)

        idxs = indices[0]
        scs = scores[0]

        chunks: List[str] = []
        chunk_scores: List[float] = []
        for idx, sc in zip(idxs, scs):
            if idx == -1:
                continue
            chunks.append(self.texts[idx])
            chunk_scores.append(float(sc))

        # If we didn't retrieve anything useful, fall back to
        # a simple keyword-based search on the raw text.
        if not chunks or max(chunk_scores, default=0.0) < 0.15:
            keyword_chunks = self.keyword_retrieve(query)
            if keyword_chunks:
                return keyword_chunks, [1.0] * len(keyword_chunks)

        return chunks, chunk_scores

    def keyword_retrieve(self, query: str, max_results: int | None = None) -> List[str]:
        """Very simple keyword-based retrieval over the raw text chunks.

        This helps when embedding similarity fails for short or specific
        keywords like 'placements', 'fees', or 'bus facility'.
        """
        if max_results is None:
            max_results = self.config.top_k

        # Basic tokenization and filtering
        query_terms = [
            w.lower() for w in query.split() if len(w) >= 4 and w.isalpha()
        ]
        if not query_terms:
            return []

        scored: List[tuple[float, str]] = []
        for t in self.texts:
            tl = t.lower()
            score = sum(tl.count(term) for term in query_terms)
            if score > 0:
                scored.append((float(score), t))

        if not scored:
            return []

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:max_results]]

    def build_context(self, chunks: List[str]) -> str:
        return "\n\n---\n\n".join(chunks)

    def generate_answer(self, question: str, model_answer_fn) -> str:
        """
        model_answer_fn: a callable that accepts a prompt:str and returns str.
        This allows plugging in OpenAI, Groq, or local models from the app layer.
        """
        chunks, _ = self.retrieve(question)
        if not chunks:
            return 'The information is not available on the official website.'

        context = self.build_context(chunks)
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        return model_answer_fn(prompt)


