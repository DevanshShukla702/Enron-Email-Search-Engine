"""
backend/app/retrieval/rrf_retriever.py

Hybrid Reciprocal Rank Fusion (RRF) Retrieval Model:
Combines rankings from TF-IDF, BM25, and Dense Sentence Transformer models.
Formula: RRF_score(d) = sum_{m in Methods} 1 / (k + rank_m(d))
Default constant: k = 60
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from backend.app.config import settings
from backend.app.retrieval.base import BaseRetriever
from backend.app.retrieval.result_types import RetrievedDoc
from backend.app.retrieval.tfidf_retriever import TfidfRetriever
from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.dense_retriever import DenseRetriever


class HybridRRFRetriever(BaseRetriever):
    def __init__(
        self,
        tfidf_retriever: TfidfRetriever,
        bm25_retriever: BM25Retriever,
        dense_retriever: DenseRetriever,
        k: int = settings.RRF_K
    ):
        self.tfidf = tfidf_retriever
        self.bm25 = bm25_retriever
        self.dense = dense_retriever
        self.k = k

    @property
    def name(self) -> str:
        return "rrf"

    def is_ready(self) -> bool:
        return self.tfidf.is_ready() and self.bm25.is_ready() and self.dense.is_ready()

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        if not self.is_ready():
            raise RuntimeError("One or more underlying retrieval indexes are not ready.")

        # Retrieve top candidate pool from each individual retriever (e.g. top 60 candidates)
        pool_size = max(top_k * 4, 60)
        tfidf_results = self.tfidf.search(query, top_k=pool_size, filters=filters)
        bm25_results = self.bm25.search(query, top_k=pool_size, filters=filters)
        dense_results = self.dense.search(query, top_k=pool_size, filters=filters)

        # Map document_id -> doc object
        docs_by_id: Dict[str, RetrievedDoc] = {}
        rrf_scores: Dict[str, float] = defaultdict(float)
        rank_details: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # 1. Process TF-IDF ranks
        for item in tfidf_results:
            d_id = item.document_id
            docs_by_id[d_id] = item
            contrib = 1.0 / (self.k + item.rank)
            rrf_scores[d_id] += contrib
            rank_details[d_id]["tfidf_rank"] = item.rank
            rank_details[d_id]["tfidf_contrib"] = round(contrib, 6)

        # 2. Process BM25 ranks
        for item in bm25_results:
            d_id = item.document_id
            if d_id not in docs_by_id:
                docs_by_id[d_id] = item
            contrib = 1.0 / (self.k + item.rank)
            rrf_scores[d_id] += contrib
            rank_details[d_id]["bm25_rank"] = item.rank
            rank_details[d_id]["bm25_contrib"] = round(contrib, 6)

        # 3. Process Dense ranks
        for item in dense_results:
            d_id = item.document_id
            if d_id not in docs_by_id:
                docs_by_id[d_id] = item
            contrib = 1.0 / (self.k + item.rank)
            rrf_scores[d_id] += contrib
            rank_details[d_id]["dense_rank"] = item.rank
            rank_details[d_id]["dense_contrib"] = round(contrib, 6)

        # Sort documents by descending RRF score
        sorted_doc_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        final_results: List[RetrievedDoc] = []
        rank = 1
        for d_id in sorted_doc_ids[:top_k]:
            orig = docs_by_id[d_id]
            final_score = rrf_scores[d_id]
            det = rank_details[d_id]

            final_results.append(
                RetrievedDoc(
                    document_id=d_id,
                    rank=rank,
                    score=round(final_score, 6),
                    subject=orig.subject,
                    sender=orig.sender,
                    recipients=orig.recipients,
                    date=orig.date,
                    folder=orig.folder,
                    snippet=orig.snippet,
                    thread_id=orig.thread_id,
                    explanation={
                        "method": "rrf",
                        "rrf_k": self.k,
                        "rrf_score": round(final_score, 6),
                        "tfidf_rank": det.get("tfidf_rank"),
                        "tfidf_contrib": det.get("tfidf_contrib", 0.0),
                        "bm25_rank": det.get("bm25_rank"),
                        "bm25_contrib": det.get("bm25_contrib", 0.0),
                        "dense_rank": det.get("dense_rank"),
                        "dense_contrib": det.get("dense_contrib", 0.0),
                        "models_contributing": len(det) // 2
                    }
                )
            )
            rank += 1

        return final_results
