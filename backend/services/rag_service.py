"""
RAG Pipeline Service
Builds and queries a FAISS vector store from the question bank + resume text.
Uses LangChain + sentence-transformers for embeddings.
"""

import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "vector_store")
EMBEDDING_MODEL   = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class RAGService:
    """
    Retrieval-Augmented Generation pipeline.

    Workflow:
      1. build_index(documents)   – encode docs and save FAISS index
      2. retrieve(query, k)       – find top-k relevant chunks
      3. (LLM is called separately in interview_service.py)
    """

    def __init__(self):
        self._embedder     = None
        self._vector_store = None
        self._documents    = []
        self._init_embedder()

    # ── Embedding model ───────────────────────────────────────────────────────
    def _init_embedder(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
            logger.info(f"✅  Embedding model '{EMBEDDING_MODEL}' loaded.")
        except Exception as exc:
            logger.error(f"Embedder init failed: {exc}")

    # ── Build FAISS index from a list of text documents ────────────────────────
    def build_index(self, documents: List[str], metadata: Optional[List[dict]] = None):
        """
        Encode `documents` and build/update the FAISS vector store.

        Args:
            documents: List of text chunks to index.
            metadata:  Optional parallel list of dicts for each document.
        """
        if not documents:
            logger.warning("build_index called with empty document list.")
            return

        try:
            import faiss
            import numpy as np

            self._documents = documents
            embeddings = self._embedder.encode(documents, show_progress_bar=False)
            embeddings = embeddings.astype("float32")

            dim   = embeddings.shape[1]
            index = faiss.IndexFlatL2(dim)
            index.add(embeddings)

            self._vector_store = index
            self._metadata     = metadata or [{} for _ in documents]

            # Persist to disk
            os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
            faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "index.faiss"))
            with open(os.path.join(VECTOR_STORE_PATH, "documents.json"), "w") as f:
                json.dump(
                    {"documents": documents, "metadata": self._metadata}, f, indent=2
                )
            logger.info(f"✅  FAISS index built with {len(documents)} documents.")

        except Exception as exc:
            logger.error(f"build_index error: {exc}")

    # ── Load existing index from disk ─────────────────────────────────────────
    def load_index(self) -> bool:
        idx_path = os.path.join(VECTOR_STORE_PATH, "index.faiss")
        doc_path = os.path.join(VECTOR_STORE_PATH, "documents.json")

        if not (os.path.exists(idx_path) and os.path.exists(doc_path)):
            return False

        try:
            import faiss
            self._vector_store = faiss.read_index(idx_path)
            with open(doc_path) as f:
                data = json.load(f)
            self._documents = data["documents"]
            self._metadata  = data.get("metadata", [])
            logger.info(f"✅  FAISS index loaded ({len(self._documents)} docs).")
            return True
        except Exception as exc:
            logger.error(f"load_index error: {exc}")
            return False

    # ── Retrieve top-k relevant documents ─────────────────────────────────────
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """
        Find the top-k most relevant documents for `query`.

        Returns list of {"text": ..., "score": ..., "metadata": ...}
        """
        if self._vector_store is None:
            if not self.load_index():
                logger.warning("No FAISS index available – returning empty results.")
                return []

        try:
            import numpy as np
            query_vec = self._embedder.encode([query]).astype("float32")
            distances, indices = self._vector_store.search(query_vec, k)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self._documents):
                    results.append({
                        "text":     self._documents[idx],
                        "score":    float(1 / (1 + dist)),   # convert L2 to similarity
                        "metadata": self._metadata[idx] if self._metadata else {},
                    })
            return results

        except Exception as exc:
            logger.error(f"retrieve error: {exc}")
            return []

    # ── Index the question bank (called at session start) ─────────────────────
    def index_question_bank(self):
        """Pull all questions from DB and build the FAISS index."""
        try:
            from backend.models.database import QuestionBank
            questions = QuestionBank.query.all()
            if not questions:
                logger.warning("Question bank is empty – skipping RAG indexing.")
                return

            docs = []
            meta = []
            for q in questions:
                docs.append(
                    f"Role: {q.job_role}\n"
                    f"Category: {q.category}\n"
                    f"Level: {q.experience}\n"
                    f"Q: {q.question}\n"
                    f"A: {q.model_answer or ''}"
                )
                meta.append({
                    "id":         q.id,
                    "job_role":   q.job_role,
                    "category":   q.category,
                    "experience": q.experience,
                })

            self.build_index(docs, meta)
        except Exception as exc:
            logger.error(f"index_question_bank error: {exc}")

    # ── Index resume text alongside question bank ─────────────────────────────
    def index_resume(self, resume_text: str, job_role: str):
        """
        Append resume chunks to the existing index so questions can be
        contextualised with the candidate's own experience.
        """
        if not resume_text:
            return

        chunk_size = 500
        chunks = [resume_text[i : i + chunk_size] for i in range(0, len(resume_text), chunk_size)]
        meta   = [{"source": "resume", "job_role": job_role} for _ in chunks]

        existing_docs = self._documents or []
        existing_meta = self._metadata  or []

        self.build_index(existing_docs + chunks, existing_meta + meta)


# ── Singleton ─────────────────────────────────────────────────────────────────
_rag_instance: Optional[RAGService] = None


def get_rag() -> RAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance