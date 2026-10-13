"""
scripts/download_dataset.py

Dataset Acquisition for Enron Email IR Project.
Downloads and extracts the official CMU Enron Email Corpus (May 7, 2015 version).
Primary Source: https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz
"""

import sys
import os
import tarfile
import urllib.request
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("download_dataset")

# Constants
ENRON_URL = "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
EXPECTED_MIN_SIZE = 400 * 1024 * 1024  # at least 400 MB

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
ARCHIVE_PATH = DATA_RAW_DIR / "enron_mail_20150507.tar.gz"
MAILDIR_PATH = DATA_RAW_DIR / "maildir"


def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TB"


def download_with_progress(url: str, dest_path: Path):
    """Download a file with continuous progress reporting."""
    logger.info(f"Connecting to {url}...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Enron-IR-Academic-Project/1.0"}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as out_file:
        total_size = int(response.headers.get("Content-Length", 0))
        logger.info(f"Target file size: {format_bytes(total_size)}")
        
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        last_reported_pct = -5
        
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            
            if total_size > 0:
                pct = int((downloaded / total_size) * 100)
                if pct >= last_reported_pct + 5:
                    logger.info(f"Downloading: {pct}% ({format_bytes(downloaded)} / {format_bytes(total_size)})")
                    last_reported_pct = pct


def count_files(directory: Path) -> int:
    """Count total files in a directory tree."""
    count = 0
    for root, _, files in os.walk(directory):
        count += len(files)
    return count


def verify_and_extract(archive_path: Path, extract_dir: Path) -> bool:
    """Extract tar.gz archive safely and report progress."""
    logger.info(f"Extracting {archive_path.name} into {extract_dir}...")
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            members = tar.getmembers()
            total_members = len(members)
            logger.info(f"Archive contains {total_members:,} entries. Beginning extraction...")
            
            # Extract in safe manner
            tar.extractall(path=extract_dir)
            logger.info("Extraction completed successfully.")
            return True
    except Exception as e:
        logger.error(f"Failed to extract tarball: {e}")
        return False


def main():
    print("=" * 60)
    print(" ENRON EMAIL DATASET ACQUISITION PIPELINE")
    print("=" * 60)
    print(f"Dataset: Official CMU Enron Email Corpus (May 7, 2015)")
    print(f"Source URL: {ENRON_URL}")
    print(f"Destination: {DATA_RAW_DIR}")
    print("=" * 60)

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Check if already extracted
    if MAILDIR_PATH.exists() and any(MAILDIR_PATH.iterdir()):
        logger.info(f"Extracted corpus already found at: {MAILDIR_PATH}")
        total_emails = count_files(MAILDIR_PATH)
        logger.info(f"Total email files detected: {total_emails:,}")
        print("=" * 60)
        print(f"STATUS: Corpus is ready for ingestion ({total_emails:,} files).")
        print("=" * 60)
        return 0

    # Step 2: Check if archive already downloaded
    if ARCHIVE_PATH.exists() and ARCHIVE_PATH.stat().st_size >= EXPECTED_MIN_SIZE:
        logger.info(f"Valid archive already exists at: {ARCHIVE_PATH} ({format_bytes(ARCHIVE_PATH.stat().st_size)})")
    else:
        logger.info("Archive not found or incomplete. Starting download...")
        try:
            download_with_progress(ENRON_URL, ARCHIVE_PATH)
            logger.info(f"Download completed: {ARCHIVE_PATH} ({format_bytes(ARCHIVE_PATH.stat().st_size)})")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            logger.error(
                "Enron dataset could not be downloaded automatically.\n"
                "Please check your internet connection or download manually from:\n"
                f"{ENRON_URL}\n"
                f"and place the archive at: {ARCHIVE_PATH}"
            )
            return 1

    # Step 3: Extract archive
    success = verify_and_extract(ARCHIVE_PATH, DATA_RAW_DIR)
    if not success:
        return 1

    # Step 4: Verify extracted files
    if not MAILDIR_PATH.exists():
        # Sometimes tarball extracts directly or into a subfolder
        extracted_dirs = [d for d in DATA_RAW_DIR.iterdir() if d.is_dir() and d.name != "maildir"]
        logger.info(f"Extracted directories: {[d.name for d in extracted_dirs]}")

    total_emails = count_files(MAILDIR_PATH) if MAILDIR_PATH.exists() else count_files(DATA_RAW_DIR)
    logger.info(f"Corpus verification complete! Total email files found: {total_emails:,}")
    print("=" * 60)
    print(f"SUCCESS: Enron dataset acquired and extracted ({total_emails:,} emails).")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
