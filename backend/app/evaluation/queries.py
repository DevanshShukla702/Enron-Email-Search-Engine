"""
backend/app/evaluation/queries.py

Loader for evaluation benchmark queries.
Format: query_id \t query_text \t description
"""

from typing import List, Dict, Any
from pathlib import Path
from backend.app.config import settings


class QueryItem:
    def __init__(self, query_id: str, query: str, description: str = ""):
        self.query_id = query_id
        self.query = query
        self.description = description

    def to_dict(self) -> Dict[str, str]:
        return {
            "query_id": self.query_id,
            "query": self.query,
            "description": self.description
        }


def load_queries(tsv_path: Path = settings.EVALUATION_DIR / "queries.tsv") -> List[QueryItem]:
    """Load query definitions from TSV file."""
    if not tsv_path.exists():
        return []

    queries = []
    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                q_id = parts[0].strip()
                q_text = parts[1].strip()
                q_desc = parts[2].strip() if len(parts) > 2 else ""
                queries.append(QueryItem(q_id, q_text, q_desc))
    return queries
