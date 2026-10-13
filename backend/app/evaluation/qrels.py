"""
backend/app/evaluation/qrels.py

Loader for relevance judgments (qrels) using standard TREC format:
query_id \t iteration \t document_id \t relevance_grade
Relevance grades:
0 = Not Relevant
1 = Partially Relevant
2 = Highly Relevant
"""

from typing import Dict
from collections import defaultdict
from pathlib import Path
from backend.app.config import settings


def load_qrels(tsv_path: Path = settings.EVALUATION_DIR / "qrels.tsv") -> Dict[str, Dict[str, int]]:
    """
    Load qrels from TSV file.
    Returns: Dict[query_id, Dict[document_id, int]]
    """
    if not tsv_path.exists():
        return {}

    qrels = defaultdict(dict)
    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 4:
                q_id = parts[0].strip()
                doc_id = parts[2].strip()
                grade = int(parts[3].strip())
                qrels[q_id][doc_id] = grade
            elif len(parts) == 3:
                q_id = parts[0].strip()
                doc_id = parts[1].strip()
                grade = int(parts[2].strip())
                qrels[q_id][doc_id] = grade
    return dict(qrels)
