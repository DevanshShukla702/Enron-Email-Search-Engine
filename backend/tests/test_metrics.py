"""
Unit tests for Information Retrieval evaluation metrics:
Precision@K, Recall, MAP, and graded nDCG@K.
"""

import pytest
import math
from backend.app.evaluation.metrics import (
    precision_at_k,
    recall,
    average_precision,
    mean_average_precision,
    dcg_at_k,
    ndcg_at_k,
    compute_precision_recall_curve
)


def test_precision_at_k_normal():
    # 3 out of top 5 are relevant
    retrieved = ["d1", "d2", "d3", "d4", "d5"]
    qrels = {"d1": 1, "d2": 0, "d3": 2, "d4": 0, "d5": 1}
    p5 = precision_at_k(retrieved, qrels, k=5)
    assert p5 == pytest.approx(3 / 5.0)

    p3 = precision_at_k(retrieved, qrels, k=3)
    assert p3 == pytest.approx(2 / 3.0)


def test_precision_at_k_edge_cases():
    # Empty retrieved
    assert precision_at_k([], {"d1": 1}, k=10) == 0.0
    # No relevant docs in qrels
    assert precision_at_k(["d1", "d2"], {"d1": 0, "d2": 0}, k=2) == 0.0
    # Fewer retrieved than k
    assert precision_at_k(["d1"], {"d1": 1}, k=10) == pytest.approx(0.1)


def test_recall_normal_and_edge_cases():
    # Total relevant in qrels: 4 (d1, d2, d4, d6)
    qrels = {"d1": 2, "d2": 1, "d3": 0, "d4": 1, "d5": 0, "d6": 2}
    retrieved = ["d1", "d3", "d4"]
    # Retrieved 2 relevant (d1, d4) out of 4 total
    rec = recall(retrieved, qrels)
    assert rec == pytest.approx(2 / 4.0)

    # Empty retrieved
    assert recall([], qrels) == 0.0
    # No relevant in qrels
    assert recall(["d1", "d2"], {"d1": 0, "d2": 0}) == 0.0


def test_average_precision():
    # Ranks:
    # 1: d1 (rel=1) -> P@1 = 1/1 = 1.0
    # 2: d2 (rel=0)
    # 3: d3 (rel=1) -> P@3 = 2/3
    # Total relevant in qrels = 2
    # Expected AP = (1.0 + 2/3) / 2 = 5/6 = 0.8333
    qrels = {"d1": 1, "d3": 1}
    retrieved = ["d1", "d2", "d3"]
    ap = average_precision(retrieved, qrels)
    assert ap == pytest.approx(5.0 / 6.0)


def test_mean_average_precision():
    qrels = {
        "q1": {"d1": 1, "d2": 1},
        "q2": {"d3": 1}
    }
    retrievals = {
        "q1": ["d1", "d2"],  # AP = (1/1 + 2/2)/2 = 1.0
        "q2": ["d0", "d3"]   # AP = (1/2)/1 = 0.5
    }
    map_score = mean_average_precision(retrievals, qrels)
    assert map_score == pytest.approx(0.75)


def test_ndcg_graded_relevance():
    # Document grades: d1=2, d2=1, d3=0
    qrels = {"d1": 2, "d2": 1, "d3": 0}

    # Ideal ordering: ["d1", "d2", "d3"]
    # Gains: (2^2 - 1)/log2(2) + (2^1 - 1)/log2(3) = 3/1 + 1/1.58496 = 3.6309
    ideal_ndcg = ndcg_at_k(["d1", "d2", "d3"], qrels, k=3)
    assert ideal_ndcg == pytest.approx(1.0)

    # Sub-optimal ordering: ["d2", "d1", "d3"]
    sub_ndcg = ndcg_at_k(["d2", "d1", "d3"], qrels, k=3)
    assert sub_ndcg < 1.0
    assert sub_ndcg > 0.5

    # Completely non-relevant
    zero_ndcg = ndcg_at_k(["d3"], qrels, k=1)
    assert zero_ndcg == 0.0


def test_interpolated_precision_recall_curve():
    qrels = {"d1": 1, "d2": 1}
    retrieved = ["d1", "d0", "d2"]
    curve = compute_precision_recall_curve(retrieved, qrels)
    assert len(curve) == 11
    # Recall 0.0 should have non-zero precision
    assert curve[0][1] >= 0.5
    # Curve should be monotonically non-increasing
    for i in range(len(curve) - 1):
        assert curve[i][1] >= curve[i + 1][1]
