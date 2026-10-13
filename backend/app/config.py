"""
backend/app/config.py

Configuration settings for the Enron Email Information Retrieval System.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Base project root (two levels above this file: backend/app -> backend -> root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Dataset Mode: "demo" or "full"
    DATASET_MODE: str = Field(default="demo")
    DEMO_EMAIL_LIMIT: int = Field(default=10000)

    # Directories and Paths
    DATA_DIR: Path = Field(default=BASE_DIR / "data")
    DATABASE_PATH: Path = Field(default=BASE_DIR / "data" / "processed" / "enron_emails.db")
    INDEX_DIR: Path = Field(default=BASE_DIR / "data" / "indexes")
    MODEL_DIR: Path = Field(default=BASE_DIR / "models")
    EVALUATION_DIR: Path = Field(default=BASE_DIR / "data" / "evaluation")
    RESULTS_DIR: Path = Field(default=BASE_DIR / "evaluation" / "results")

    # Retrieval Models Configuration
    DENSE_MODEL_NAME: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    DEFAULT_TOP_K: int = Field(default=10)
    RRF_K: int = Field(default=60)
    BM25_K1: float = Field(default=1.5)
    BM25_B: float = Field(default=0.75)

    # Text Representation Field Weights
    WEIGHT_SUBJECT: float = Field(default=2.0)
    WEIGHT_BODY: float = Field(default=1.0)
    WEIGHT_SENDER: float = Field(default=0.5)
    WEIGHT_RECIPIENTS: float = Field(default=0.5)

    # Server Configuration
    API_HOST: str = Field(default="127.0.0.1")
    API_PORT: int = Field(default=8000)
    FRONTEND_URL: str = Field(default="http://localhost:5173")

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global singleton settings
settings = Settings()
