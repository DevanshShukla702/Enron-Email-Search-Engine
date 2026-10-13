"""
scripts/preprocess_dataset.py

Preprocesses subject and body fields in the SQLite database:
- Unicode normalization, HTML stripping, lowercasing, tokenization, stop-word removal, stemming.
- Updates processed_subject and processed_body columns.
"""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.storage.database import get_db_connection
from backend.app.storage.repository import EmailRepository
from backend.app.core.preprocessing import default_preprocessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("preprocess_dataset")


def main():
    print("=" * 60)
    print(" EMAIL PREPROCESSING PIPELINE")
    print("=" * 60)
    print(f"Database: {settings.DATABASE_PATH}")
    print("=" * 60)

    repo = EmailRepository(settings.DATABASE_PATH)
    total_emails = repo.count_emails()
    if total_emails == 0:
        logger.error("No emails found in database. Run python scripts/ingest_dataset.py first.")
        sys.exit(1)

    logger.info(f"Loaded {total_emails:,} emails to preprocess...")

    conn = get_db_connection(settings.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT document_id, subject, body FROM emails ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    batch_size = 500
    updates = []
    processed_count = 0

    for row in rows:
        doc_id = row["document_id"]
        subj = row["subject"] or ""
        bdy = row["body"] or ""

        proc_subj = default_preprocessor.preprocess(subj)
        proc_bdy = default_preprocessor.preprocess(bdy)

        updates.append((proc_subj, proc_bdy, doc_id))
        processed_count += 1

        if len(updates) >= batch_size:
            repo.update_processed_batch(updates)
            updates = []
            if processed_count % 2000 == 0 or processed_count == total_emails:
                logger.info(f"Preprocessed {processed_count:,} / {total_emails:,} documents...")

    if updates:
        repo.update_processed_batch(updates)

    print("=" * 60)
    print(f"PREPROCESSING COMPLETE: {processed_count:,} documents processed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
