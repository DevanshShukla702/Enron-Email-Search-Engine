"""
backend/app/retrieval/dense_retriever.py

Dense semantic retrieval model using SentenceTransformers (all-MiniLM-L6-v2)
and FAISS (IndexFlatIP) for fast vector similarity search.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from sentence_transformers import SentenceTransformer

from backend.app.config import settings
from backend.app.retrieval.base import BaseRetriever
from backend.app.retrieval.result_types import RetrievedDoc, make_snippet
from backend.app.storage.repository import EmailRepository

logger = logging.getLogger("dense_retriever")


class DenseRetriever(BaseRetriever):
    def __init__(
        self,
        index_dir: Path = settings.INDEX_DIR,
        db_path: Path = settings.DATABASE_PATH,
        model_name: str = settings.DENSE_MODEL_NAME
    ):
        self.index_dir = index_dir
        self.db_path = db_path
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.faiss_index = None
        self.embeddings: Optional[np.ndarray] = None
        self.doc_ids: List[str] = []
        self.repo = EmailRepository(db_path)
        self._load_index()

    @property
    def name(self) -> str:
        return "dense"

    def _load_index(self):
        index_path = self.index_dir / "dense_index.faiss"
        emb_path = self.index_dir / "dense_embeddings.npy"
        doc_path = self.index_dir / "dense_doc_ids.json"

        if (index_path.exists() or emb_path.exists()) and doc_path.exists():
            try:
                logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
                self.model = SentenceTransformer(self.model_name)

                with open(doc_path, "r", encoding="utf-8") as f:
                    self.doc_ids = json.load(f)

                if index_path.exists() and HAS_FAISS:
                    self.faiss_index = faiss.read_index(str(index_path))
                    logger.info(f"Loaded FAISS dense index with {self.faiss_index.ntotal:,} vectors.")
                elif emb_path.exists():
                    self.embeddings = np.load(emb_path)
                    logger.info(f"Loaded dense numpy embeddings matrix: {self.embeddings.shape}")
            except Exception as e:
                logger.error(f"Failed to load dense retriever: {e}")
        else:
            logger.warning("Dense index files not found. Run python scripts/build_dense_index.py.")

    def is_ready(self) -> bool:
        has_vectors = (self.faiss_index is not None) or (self.embeddings is not None)
        return self.model is not None and has_vectors and len(self.doc_ids) > 0

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        if not self.is_ready():
            raise RuntimeError("Dense retriever is not loaded. Run python scripts/build_dense_index.py.")

        # Encode query to normalized 384-d vector
        query_vector = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype(np.float32)

        fetch_limit = min(len(self.doc_ids), top_k * 10 if filters else top_k)
        if fetch_limit == 0:
            return []

        if self.faiss_index is not None:
            distances, indices = self.faiss_index.search(query_vector, fetch_limit)
            sorted_indices = indices[0]
            scores = distances[0]
        else:
            # Fallback to normalized inner product dot
            scores_all = np.dot(self.embeddings, query_vector[0])
            sorted_indices = np.argsort(-scores_all)[:fetch_limit]
            scores = scores_all[sorted_indices]

        doc_ids_to_fetch = [self.doc_ids[idx] for idx in sorted_indices if idx >= 0]
        docs_map = self.repo.get_emails_by_ids(doc_ids_to_fetch)

        results: List[RetrievedDoc] = []
        rank = 1
        for idx, score in zip(sorted_indices, scores):
            if idx < 0:
                continue

            doc_id = self.doc_ids[idx]
            doc = docs_map.get(doc_id)
            if not doc:
                continue

            # Apply filters
            if filters:
                if filters.get("sender") and filters["sender"].lower() not in (doc.get("sender") or "").lower():
                    continue
                if filters.get("folder") and filters["folder"].lower() not in (doc.get("folder") or "").lower():
                    continue
                if filters.get("date_from") and (doc.get("date") or "") < filters["date_from"]:
                    continue
                if filters.get("date_to") and (doc.get("date") or "") > filters["date_to"]:
                    continue

            snippet = make_snippet(doc.get("body") or "", query)

            results.append(
                RetrievedDoc(
                    document_id=doc_id,
                    rank=rank,
                    score=round(float(score), 4),
                    subject=doc.get("subject") or "(No Subject)",
                    sender=doc.get("sender") or "",
                    recipients=doc.get("recipients") or "",
                    date=doc.get("date"),
                    folder=doc.get("folder"),
                    snippet=snippet,
                    thread_id=doc.get("thread_id"),
                    explanation={
                        "method": "dense",
                        "model": self.model_name,
                        "semantic_similarity": round(float(score), 4),
                        "embedding_dimension": 384
                    }
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results
