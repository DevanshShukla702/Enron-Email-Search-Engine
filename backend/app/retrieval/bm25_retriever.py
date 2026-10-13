"""
backend/app/retrieval/bm25_retriever.py

Probabilistic BM25 (Okapi BM25) retrieval model with configurable k1 and b parameters.
Searches over preprocessed tokenized documents.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi

from backend.app.config import settings
from backend.app.retrieval.base import BaseRetriever
from backend.app.retrieval.result_types import RetrievedDoc, make_snippet
from backend.app.core.preprocessing import default_preprocessor
from backend.app.storage.repository import EmailRepository

logger = logging.getLogger("bm25_retriever")


class BM25Retriever(BaseRetriever):
    def __init__(
        self,
        index_dir: Path = settings.INDEX_DIR,
        db_path: Path = settings.DATABASE_PATH,
        k1: float = settings.BM25_K1,
        b: float = settings.BM25_B
    ):
        self.index_dir = index_dir
        self.db_path = db_path
        self.k1 = k1
        self.b = b
        self.bm25: Optional[BM25Okapi] = None
        self.doc_ids: List[str] = []
        self.repo = EmailRepository(db_path)
        self._load_index()

    @property
    def name(self) -> str:
        return "bm25"

    def _load_index(self):
        index_path = self.index_dir / "bm25_index.pkl"
        doc_path = self.index_dir / "bm25_doc_ids.json"

        if index_path.exists() and doc_path.exists():
            try:
                with open(index_path, "rb") as f:
                    self.bm25 = pickle.load(f)
                with open(doc_path, "r", encoding="utf-8") as f:
                    self.doc_ids = json.load(f)
                logger.info(f"Loaded BM25 index with {len(self.doc_ids):,} documents (k1={self.k1}, b={self.b}).")
            except Exception as e:
                logger.error(f"Failed to load BM25 index: {e}")
        else:
            logger.warning("BM25 index files not found. Run python scripts/build_bm25_index.py.")

    def is_ready(self) -> bool:
        return self.bm25 is not None and len(self.doc_ids) > 0

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        if not self.is_ready():
            raise RuntimeError("BM25 index is not loaded. Run python scripts/build_bm25_index.py.")

        tokens = default_preprocessor.preprocess_tokens(query)
        if not tokens:
            tokens = [t.lower() for t in query.split() if t.isalnum()]

        if not tokens:
            return []

        # Compute Okapi BM25 scores
        scores = self.bm25.get_scores(tokens)
        if not isinstance(scores, np.ndarray):
            scores = np.array(scores)

        # Retrieve top candidates
        fetch_limit = min(len(scores), top_k * 10 if filters else top_k)
        if fetch_limit == 0:
            return []

        cand_indices = np.argpartition(scores, -fetch_limit)[-fetch_limit:]
        sorted_indices = cand_indices[np.argsort(-scores[cand_indices])]

        doc_ids_to_fetch = [self.doc_ids[idx] for idx in sorted_indices if scores[idx] > 0.0]
        if not doc_ids_to_fetch:
            return []

        docs_map = self.repo.get_emails_by_ids(doc_ids_to_fetch)

        results: List[RetrievedDoc] = []
        rank = 1
        for idx in sorted_indices:
            score = float(scores[idx])
            if score <= 0.0:
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
                    score=round(score, 4),
                    subject=doc.get("subject") or "(No Subject)",
                    sender=doc.get("sender") or "",
                    recipients=doc.get("recipients") or "",
                    date=doc.get("date"),
                    folder=doc.get("folder"),
                    snippet=snippet,
                    thread_id=doc.get("thread_id"),
                    explanation={
                        "method": "bm25",
                        "raw_score": round(score, 4),
                        "k1": self.k1,
                        "b": self.b,
                        "query_tokens": tokens
                    }
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results
