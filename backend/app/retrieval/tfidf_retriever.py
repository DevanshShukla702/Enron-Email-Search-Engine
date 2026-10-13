"""
backend/app/retrieval/tfidf_retriever.py

Classical TF-IDF retrieval model utilizing scikit-learn TfidfVectorizer
and cosine similarity over preprocessed sparse text representations.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from scipy.sparse import load_npz, csr_matrix

from backend.app.config import settings
from backend.app.retrieval.base import BaseRetriever
from backend.app.retrieval.result_types import RetrievedDoc, make_snippet
from backend.app.core.preprocessing import default_preprocessor
from backend.app.storage.repository import EmailRepository

logger = logging.getLogger("tfidf_retriever")


class TfidfRetriever(BaseRetriever):
    def __init__(
        self,
        index_dir: Path = settings.INDEX_DIR,
        db_path: Path = settings.DATABASE_PATH
    ):
        self.index_dir = index_dir
        self.db_path = db_path
        self.vectorizer = None
        self.tfidf_matrix: Optional[csr_matrix] = None
        self.doc_ids: List[str] = []
        self.doc_id_to_idx: Dict[str, int] = {}
        self.repo = EmailRepository(db_path)
        self._load_index()

    @property
    def name(self) -> str:
        return "tfidf"

    def _load_index(self):
        vec_path = self.index_dir / "tfidf_vectorizer.pkl"
        mat_path = self.index_dir / "tfidf_matrix.npz"
        doc_path = self.index_dir / "tfidf_doc_ids.json"

        if vec_path.exists() and mat_path.exists() and doc_path.exists():
            try:
                with open(vec_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                self.tfidf_matrix = load_npz(mat_path)
                with open(doc_path, "r", encoding="utf-8") as f:
                    self.doc_ids = json.load(f)
                self.doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(self.doc_ids)}
                logger.info(f"Loaded TF-IDF index with {len(self.doc_ids):,} documents.")
            except Exception as e:
                logger.error(f"Failed to load TF-IDF index: {e}")
        else:
            logger.warning("TF-IDF index files not found. Run python scripts/build_tfidf_index.py.")

    def is_ready(self) -> bool:
        return (
            self.vectorizer is not None
            and self.tfidf_matrix is not None
            and len(self.doc_ids) > 0
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        if not self.is_ready():
            raise RuntimeError("TF-IDF index is not built or loaded. Run python scripts/build_tfidf_index.py.")

        proc_query = default_preprocessor.preprocess(query)
        if not proc_query:
            proc_query = query.lower()

        # Vectorize query
        q_vec = self.vectorizer.transform([proc_query])
        if q_vec.nnz == 0:
            return []

        # Cosine similarity: (M * q^T)
        scores = self.tfidf_matrix.dot(q_vec.T).toarray().ravel()

        # Find top matching candidates
        # Fetch more if filters are applied
        fetch_limit = min(len(scores), top_k * 10 if filters else top_k)
        if fetch_limit == 0:
            return []

        # Partition top candidates
        cand_indices = np.argpartition(scores, -fetch_limit)[-fetch_limit:]
        sorted_indices = cand_indices[np.argsort(-scores[cand_indices])]

        results: List[RetrievedDoc] = []
        doc_ids_to_fetch = [self.doc_ids[idx] for idx in sorted_indices if scores[idx] > 0.0]
        if not doc_ids_to_fetch:
            return []

        # Retrieve documents from database
        docs_map = self.repo.get_emails_by_ids(doc_ids_to_fetch)

        rank = 1
        for idx in sorted_indices:
            score = float(scores[idx])
            if score <= 0.0:
                continue

            doc_id = self.doc_ids[idx]
            doc = docs_map.get(doc_id)
            if not doc:
                continue

            # Apply filters if present
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
                    score=round(score, 5),
                    subject=doc.get("subject") or "(No Subject)",
                    sender=doc.get("sender") or "",
                    recipients=doc.get("recipients") or "",
                    date=doc.get("date"),
                    folder=doc.get("folder"),
                    snippet=snippet,
                    thread_id=doc.get("thread_id"),
                    explanation={
                        "method": "tfidf",
                        "raw_score": round(score, 5),
                        "cosine_similarity": round(score, 5),
                        "terms_matched": [t for t in proc_query.split() if t in self.vectorizer.vocabulary_]
                    }
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results
