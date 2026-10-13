"""
scripts/build_bm25_index.py

Constructs and serializes the BM25 index:
- Uses rank-bm25 BM25Okapi with configurable k1 and b
- Preprocesses and tokenizes documents
- Persists BM25 model and document ID list
"""

import sys
import json
import pickle
import logging
from pathlib import Path
from rank_bm25 import BM25Okapi

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.storage.repository import EmailRepository
from backend.app.core.field_weights import default_field_weights
from backend.app.core.preprocessing import default_preprocessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("build_bm25_index")


def main():
    print("=" * 60)
    print(" BM25 INDEX CONSTRUCTION PIPELINE")
    print("=" * 60)
    print(f"BM25 Parameters: k1={settings.BM25_K1}, b={settings.BM25_B}")

    repo = EmailRepository(settings.DATABASE_PATH)
    total_emails = repo.count_emails()
    if total_emails == 0:
        logger.error("No emails found in database. Run ingestion and preprocessing first.")
        sys.exit(1)

    logger.info(f"Loading {total_emails:,} email records from database...")
    emails = repo.get_all_for_indexing()

    doc_ids = []
    tokenized_corpus = []

    logger.info("Tokenizing documents for BM25...")
    for i, em in enumerate(emails, 1):
        doc_ids.append(em["document_id"])
        subj = em.get("processed_subject") or em.get("subject") or ""
        bdy = em.get("processed_body") or em.get("body") or ""
        sndr = em.get("sender") or ""
        recips = em.get("recipients") or ""

        weighted_text = default_field_weights.build_weighted_text(
            subject=subj,
            body=bdy,
            sender=sndr,
            recipients=recips
        )
        tokens = [t for t in weighted_text.split() if len(t) > 1]
        tokenized_corpus.append(tokens)

        if i % 2500 == 0 or i == total_emails:
            logger.info(f"Tokenized {i:,} / {total_emails:,} documents...")

    logger.info("Fitting BM25Okapi model...")
    bm25 = BM25Okapi(tokenized_corpus, k1=settings.BM25_K1, b=settings.BM25_B)

    # Persist BM25 index
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index_path = settings.INDEX_DIR / "bm25_index.pkl"
    doc_path = settings.INDEX_DIR / "bm25_doc_ids.json"

    with open(index_path, "wb") as f:
        pickle.dump(bm25, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(doc_ids, f)

    print("=" * 60)
    print(" BM25 INDEX BUILT SUCCESSFULLY")
    print(f"Index saved:  {index_path}")
    print(f"Document IDs: {doc_path} ({len(doc_ids):,} items)")
    print("=" * 60)


if __name__ == "__main__":
    main()
