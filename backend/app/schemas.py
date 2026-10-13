"""
backend/app/schemas.py

Pydantic schemas and data transfer models for API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    sender: Optional[str] = None
    folder: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    method: str = Field(default="rrf", description="Retrieval method: tfidf, bm25, dense, or rrf")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to retrieve")
    filters: Optional[SearchFilters] = Field(default=None, description="Optional search filters")
    thread_mode: bool = Field(default=False, description="Group results by conversation thread")


class RankingExplanation(BaseModel):
    method: str
    raw_score: Optional[float] = None
    tfidf_rank: Optional[int] = None
    bm25_rank: Optional[int] = None
    dense_rank: Optional[int] = None
    rrf_score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class SearchResultItem(BaseModel):
    document_id: str
    rank: int
    score: float
    subject: str
    sender: str
    recipients: str
    date: Optional[str] = None
    folder: Optional[str] = None
    snippet: str
    thread_id: Optional[str] = None
    highlighted_snippet: Optional[str] = None
    explanation: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    query: str
    method: str
    total_results: int
    execution_time_ms: float
    results: List[SearchResultItem]


class CompareResponse(BaseModel):
    query: str
    execution_time_ms: float
    tfidf: List[SearchResultItem]
    bm25: List[SearchResultItem]
    dense: List[SearchResultItem]
    rrf: List[SearchResultItem]


class EmailDetail(BaseModel):
    document_id: str
    message_id: Optional[str] = None
    sender: str
    sender_name: Optional[str] = None
    recipients: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    subject: str
    date: Optional[str] = None
    mailbox: Optional[str] = None
    folder: Optional[str] = None
    body: str
    thread_id: Optional[str] = None
    file_path: Optional[str] = None


class ThreadResponse(BaseModel):
    thread_id: str
    subject: str
    message_count: int
    messages: List[EmailDetail]


class MetricScores(BaseModel):
    precision_at_10: float
    recall: float
    map: float
    ndcg: float


class EvaluationSummary(BaseModel):
    dataset_mode: str
    corpus_size: int
    query_count: int
    qrels_count: int
    metrics: Dict[str, MetricScores]
    metadata: Dict[str, Any]


class AnalyticsOverview(BaseModel):
    total_emails: int
    unique_senders: int
    unique_recipients: int
    date_range: Dict[str, Optional[str]]
    avg_body_length: float
    top_senders: List[Dict[str, Any]]
    top_folders: List[Dict[str, Any]]
    emails_by_year: List[Dict[str, Any]]
    thread_stats: Dict[str, Any]
    index_stats: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    indexed_documents: int
    indexes: Dict[str, bool]
    model_loaded: bool
