"""
scripts/health_check.py

System and Index Integrity Health Check.
Verifies all 10 core criteria:
1. Python dependencies importable
2. SQLite database exists
3. Document count > 0
4. TF-IDF index exists and loads
5. BM25 index exists and loads
6. Dense index exists and loads
7. Dense embedding model loads
8. Document ID mappings align across all indexes
9. Evaluation results and benchmark files exist
10. Frontend package.json and built assets exist
"""

import sys
import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("health_check")


def main():
    print("=" * 65)
    print(" ENRON EMAIL IR SYSTEM - HEALTH CHECK")
    print("=" * 65)

    checks = []

    # 1. Python dependencies
    try:
        import fastapi
        import uvicorn
        import rank_bm25
        import sentence_transformers
        import sklearn
        import scipy
        import pandas
        import numpy
        checks.append(("Python Dependencies", True, "All required IR/ML packages importable"))
    except Exception as e:
        checks.append(("Python Dependencies", False, str(e)))

    # 2. Database existence
    from backend.app.config import settings
    from backend.app.storage.repository import EmailRepository
    db_ok = settings.DATABASE_PATH.exists()
    checks.append(("Database Exists", db_ok, str(settings.DATABASE_PATH)))

    # 3. Document count
    try:
        repo = EmailRepository(settings.DATABASE_PATH)
        count = repo.count_emails()
        checks.append(("Indexed Document Count", count > 0, f"{count:,} emails in SQLite"))
    except Exception as e:
        checks.append(("Indexed Document Count", False, str(e)))
        count = 0

    # 4. TF-IDF index
    from backend.app.retrieval.tfidf_retriever import TfidfRetriever
    try:
        tfidf = TfidfRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)
        tfidf_ok = tfidf.is_ready()
        checks.append(("TF-IDF Index", tfidf_ok, f"{len(tfidf.doc_ids):,} indexed documents"))
    except Exception as e:
        checks.append(("TF-IDF Index", False, str(e)))
        tfidf = None

    # 5. BM25 index
    from backend.app.retrieval.bm25_retriever import BM25Retriever
    try:
        bm25 = BM25Retriever(settings.INDEX_DIR, settings.DATABASE_PATH)
        bm25_ok = bm25.is_ready()
        checks.append(("BM25 Index", bm25_ok, f"{len(bm25.doc_ids):,} indexed documents (k1={bm25.k1}, b={bm25.b})"))
    except Exception as e:
        checks.append(("BM25 Index", False, str(e)))
        bm25 = None

    # 6. Dense index
    from backend.app.retrieval.dense_retriever import DenseRetriever
    try:
        dense = DenseRetriever(settings.INDEX_DIR, settings.DATABASE_PATH)
        dense_ok = dense.is_ready()
        checks.append(("Dense Vector Index", dense_ok, f"{len(dense.doc_ids):,} indexed vectors (MiniLM-L6-v2)"))
    except Exception as e:
        checks.append(("Dense Vector Index", False, str(e)))
        dense = None

    # 7. Embedding model
    try:
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer(settings.DENSE_MODEL_NAME)
        checks.append(("Embedding Model", True, f"{settings.DENSE_MODEL_NAME} (384-d)"))
    except Exception as e:
        checks.append(("Embedding Model", False, str(e)))

    # 8. Document ID alignment
    try:
        if tfidf and bm25 and dense and tfidf.doc_ids and bm25.doc_ids and dense.doc_ids:
            aligned = (tfidf.doc_ids == bm25.doc_ids == dense.doc_ids)
            checks.append(("Document ID Alignment", aligned, f"Aligned across all 3 models ({len(tfidf.doc_ids):,} docs)"))
        else:
            checks.append(("Document ID Alignment", False, "One or more doc_ids lists empty"))
    except Exception as e:
        checks.append(("Document ID Alignment", False, str(e)))

    # 9. Evaluation benchmark & results
    q_file = settings.EVALUATION_DIR / "queries.tsv"
    qr_file = settings.EVALUATION_DIR / "qrels.tsv"
    m_file = settings.RESULTS_DIR / "metrics.json"
    eval_ok = q_file.exists() and qr_file.exists() and m_file.exists()
    checks.append(("Evaluation Results", eval_ok, f"Benchmark and empirical metrics present at {settings.RESULTS_DIR}"))

    # 10. Frontend dependencies & build
    fe_pkg = PROJECT_ROOT / "frontend" / "package.json"
    fe_dist = PROJECT_ROOT / "frontend" / "dist" / "index.html"
    fe_ok = fe_pkg.exists() and fe_dist.exists()
    checks.append(("Frontend Build Assets", fe_ok, f"Built bundle present: {fe_dist.name}"))

    print(f"{'Check Item':<28} | {'Status':<6} | {'Details'}")
    print("-" * 65)

    all_passed = True
    for item, passed, details in checks:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{item:<28} | {status_str:<6} | {details}")

    print("=" * 65)
    if all_passed:
        print("OVERALL HEALTH STATUS: PASS (System is fully ready for demonstration)")
    else:
        print("OVERALL HEALTH STATUS: FAIL (Resolve failing components)")
    print("=" * 65)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
