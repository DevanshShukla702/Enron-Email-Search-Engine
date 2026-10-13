"""
backend/app/main.py

FastAPI Application Entrypoint for Enron Email IR System.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Suppress noisy third-party loggers before anything else loads ──────────────
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")       # suppress tokenizer fork warning
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")       # suppress HF transformers chatter
os.environ.setdefault("HF_HUB_VERBOSITY", "warning")           # suppress HF Hub unauthenticated banner
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")    # suppress HF download progress bars

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

# Silence verbose third-party loggers
for _noisy in (
    "httpx",
    "httpcore",
    "huggingface_hub",
    "huggingface_hub.utils._http",
    "sentence_transformers",
    "sentence_transformers.base.model",
    "transformers",
    "faiss",
):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

logger = logging.getLogger("main")

from backend.app.config import settings
from backend.app.api.search import router as search_router, init_search_engines
from backend.app.api.evaluation import router as evaluation_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Enron Email IR search engines and preloaded indexes...")
    init_search_engines()
    logger.info("Search engines ready.")
    yield
    logger.info("Shutting down IR server.")


app = FastAPI(
    title="Enron Email Information Retrieval System",
    description="Academic IR engine implementing TF-IDF, BM25, Sentence Transformer Dense, and Hybrid RRF retrieval.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(search_router)
app.include_router(evaluation_router)
app.include_router(analytics_router)
app.include_router(health_router)


@app.get("/")
def root():
    return {
        "title": "Enterprise Email Retrieval Engine",
        "description": "Multi-paradigm Information Retrieval system (TF-IDF, BM25, Dense Sentence Transformers, Hybrid RRF)",
        "version": "1.0.0",
        "dataset_mode": settings.DATASET_MODE,
        "docs": "/docs",
        "endpoints": {
            "search": "/api/search",
            "compare": "/api/search/compare",
            "evaluation": "/api/evaluation/summary",
            "analytics": "/api/analytics/overview",
            "health": "/api/health"
        }
    }
