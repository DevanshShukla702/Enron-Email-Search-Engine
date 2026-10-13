"""
backend/app/retrieval/base.py

Abstract Base Retriever class defining the standard interface for all retrieval models.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.app.retrieval.result_types import RetrievedDoc


class BaseRetriever(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the retrieval method (tfidf, bm25, dense, rrf)."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        """Execute query retrieval and return ranked list of RetrievedDoc."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Verify whether indexes and models are fully loaded into memory."""
        pass
