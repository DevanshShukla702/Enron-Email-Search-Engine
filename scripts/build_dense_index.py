"""
scripts/build_dense_index.py

Constructs and serializes dense semantic embeddings and FAISS index:
- Uses sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- Generates embeddings in batches with live progress updates
- Normalizes vectors to unit length (L2 norm)
- Builds FAISS IndexFlatIP (cosine similarity)
- Persists FAISS index, embeddings numpy array, and document ID list
"""

import sys
import json
import logging
from pathlib import Path
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import settings
from backend.app.storage.repository import EmailRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("build_dense_index")


def prepare_dense_text(subject: str, body: str, max_body_chars: int = 250) -> str:
    """Combine subject with leading body snippet for optimal dense encoding."""
    subj = (subject or "").strip()
    bdy = " ".join((body or "").split())[:max_body_chars]
    if subj and bdy:
        return f"{subj}. {bdy}"
    return subj or bdy or "empty email"


def main():
    print("=" * 60)
    print(" DENSE VECTOR INDEX CONSTRUCTION PIPELINE")
    print("=" * 60)
    print(f"Model: {settings.DENSE_MODEL_NAME}")
    print(f"FAISS available: {HAS_FAISS}")

    repo = EmailRepository(settings.DATABASE_PATH)
    total_emails = repo.count_emails()
    if total_emails == 0:
        logger.error("No emails found in database. Run ingestion and preprocessing first.")
        sys.exit(1)

    logger.info(f"Loading {total_emails:,} email records from database...")
    emails = repo.get_all_for_indexing()

    doc_ids = []
    dense_texts = []

    for em in emails:
        doc_ids.append(em["document_id"])
        text = prepare_dense_text(em.get("subject", ""), em.get("body", ""))
        dense_texts.append(text)

    logger.info(f"Initializing SentenceTransformer: {settings.DENSE_MODEL_NAME}...")
    model = SentenceTransformer(settings.DENSE_MODEL_NAME)

    batch_size = 256
    total_batches = (len(dense_texts) + batch_size - 1) // batch_size
    all_embeddings = []

    logger.info(f"Encoding {len(dense_texts):,} documents in {total_batches} batches...")

    for b in range(total_batches):
        start_idx = b * batch_size
        end_idx = min(start_idx + batch_size, len(dense_texts))
        batch_texts = dense_texts[start_idx:end_idx]

        batch_emb = model.encode(
            batch_texts,
            batch_size=len(batch_texts),
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype(np.float32)

        all_embeddings.append(batch_emb)

        if (b + 1) % 10 == 0 or (b + 1) == total_batches:
            logger.info(f"Embedding batch {b + 1}/{total_batches} ({(b + 1) / total_batches * 100:.1f}% complete)...")

    embeddings_matrix = np.vstack(all_embeddings)
    dim = embeddings_matrix.shape[1]
    logger.info(f"Embeddings matrix computed: {embeddings_matrix.shape} (dim={dim})")

    # Persist index files
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    emb_path = settings.INDEX_DIR / "dense_embeddings.npy"
    doc_path = settings.INDEX_DIR / "dense_doc_ids.json"
    conf_path = settings.INDEX_DIR / "dense_model_config.json"
    faiss_path = settings.INDEX_DIR / "dense_index.faiss"

    np.save(emb_path, embeddings_matrix)

    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(doc_ids, f)

    config_data = {
        "model_name": settings.DENSE_MODEL_NAME,
        "embedding_dimension": dim,
        "document_count": len(doc_ids),
        "normalized": True,
        "similarity_metric": "inner_product_cosine"
    }
    with open(conf_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    if HAS_FAISS:
        logger.info("Building FAISS IndexFlatIP...")
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings_matrix)
        faiss.write_index(index, str(faiss_path))
        logger.info(f"FAISS index written: {faiss_path}")

    print("=" * 60)
    print(" DENSE INDEX BUILT SUCCESSFULLY")
    print(f"Embeddings:   {emb_path} ({embeddings_matrix.shape})")
    print(f"FAISS Index:  {faiss_path if HAS_FAISS else 'N/A'}")
    print(f"Document IDs: {doc_path} ({len(doc_ids):,} items)")
    print("=" * 60)


if __name__ == "__main__":
    main()
