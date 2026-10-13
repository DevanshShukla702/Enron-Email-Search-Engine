"""
backend/app/storage/database.py

SQLite connection management and schema migration for Enron Email records.
Uses WAL mode for high concurrency read/write performance.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Generator
from backend.app.config import settings

logger = logging.getLogger("database")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT UNIQUE NOT NULL,
    message_id TEXT,
    sender TEXT,
    sender_name TEXT,
    recipients TEXT,
    cc TEXT,
    bcc TEXT,
    subject TEXT,
    date TEXT,
    mailbox TEXT,
    folder TEXT,
    body TEXT,
    processed_subject TEXT,
    processed_body TEXT,
    thread_id TEXT,
    file_path TEXT,
    in_reply_to TEXT,
    references_field TEXT
);

CREATE INDEX IF NOT EXISTS idx_emails_document_id ON emails(document_id);
CREATE INDEX IF NOT EXISTS idx_emails_thread_id ON emails(thread_id);
CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender);
CREATE INDEX IF NOT EXISTS idx_emails_date ON emails(date);
CREATE INDEX IF NOT EXISTS idx_emails_folder ON emails(folder);
CREATE INDEX IF NOT EXISTS idx_emails_mailbox ON emails(mailbox);
"""


def get_db_connection(db_path: Path = settings.DATABASE_PATH) -> sqlite3.Connection:
    """Create a connection to the SQLite database with row factory enabled."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode and pragmas for performance
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB cache
    return conn


def init_db(db_path: Path = settings.DATABASE_PATH):
    """Initialize database tables and indexes."""
    logger.info(f"Initializing database at: {db_path}")
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.executescript(SCHEMA_SQL)
        logger.info("Database schema initialized successfully.")
    finally:
        conn.close()
