"""
scripts/build_all_indexes.py

Master index construction runner:
Builds TF-IDF, BM25, and Dense Sentence Transformer FAISS indexes.
"""

import sys
import subprocess
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("build_all_indexes")


def run_script(script_name: str) -> bool:
    script_path = PROJECT_ROOT / "scripts" / script_name
    logger.info(f"Running {script_name}...")
    res = subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_ROOT))
    return res.returncode == 0


def main():
    print("=" * 60)
    print(" BUILDING ALL SEARCH INDEXES")
    print("=" * 60)

    steps = [
        "build_tfidf_index.py",
        "build_bm25_index.py",
        "build_dense_index.py"
    ]

    for step in steps:
        success = run_script(step)
        if not success:
            logger.error(f"Step {step} failed. Aborting.")
            sys.exit(1)

    print("=" * 60)
    print(" ALL INDEXES BUILT SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
