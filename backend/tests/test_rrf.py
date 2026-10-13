"""
Unit tests for Hybrid Reciprocal Rank Fusion (RRF).
Formula: RRF_score(d) = sum_{m in Methods} 1 / (k + rank_m(d))
"""

import pytest
from unittest.mock import MagicMock
from backend.app.retrieval.result_types import RetrievedDoc
from backend.app.retrieval.rrf_retriever import HybridRRFRetriever


def test_rrf_scoring_formula():
    # Mock three retrievers
    mock_tfidf = MagicMock()
    mock_bm25 = MagicMock()
    mock_dense = MagicMock()

    mock_tfidf.is_ready.return_value = True
    mock_bm25.is_ready.return_value = True
    mock_dense.is_ready.return_value = True

    # Document "doc_A" is rank 1 in TF-IDF, rank 2 in BM25, and rank 3 in Dense
    # k = 60
    # Expected RRF score = 1/(60+1) + 1/(60+2) + 1/(60+3) = 1/61 + 1/62 + 1/63 = 0.016393 + 0.016129 + 0.015873 = 0.048395
    doc_A_1 = RetrievedDoc(document_id="doc_A", rank=1, score=0.9, subject="Test A")
    doc_A_2 = RetrievedDoc(document_id="doc_A", rank=2, score=15.0, subject="Test A")
    doc_A_3 = RetrievedDoc(document_id="doc_A", rank=3, score=0.85, subject="Test A")

    doc_B_1 = RetrievedDoc(document_id="doc_B", rank=2, score=0.8, subject="Test B")
    doc_B_2 = RetrievedDoc(document_id="doc_B", rank=1, score=18.0, subject="Test B")

    mock_tfidf.search.return_value = [doc_A_1, doc_B_1]
    mock_bm25.search.return_value = [doc_B_2, doc_A_2]
    mock_dense.search.return_value = [doc_A_3]

    rrf_retriever = HybridRRFRetriever(
        tfidf_retriever=mock_tfidf,
        bm25_retriever=mock_bm25,
        dense_retriever=mock_dense,
        k=60
    )

    results = rrf_retriever.search("energy", top_k=2)
    assert len(results) == 2

    # doc_A has 3 contributing models: 1/61 + 1/62 + 1/63 ≈ 0.048395
    # doc_B has 2 contributing models: 1/62 + 1/61 ≈ 0.032522
    # Therefore doc_A should be rank 1
    assert results[0].document_id == "doc_A"
    assert results[0].rank == 1
    assert results[0].score == pytest.approx(1/61 + 1/62 + 1/63, rel=1e-3)

    assert results[1].document_id == "doc_B"
    assert results[1].rank == 2
    assert results[1].score == pytest.approx(1/62 + 1/61, rel=1e-3)

    # Explanation structure
    exp = results[0].explanation
    assert exp["method"] == "rrf"
    assert exp["rrf_k"] == 60
    assert exp["tfidf_rank"] == 1
    assert exp["bm25_rank"] == 2
    assert exp["dense_rank"] == 3
