"""
backend/app/api/analytics.py

Corpus analytics endpoint: volume, senders, folders, and thread statistics.
"""

from fastapi import APIRouter
from backend.app.storage.repository import EmailRepository
from backend.app.config import settings

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
repo = EmailRepository(settings.DATABASE_PATH)


@router.get("/overview")
def get_analytics_overview():
    return repo.get_analytics_overview()
