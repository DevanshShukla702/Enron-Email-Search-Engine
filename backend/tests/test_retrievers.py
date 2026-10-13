"""
Integration tests for search retrievers against built indexes.
"""

import pytest
from backend.app.config import settings
from backend.app.retrieval.tfidf_retriever import TfidfRetriever
from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.dense_retriever import DenseRetriever
from backend.app.retrieval.result_types import make_snippet


def test_snippet_generation():
    text = "The California wholesale power market has faced severe constraints during peak periods."
    snippet = make_snippet(text, "wholesale power")
    assert "wholesale" in snippet.lower() or "power" in snippet.lower()


def test_tfidf_retriever():
    retriever = TfidfRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)
    assert retriever.is_ready()

    results = retriever.search("California power market", top_k=5)
    assert len(results) > 0
    assert results[0].score > 0.0
    assert results[0].rank == 1
    assert "explanation" in results[0].__dict__


def test_bm25_retriever():
    retriever = BM25Retriever(settings.INDEX_DIR, settings.DATABASE_PATH)
    assert retriever.is_ready()

    results = retriever.search("FERC regulatory filings", top_k=5)
    assert len(results) > 0
    assert results[0].score > 0.0
    assert results[0].rank == 1
    assert results[0].explanation["method"] == "bm25"


def test_dense_retriever():
    retriever = DenseRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)
    assert retriever.is_ready()

    results = retriever.search("employee compensation and bonuses", top_k=5)
    assert len(results) > 0
    assert results[0].score > 0.0
    assert results[0].rank == 1
    assert results[0].explanation["method"] == "dense"
