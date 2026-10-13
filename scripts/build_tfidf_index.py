"""
scripts/build_tfidf_index.py

Constructs and serializes the TF-IDF sparse index:
- Uses scikit-learn TfidfVectorizer (sublinear_tf=True, ngram_range=(1,2))
- Fits over preprocessed, field-weighted text representations
- Persists vectorizer, CSR matrix, and document ID mapping
"""

import sys
import json
import pickle
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from scipy.sparse import save_npz

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.storage.repository import EmailRepository
from backend.app.core.field_weights import default_field_weights

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("build_tfidf_index")


def main():
    print("=" * 60)
    print(" TF-IDF INDEX CONSTRUCTION PIPELINE")
    print("=" * 60)

    repo = EmailRepository(settings.DATABASE_PATH)
    total_emails = repo.count_emails()
    if total_emails == 0:
        logger.error("No emails found in database. Run ingestion and preprocessing first.")
        sys.exit(1)

    logger.info(f"Loading {total_emails:,} email records from database...")
    emails = repo.get_all_for_indexing()

    doc_ids = []
    corpus_texts = []

    logger.info("Building field-weighted textual representations...")
    for em in emails:
        doc_ids.append(em["document_id"])
        # Use preprocessed text if available, otherwise raw
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
        corpus_texts.append(weighted_text)

    logger.info(f"Fitting TfidfVectorizer on {len(corpus_texts):,} documents...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.90,
        sublinear_tf=True,
        norm="l2"
    )

    tfidf_matrix = vectorizer.fit_transform(corpus_texts)
    # Ensure L2 normalization for direct cosine similarity via dot product
    tfidf_matrix = normalize(tfidf_matrix, norm="l2", axis=1)

    logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    logger.info(f"Vocabulary size: {len(vectorizer.vocabulary_):,} terms")
    logger.info(f"Non-zero elements: {tfidf_matrix.nnz:,}")

    # Persist index files
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vec_path = settings.INDEX_DIR / "tfidf_vectorizer.pkl"
    mat_path = settings.INDEX_DIR / "tfidf_matrix.npz"
    doc_path = settings.INDEX_DIR / "tfidf_doc_ids.json"

    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f, protocol=pickle.HIGHEST_PROTOCOL)

    save_npz(mat_path, tfidf_matrix)

    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(doc_ids, f)

    print("=" * 60)
    print(" TF-IDF INDEX BUILT SUCCESSFULLY")
    print(f"Vectorizer saved: {vec_path}")
    print(f"Matrix saved:     {mat_path}")
    print(f"Document IDs:     {doc_path} ({len(doc_ids):,} items)")
    print("=" * 60)


if __name__ == "__main__":
    main()
