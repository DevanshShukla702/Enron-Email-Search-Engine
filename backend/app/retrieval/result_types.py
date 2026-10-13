"""
backend/app/retrieval/result_types.py

Data structures for search results and ranking explanations.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class RetrievedDoc:
    document_id: str
    rank: int
    score: float
    subject: str = ""
    sender: str = ""
    recipients: str = ""
    date: Optional[str] = None
    folder: Optional[str] = None
    snippet: str = ""
    thread_id: Optional[str] = None
    highlighted_snippet: Optional[str] = None
    explanation: Optional[Dict[str, Any]] = None


def make_snippet(text: str, query: str, max_chars: int = 240) -> str:
    """Extract a query-aware context snippet from email body or fallback to start."""
    if not text:
        return ""
    text_clean = " ".join(text.split())
    if not query:
        return text_clean[:max_chars] + ("..." if len(text_clean) > max_chars else "")

    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    pos = -1
    for term in query_terms:
        idx = text_clean.lower().find(term)
        if idx != -1:
            pos = idx
            break

    if pos == -1:
        return text_clean[:max_chars] + ("..." if len(text_clean) > max_chars else "")

    start = max(0, pos - 60)
    end = min(len(text_clean), pos + 180)
    snippet = text_clean[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text_clean):
        snippet = snippet + "..."
    return snippet
