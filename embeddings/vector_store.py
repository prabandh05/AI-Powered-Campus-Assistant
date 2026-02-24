from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_corpus_text(text_path: Path) -> List[str]:
    """
    Load pre-scraped website text and split into simple paragraphs.
    For the MVP we treat each non-empty block separated by blank lines as a chunk.
    """
    raw = text_path.read_text(encoding="utf-8")
    # split on double newlines and strip
    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]

    cleaned_blocks: List[str] = []
    for b in blocks:
        # Skip chunks that are mostly separators or non-alphabetic noise
        alpha_ratio = sum(ch.isalpha() for ch in b) / max(len(b), 1)
        if alpha_ratio < 0.1:
            continue
        cleaned_blocks.append(b)

    return cleaned_blocks


def build_embeddings(
    texts: List[str],
    model_name: str = DEFAULT_MODEL_NAME,
) -> Tuple[np.ndarray, SentenceTransformer]:
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")
    return embeddings, model


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build an inner-product FAISS index. We will L2-normalize embeddings so that
    inner product is equivalent to cosine similarity.
    """
    faiss.normalize_L2(embeddings)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def save_index(
    index: faiss.IndexFlatIP,
    texts: List[str],
    index_path: Path,
    texts_path: Path,
) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    texts_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))
    texts_array = np.array(texts, dtype=object)
    np.save(texts_path, texts_array, allow_pickle=True)


def load_index_and_texts(
    index_path: Path,
    texts_path: Path,
) -> Tuple[faiss.IndexFlatIP, List[str]]:
    index = faiss.read_index(str(index_path))
    texts_array = np.load(texts_path, allow_pickle=True)
    texts: List[str] = texts_array.tolist()
    return index, texts


def create_vector_store(
    corpus_path: str = "data/website_text.txt",
    index_path: str = "embeddings/faiss_index.bin",
    texts_path: str = "embeddings/text_chunks.npy",
    model_name: str = DEFAULT_MODEL_NAME,
) -> None:
    """
    High-level helper to:
    - Load scraped text
    - Create chunks
    - Build embeddings
    - Build FAISS index
    - Persist index and chunks
    """
    corpus_file = Path(corpus_path)
    if not corpus_file.exists():
        raise FileNotFoundError(
            f"Corpus file not found at {corpus_file}. Run the scraper first."
        )

    texts = load_corpus_text(corpus_file)
    if not texts:
        raise ValueError("No text chunks were created from the corpus.")

    embeddings, _ = build_embeddings(texts, model_name=model_name)
    index = build_faiss_index(embeddings)
    save_index(index, texts, Path(index_path), Path(texts_path))


if __name__ == "__main__":
    create_vector_store()

