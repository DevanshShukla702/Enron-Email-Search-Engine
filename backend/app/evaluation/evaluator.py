"""
backend/app/evaluation/evaluator.py

Evaluation coordinator: Executes queries across all 4 retrieval models,
computes query-level and aggregated metrics (P@10, Recall, MAP, nDCG@10),
and computes interpolated Precision-Recall curves.
"""

from typing import Dict, Any, List
import logging
from collections import defaultdict

from backend.app.evaluation.queries import QueryItem
from backend.app.evaluation.metrics import (
    precision_at_k,
    recall,
    average_precision,
    ndcg_at_k,
    compute_precision_recall_curve
)
from backend.app.retrieval.base import BaseRetriever

logger = logging.getLogger("evaluator")


class Evaluator:
    def __init__(
        self,
        retrievers: Dict[str, BaseRetriever],
        queries: List[QueryItem],
        qrels: Dict[str, Dict[str, int]]
    ):
        self.retrievers = retrievers
        self.queries = queries
        self.qrels = qrels

    def evaluate(self, top_k: int = 50) -> Dict[str, Any]:
        """
        Run complete evaluation across all queries and models.
        """
        results_by_method = {}
        all_query_details = []

        # Standard 11-point recall levels
        recall_levels = [round(i * 0.1, 1) for i in range(11)]

        for method_name, retriever in self.retrievers.items():
            logger.info(f"Evaluating retriever: {method_name} across {len(self.queries)} queries...")

            p10_list = []
            rec_list = []
            ap_list = []
            ndcg_list = []
            pr_curves_by_query = []
            retrieval_records = {}

            for q in self.queries:
                q_id = q.query_id
                query_qrels = self.qrels.get(q_id, {})

                # Retrieve ranked documents
                retrieved_docs = retriever.search(q.query, top_k=top_k)
                retrieved_ids = [d.document_id for d in retrieved_docs]
                retrieval_records[q_id] = retrieved_ids

                # Compute query-level metrics
                p10 = precision_at_k(retrieved_ids, query_qrels, k=10)
                rec = recall(retrieved_ids, query_qrels)
                ap = average_precision(retrieved_ids, query_qrels)
                ndcg = ndcg_at_k(retrieved_ids, query_qrels, k=10)
                pr_curve = compute_precision_recall_curve(retrieved_ids, query_qrels)

                p10_list.append(p10)
                rec_list.append(rec)
                ap_list.append(ap)
                ndcg_list.append(ndcg)
                pr_curves_by_query.append(pr_curve)

                # Store per-query details for reporting
                all_query_details.append({
                    "method": method_name,
                    "query_id": q_id,
                    "query": q.query,
                    "precision_at_10": round(p10, 4),
                    "recall": round(rec, 4),
                    "average_precision": round(ap, 4),
                    "ndcg": round(ndcg, 4),
                    "retrieved_count": len(retrieved_ids),
                    "top_retrieved": retrieved_ids[:10]
                })

            # Calculate aggregated 11-point PR curve (mean across queries)
            aggregated_pr_curve = []
            for idx, r_level in enumerate(recall_levels):
                precisions_at_r = [curve[idx][1] for curve in pr_curves_by_query if len(curve) > idx]
                mean_p = sum(precisions_at_r) / len(precisions_at_r) if precisions_at_r else 0.0
                aggregated_pr_curve.append({
                    "recall": r_level,
                    "precision": round(mean_p, 4)
                })

            mean_p10 = sum(p10_list) / len(p10_list) if p10_list else 0.0
            mean_rec = sum(rec_list) / len(rec_list) if rec_list else 0.0
            map_score = sum(ap_list) / len(ap_list) if ap_list else 0.0
            mean_ndcg = sum(ndcg_list) / len(ndcg_list) if ndcg_list else 0.0

            results_by_method[method_name] = {
                "precision_at_10": round(mean_p10, 4),
                "recall": round(mean_rec, 4),
                "map": round(map_score, 4),
                "ndcg": round(mean_ndcg, 4),
                "precision_recall_curve": aggregated_pr_curve
            }

        return {
            "summary": results_by_method,
            "query_details": all_query_details,
            "queries_evaluated": len(self.queries)
        }
