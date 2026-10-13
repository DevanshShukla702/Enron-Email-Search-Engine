"""
backend/app/evaluation/metrics.py

Rigorous academic Information Retrieval evaluation metrics:
- Precision@K
- Recall
- Average Precision (AP) & Mean Average Precision (MAP)
- Graded Normalized Discounted Cumulative Gain (nDCG@K)
- 11-Point Interpolated Precision-Recall Curve Generation
"""

import math
from typing import List, Dict, Tuple, Optional


def precision_at_k(
    retrieved_doc_ids: List[str],
    qrels: Dict[str, int],
    k: int = 10,
    relevance_threshold: int = 1
) -> float:
    """
    Precision at rank K:
    Fraction of top K retrieved documents that are relevant (rel >= threshold).
    Handles edge cases: k <= 0, empty retrievals, fewer than k items.
    """
    if k <= 0:
        return 0.0
    if not retrieved_doc_ids:
        return 0.0

    top_k = retrieved_doc_ids[:k]
    relevant_retrieved = sum(
        1 for doc_id in top_k
        if qrels.get(doc_id, 0) >= relevance_threshold
    )
    return relevant_retrieved / float(k)


def recall(
    retrieved_doc_ids: List[str],
    qrels: Dict[str, int],
    relevance_threshold: int = 1
) -> float:
    """
    Recall:
    Fraction of all relevant documents that were retrieved.
    If there are no relevant documents in qrels, returns 0.0.
    """
    total_relevant = sum(1 for rel in qrels.values() if rel >= relevance_threshold)
    if total_relevant == 0:
        return 0.0
    if not retrieved_doc_ids:
        return 0.0

    # Ensure unique retrieved documents
    seen = set()
    retrieved_unique = []
    for d in retrieved_doc_ids:
        if d not in seen:
            seen.add(d)
            retrieved_unique.append(d)

    relevant_retrieved = sum(
        1 for doc_id in retrieved_unique
        if qrels.get(doc_id, 0) >= relevance_threshold
    )
    return relevant_retrieved / float(total_relevant)


def average_precision(
    retrieved_doc_ids: List[str],
    qrels: Dict[str, int],
    relevance_threshold: int = 1
) -> float:
    """
    Average Precision (AP) for a single query:
    Area under the precision-recall curve across all retrieved ranks.
    AP = sum_{k=1}^N (P@k * rel(k)) / total_relevant
    """
    total_relevant = sum(1 for rel in qrels.values() if rel >= relevance_threshold)
    if total_relevant == 0:
        return 0.0
    if not retrieved_doc_ids:
        return 0.0

    cumulative_relevant = 0
    precision_sum = 0.0

    seen = set()
    rank = 0
    for doc_id in retrieved_doc_ids:
        if doc_id in seen:
            continue
        seen.add(doc_id)
        rank += 1

        rel = qrels.get(doc_id, 0)
        if rel >= relevance_threshold:
            cumulative_relevant += 1
            precision_at_current_rank = cumulative_relevant / float(rank)
            precision_sum += precision_at_current_rank

    return precision_sum / float(total_relevant)


def mean_average_precision(
    all_query_retrievals: Dict[str, List[str]],
    all_qrels: Dict[str, Dict[str, int]],
    relevance_threshold: int = 1
) -> float:
    """
    Mean Average Precision (MAP) across multiple queries:
    MAP = (1 / |Q|) * sum_{q in Q} AP(q)
    """
    if not all_query_retrievals:
        return 0.0

    ap_scores = []
    for query_id, retrieved in all_query_retrievals.items():
        qrels = all_qrels.get(query_id, {})
        ap = average_precision(retrieved, qrels, relevance_threshold=relevance_threshold)
        ap_scores.append(ap)

    return sum(ap_scores) / float(len(ap_scores)) if ap_scores else 0.0


def dcg_at_k(
    retrieved_doc_ids: List[str],
    qrels: Dict[str, int],
    k: int = 10
) -> float:
    """
    Discounted Cumulative Gain at rank K using graded relevance:
    DCG@K = sum_{i=1}^K (2^{rel_i} - 1) / log_2(i + 1)
    """
    if k <= 0 or not retrieved_doc_ids:
        return 0.0

    dcg = 0.0
    top_k = retrieved_doc_ids[:k]
    for i, doc_id in enumerate(top_k, 1):
        rel = qrels.get(doc_id, 0)
        gain = (2.0 ** rel) - 1.0
        discount = math.log2(i + 1.0)
        dcg += gain / discount
    return dcg


def ndcg_at_k(
    retrieved_doc_ids: List[str],
    qrels: Dict[str, int],
    k: int = 10
) -> float:
    """
    Normalized Discounted Cumulative Gain at rank K:
    nDCG@K = DCG@K / IDCG@K
    IDCG is computed from the ideally sorted list of relevant judgments.
    """
    if k <= 0 or not retrieved_doc_ids:
        return 0.0

    actual_dcg = dcg_at_k(retrieved_doc_ids, qrels, k=k)

    # Ideal ranking: sort all available qrels relevance descending
    sorted_ideal_rels = sorted(qrels.values(), reverse=True)
    if not sorted_ideal_rels or sorted_ideal_rels[0] <= 0:
        return 0.0

    ideal_dcg = 0.0
    for i, rel in enumerate(sorted_ideal_rels[:k], 1):
        gain = (2.0 ** rel) - 1.0
        discount = math.log2(i + 1.0)
        ideal_dcg += gain / discount

    if ideal_dcg <= 0.0:
        return 0.0

    return min(1.0, actual_dcg / ideal_dcg)


def compute_precision_recall_curve(
    retrieved_doc_ids: List[str],
    qrels: Dict[str, int],
    relevance_threshold: int = 1
) -> List[Tuple[float, float]]:
    """
    Calculate the standard 11-point interpolated Precision-Recall curve:
    Recall levels: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    p_interp(r) = max_{r' >= r} p(r')
    """
    standard_recall_levels = [round(i * 0.1, 1) for i in range(11)]
    total_relevant = sum(1 for rel in qrels.values() if rel >= relevance_threshold)
    if total_relevant == 0 or not retrieved_doc_ids:
        return [(r, 0.0) for r in standard_recall_levels]

    precisions = []
    recalls = []
    cumulative_relevant = 0

    seen = set()
    rank = 0
    for doc_id in retrieved_doc_ids:
        if doc_id in seen:
            continue
        seen.add(doc_id)
        rank += 1

        rel = qrels.get(doc_id, 0)
        if rel >= relevance_threshold:
            cumulative_relevant += 1
            prec = cumulative_relevant / float(rank)
            rec = cumulative_relevant / float(total_relevant)
            precisions.append(prec)
            recalls.append(rec)

    if not precisions:
        return [(r, 0.0) for r in standard_recall_levels]

    # Compute 11-point interpolated precision
    interpolated_curve = []
    for r in standard_recall_levels:
        # Find all precisions at recall >= r
        valid_prec = [p for p, rec in zip(precisions, recalls) if rec >= r]
        p_interp = max(valid_prec) if valid_prec else 0.0
        interpolated_curve.append((r, round(p_interp, 4)))

    return interpolated_curve
