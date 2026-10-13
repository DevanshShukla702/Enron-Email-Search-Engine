"""
scripts/ingest_dataset.py

Ingests raw Enron emails from data/raw/maildir into SQLite database.
Generates evaluation/results/dataset_statistics.json.
"""

import sys
import os
import json
import logging
from pathlib import Path
from collections import Counter
from datetime import datetime

# Adjust Python path to include project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.storage.database import init_db
from backend.app.storage.repository import EmailRepository
from backend.app.core.email_parser import parse_email_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ingest_dataset")


def main():
    print("=" * 60)
    print(" ENRON EMAIL INGESTION PIPELINE")
    print("=" * 60)
    print(f"Dataset Mode: {settings.DATASET_MODE}")
    limit = settings.DEMO_EMAIL_LIMIT if settings.DATASET_MODE == "demo" else None
    print(f"Target Email Ingestion Limit: {limit if limit else 'ALL'}")
    print(f"Database Target: {settings.DATABASE_PATH}")
    print("=" * 60)

    maildir = PROJECT_ROOT / "data" / "raw" / "maildir"
    if not maildir.exists():
        logger.error(f"Maildir not found at {maildir}. Please run python scripts/download_dataset.py first.")
        sys.exit(1)

    # Initialize SQLite schema
    init_db(settings.DATABASE_PATH)
    repo = EmailRepository(settings.DATABASE_PATH)

    # Gather list of email files
    logger.info("Scanning maildir for email files...")
    all_files = []
    for root, _, files in os.walk(maildir):
        for f in files:
            all_files.append(Path(root) / f)

    total_files = len(all_files)
    logger.info(f"Total raw email files located: {total_files:,}")

    if limit and total_files > limit:
        logger.info(f"Sampling {limit:,} files for DEMO mode...")
        target_files = all_files[:limit]
    else:
        target_files = all_files

    # Parse and insert in batches
    batch_size = 500
    current_batch = []
    parsed_count = 0
    failed_count = 0

    senders = Counter()
    recipients = Counter()
    mailboxes = Counter()
    folders = Counter()
    dates = []
    body_lengths = []
    empty_bodies = 0
    has_subject_count = 0

    logger.info(f"Parsing and ingesting {len(target_files):,} emails...")

    for i, file_path in enumerate(target_files, 1):
        parsed = parse_email_file(file_path)
        if not parsed:
            failed_count += 1
            continue

        parsed_count += 1
        current_batch.append(parsed)

        # Track statistics
        if parsed["sender"]:
            senders[parsed["sender"]] += 1
        if parsed["recipients"]:
            for r in parsed["recipients"].split(","):
                r_clean = r.strip().lower()
                if r_clean:
                    recipients[r_clean] += 1
        if parsed["mailbox"]:
            mailboxes[parsed["mailbox"]] += 1
        if parsed["folder"]:
            folders[parsed["folder"]] += 1
        if parsed["date"]:
            dates.append(parsed["date"])
        if parsed["subject"]:
            has_subject_count += 1

        b_len = len(parsed["body"])
        body_lengths.append(b_len)
        if b_len == 0:
            empty_bodies += 1

        # Batch insert
        if len(current_batch) >= batch_size:
            repo.insert_emails_batch(current_batch)
            current_batch = []
            if i % 2000 == 0 or i == len(target_files):
                logger.info(f"Ingested {i:,} / {len(target_files):,} emails...")

    if current_batch:
        repo.insert_emails_batch(current_batch)

    # Compute statistics summary
    valid_dates = [d for d in dates if d and len(d) >= 10]
    min_date = min(valid_dates) if valid_dates else None
    max_date = max(valid_dates) if valid_dates else None
    avg_body_len = sum(body_lengths) / len(body_lengths) if body_lengths else 0

    stats = {
        "dataset_mode": settings.DATASET_MODE,
        "total_files_scanned": total_files,
        "successfully_parsed": parsed_count,
        "failed_emails": failed_count,
        "unique_senders": len(senders),
        "unique_recipients": len(recipients),
        "unique_mailboxes": len(mailboxes),
        "date_range": {
            "start": min_date,
            "end": max_date
        },
        "average_body_length_chars": round(avg_body_len, 2),
        "empty_body_count": empty_bodies,
        "subject_coverage_pct": round((has_subject_count / parsed_count * 100), 2) if parsed_count else 0,
        "top_senders": dict(senders.most_common(15)),
        "folder_distribution": dict(folders.most_common(15)),
        "mailbox_distribution": dict(mailboxes.most_common(15)),
        "ingested_at": datetime.now().isoformat()
    }

    # Save to evaluation/results/dataset_statistics.json
    results_dir = PROJECT_ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    stats_file = results_dir / "dataset_statistics.json"

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    logger.info(f"Dataset statistics saved to: {stats_file}")
    print("=" * 60)
    print(" INGESTION COMPLETE")
    print(f"Total Emails Ingested: {parsed_count:,}")
    print(f"Unique Senders: {len(senders):,}")
    print(f"Unique Mailboxes: {len(mailboxes):,}")
    print(f"Date Range: {min_date} -> {max_date}")
    print(f"Subject Coverage: {stats['subject_coverage_pct']}%")
    print(f"Average Body Length: {round(avg_body_len, 1)} chars")
    print("=" * 60)


if __name__ == "__main__":
    main()
