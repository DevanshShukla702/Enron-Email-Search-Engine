"""
backend/app/api/search.py

Search and email detail endpoints.
Supports TF-IDF, BM25, Dense, and Hybrid RRF retrieval with metadata filtering.
"""

import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends

from backend.app.schemas import (
    SearchRequest,
    SearchResponse,
    CompareResponse,
    EmailDetail,
    ThreadResponse,
    SearchResultItem
)
from backend.app.retrieval.result_types import RetrievedDoc
from backend.app.retrieval.tfidf_retriever import TfidfRetriever
from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.dense_retriever import DenseRetriever
from backend.app.retrieval.rrf_retriever import HybridRRFRetriever
from backend.app.storage.repository import EmailRepository
from backend.app.config import settings

router = APIRouter(prefix="/api", tags=["search"])

# Module-level instances initialized at startup
_repo: Optional[EmailRepository] = None
_tfidf: Optional[TfidfRetriever] = None
_bm25: Optional[BM25Retriever] = None
_dense: Optional[DenseRetriever] = None
_rrf: Optional[HybridRRFRetriever] = None


def init_search_engines():
    global _repo, _tfidf, _bm25, _dense, _rrf
    _repo = EmailRepository(settings.DATABASE_PATH)
    _tfidf = TfidfRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)
    _bm25 = BM25Retriever(settings.INDEX_DIR, settings.DATABASE_PATH, k1=settings.BM25_K1, b=settings.BM25_B)
    _dense = DenseRetriever(settings.INDEX_DIR, settings.DATABASE_PATH, model_name=settings.DENSE_MODEL_NAME)
    _rrf = HybridRRFRetriever(_tfidf, _bm25, _dense, k=settings.RRF_K)


def get_retriever(method: str):
    method = method.lower()
    if method == "tfidf":
        return _tfidf
    elif method == "bm25":
        return _bm25
    elif method == "dense":
        return _dense
    elif method == "rrf":
        return _rrf
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported retrieval method: '{method}'. Choose from: tfidf, bm25, dense, rrf."
        )


def doc_to_schema(doc: RetrievedDoc) -> SearchResultItem:
    return SearchResultItem(
        document_id=doc.document_id,
        rank=doc.rank,
        score=doc.score,
        subject=doc.subject,
        sender=doc.sender,
        recipients=doc.recipients,
        date=doc.date,
        folder=doc.folder,
        snippet=doc.snippet,
        thread_id=doc.thread_id,
        explanation=doc.explanation
    )


@router.post("/search", response_model=SearchResponse)
def execute_search(request: SearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query must contain at least one non-whitespace character.")

    retriever = get_retriever(request.method)
    if not retriever or not retriever.is_ready():
        raise HTTPException(
            status_code=503,
            detail=f"Retriever '{request.method}' is not initialized or index is missing. Please run build scripts."
        )

    filters = request.filters.model_dump(exclude_none=True) if request.filters else None

    start_time = time.perf_counter()
    try:
        results = retriever.search(query, top_k=request.top_k, filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Thread grouping if requested
    if request.thread_mode:
        seen_threads = set()
        deduped = []
        for r in results:
            t_id = r.thread_id
            if t_id:
                if t_id not in seen_threads:
                    seen_threads.add(t_id)
                    deduped.append(r)
            else:
                deduped.append(r)
        results = deduped[:request.top_k]

    return SearchResponse(
        query=query,
        method=request.method,
        total_results=len(results),
        execution_time_ms=round(elapsed_ms, 2),
        results=[doc_to_schema(d) for d in results]
    )


@router.post("/search/compare", response_model=CompareResponse)
def compare_all_models(request: SearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query must contain at least one non-whitespace character.")

    filters = request.filters.model_dump(exclude_none=True) if request.filters else None

    start_time = time.perf_counter()
    try:
        tfidf_res = _tfidf.search(query, top_k=request.top_k, filters=filters)
        bm25_res = _bm25.search(query, top_k=request.top_k, filters=filters)
        dense_res = _dense.search(query, top_k=request.top_k, filters=filters)
        rrf_res = _rrf.search(query, top_k=request.top_k, filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison execution error: {str(e)}")

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return CompareResponse(
        query=query,
        execution_time_ms=round(elapsed_ms, 2),
        tfidf=[doc_to_schema(d) for d in tfidf_res],
        bm25=[doc_to_schema(d) for d in bm25_res],
        dense=[doc_to_schema(d) for d in dense_res],
        rrf=[doc_to_schema(d) for d in rrf_res]
    )


@router.get("/email/{document_id}", response_model=EmailDetail)
def get_email_detail(document_id: str):
    email = _repo.get_email_by_id(document_id)
    if not email:
        raise HTTPException(status_code=404, detail=f"Email with ID '{document_id}' not found.")
    return EmailDetail(
        document_id=email["document_id"],
        message_id=email.get("message_id"),
        sender=email.get("sender") or "",
        sender_name=email.get("sender_name"),
        recipients=email.get("recipients") or "",
        cc=email.get("cc"),
        bcc=email.get("bcc"),
        subject=email.get("subject") or "(No Subject)",
        date=email.get("date"),
        mailbox=email.get("mailbox"),
        folder=email.get("folder"),
        body=email.get("body") or "",
        thread_id=email.get("thread_id"),
        file_path=email.get("file_path")
    )


@router.get("/thread/{thread_id}", response_model=ThreadResponse)
def get_thread_view(thread_id: str):
    messages = _repo.get_emails_by_thread(thread_id)
    if not messages:
        raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found or empty.")

    details = [
        EmailDetail(
            document_id=m["document_id"],
            message_id=m.get("message_id"),
            sender=m.get("sender") or "",
            sender_name=m.get("sender_name"),
            recipients=m.get("recipients") or "",
            cc=m.get("cc"),
            bcc=m.get("bcc"),
            subject=m.get("subject") or "(No Subject)",
            date=m.get("date"),
            mailbox=m.get("mailbox"),
            folder=m.get("folder"),
            body=m.get("body") or "",
            thread_id=m.get("thread_id"),
            file_path=m.get("file_path")
        )
        for m in messages
    ]

    subject = details[0].subject if details else "(Empty Thread)"

    return ThreadResponse(
        thread_id=thread_id,
        subject=subject,
        message_count=len(details),
        messages=details
    )
