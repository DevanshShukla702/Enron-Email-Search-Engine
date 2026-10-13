"""
scripts/build_threads.py

Reconstructs email conversation threads and updates thread_id in SQLite.
"""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.storage.repository import EmailRepository
from backend.app.core.thread_builder import build_email_threads

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("build_threads")


def main():
    print("=" * 60)
    print(" EMAIL THREAD RECONSTRUCTION PIPELINE")
    print("=" * 60)

    repo = EmailRepository(settings.DATABASE_PATH)
    total_emails = repo.count_emails()
    if total_emails == 0:
        logger.error("No emails found in database. Run python scripts/ingest_dataset.py first.")
        sys.exit(1)

    logger.info(f"Loading {total_emails:,} emails for thread analysis...")
    emails = repo.get_all_for_threading()

    logger.info("Executing Disjoint-Set conversation thread reconstruction...")
    doc_to_thread = build_email_threads(emails)

    unique_threads = len(set(doc_to_thread.values()))
    logger.info(f"Identified {unique_threads:,} distinct conversation threads across {len(doc_to_thread):,} emails.")

    # Update database in batches
    updates = [(thread_id, doc_id) for doc_id, thread_id in doc_to_thread.items()]
    batch_size = 1000
    for i in range(0, len(updates), batch_size):
        chunk = updates[i:i + batch_size]
        repo.update_threads_batch(chunk)

    print("=" * 60)
    print(f"THREAD RECONSTRUCTION COMPLETE")
    print(f"Total Threads: {unique_threads:,}")
    print(f"Average Messages per Thread: {round(len(doc_to_thread) / unique_threads, 2)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
