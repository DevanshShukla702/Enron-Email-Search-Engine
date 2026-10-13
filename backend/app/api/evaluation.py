"""
backend/app/api/evaluation.py

Evaluation results and precision-recall curve data endpoints.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.config import settings

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/summary")
def get_evaluation_summary():
    metrics_path = settings.RESULTS_DIR / "metrics.json"
    meta_path = settings.RESULTS_DIR / "evaluation_run_metadata.json"

    if not metrics_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Evaluation has not been executed yet. Run python scripts/run_evaluation.py."
        )

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    meta_data = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

    return {
        "status": "ready",
        "dataset_mode": meta_data.get("dataset_mode", settings.DATASET_MODE),
        "corpus_size": meta_data.get("corpus_size", 10000),
        "query_count": meta_data.get("query_count", 12),
        "qrels_count": meta_data.get("qrels_count", 0),
        "metrics": metrics_data,
        "metadata": meta_data
    }


@router.get("/results")
def get_detailed_results():
    results_path = settings.RESULTS_DIR / "all_query_results.json"
    if not results_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Detailed evaluation results not found. Run python scripts/run_evaluation.py."
        )

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {"results": data}


@router.get("/precision-recall")
def get_precision_recall_data():
    metrics_path = settings.RESULTS_DIR / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Evaluation metrics not found. Run python scripts/run_evaluation.py."
        )

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    # Format into unified table for recharts: [{recall: 0.0, tfidf: 0.8, bm25: 0.85, ...}, ...]
    recall_levels = [round(i * 0.1, 1) for i in range(11)]
    recharts_points = []

    for idx, r in enumerate(recall_levels):
        pt = {"recall": r}
        for method in ["tfidf", "bm25", "dense", "rrf"]:
            curve = metrics_data.get(method, {}).get("precision_recall_curve", [])
            pt[method] = curve[idx]["precision"] if idx < len(curve) else 0.0
        recharts_points.append(pt)

    return {"points": recharts_points}
