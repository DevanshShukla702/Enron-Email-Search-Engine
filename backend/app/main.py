"""
backend/app/main.py

FastAPI Application Entrypoint for Enron Email IR System.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.api.search import router as search_router, init_search_engines
from backend.app.api.evaluation import router as evaluation_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("main")


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
        "title": "Enterprise Email Search Engine using Enron Corpus",
        "version": "1.0.0",
        "project": "Information Retrieval Project 16",
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
