"""
backend/app/api/health.py

System health, corpus stats, and runtime configuration endpoints.
"""

from fastapi import APIRouter
from backend.app.config import settings
from backend.app.storage.repository import EmailRepository
from backend.app.retrieval.tfidf_retriever import TfidfRetriever
from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.dense_retriever import DenseRetriever

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    repo = EmailRepository(settings.DATABASE_PATH)
    try:
        count = repo.count_emails()
        db_ok = True
    except Exception:
        count = 0
        db_ok = False

    tfidf = TfidfRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)
    bm25 = BM25Retriever(settings.INDEX_DIR, settings.DATABASE_PATH)
    dense = DenseRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)

    indexes_ready = {
        "tfidf": tfidf.is_ready(),
        "bm25": bm25.is_ready(),
        "dense": dense.is_ready()
    }
    all_ok = db_ok and all(indexes_ready.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "database_connected": db_ok,
        "indexed_documents": count,
        "dataset_mode": settings.DATASET_MODE,
        "indexes": indexes_ready
    }


@router.get("/stats")
def corpus_stats():
    repo = EmailRepository(settings.DATABASE_PATH)
    count = repo.count_emails()
    return {
        "total_documents": count,
        "dataset_mode": settings.DATASET_MODE,
        "database_path": str(settings.DATABASE_PATH),
        "index_dir": str(settings.INDEX_DIR),
        "dense_model": settings.DENSE_MODEL_NAME
    }


@router.get("/config")
def get_runtime_config():
    return {
        "dataset_mode": settings.DATASET_MODE,
        "demo_email_limit": settings.DEMO_EMAIL_LIMIT,
        "dense_model_name": settings.DENSE_MODEL_NAME,
        "default_top_k": settings.DEFAULT_TOP_K,
        "rrf_k": settings.RRF_K,
        "bm25_k1": settings.BM25_K1,
        "bm25_b": settings.BM25_B,
        "weights": {
            "subject": settings.WEIGHT_SUBJECT,
            "body": settings.WEIGHT_BODY,
            "sender": settings.WEIGHT_SENDER,
            "recipients": settings.WEIGHT_RECIPIENTS
        }
    }
