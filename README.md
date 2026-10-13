# 📬 Enterprise Email Retrieval

> Search, discover, and analyze enterprise correspondence across lexical, probabilistic, dense semantic, and hybrid retrieval paradigms on the historical Enron email collection.

---

## 🗂️ Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Retrieval Methods](#retrieval-methods)
- [Evaluation Results](#evaluation-results)
- [Viva & Technical Defense Guide](#viva--technical-defense-guide)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Scripts Reference](#scripts-reference)
- [License](#license)

---

## Overview

**Enterprise Email Retrieval** is an enterprise-grade search system engineered over the historical Enron email collection. It indexes 10,000 authentic corporate messages in a fast in-memory demonstration configuration (scalable to the full ~517k corpus) and provides a unified search experience across:

- **Lexical term matching** via sublinear TF-IDF and cosine similarity
- **Probabilistic relevance ranking** via Okapi BM25 with term saturation and document length normalization
- **Dense semantic vector search** via Sentence Transformers (`all-MiniLM-L6-v2`) and FAISS `IndexFlatIP`
- **Hybrid rank fusion** via Reciprocal Rank Fusion (RRF, $k=60$)
- **Head-to-head model comparison** executing all four paradigms synchronously
- **Conversation thread reconstruction** using RFC-2822 header references and normalized subject grouping
- **Offline benchmark evaluation** tracking Precision@10, Recall, MAP, nDCG@10, and 11-point interpolated precision-recall curves

---

## Viva & Technical Defense Guide

A comprehensive, mathematically rigorous viva defense manual is available at:
👉 **[`docs/VIVA_GUIDE.md`](docs/VIVA_GUIDE.md)**

Covering:
- Detailed reasons to choose each model with seminal academic citations
- Step-by-step worked numerical examples for BM25, RRF, MAP, and nDCG
- Deep-dive into tokenization and query preprocessing
- Empirical explanation for why BM25 outperforms dense retrieval on specialized enterprise corpora
- Model failure modes, edge cases, and rapid-fire viva Q&A

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React + TypeScript UI                   │
│        (Search · Analytics · Evaluation · About)            │
└────────────────────────┬────────────────────────────────────┘
                         │  HTTP / JSON  (port 5173 → 8000)
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                          │
│  /api/search   /api/search/compare   /api/evaluation        │
│  /api/analytics/overview             /api/health            │
└───────┬────────────────┬────────────────────────────────────┘
        │                │
┌───────▼──────┐  ┌──────▼───────────────────────────────┐
│   SQLite DB  │  │          Retrieval Layer               │
│ (emails +    │  │  TF-IDF · BM25 · Dense FAISS · RRF   │
│  metadata)   │  │  (pre-built indexes loaded at startup) │
└──────────────┘  └──────────────────────────────────────┘
```

---

## Retrieval Methods

| Method | Algorithm | Index Type | Notes |
|--------|-----------|------------|-------|
| **TF-IDF** | Cosine similarity on TF-IDF sparse matrix | `scikit-learn` sparse matrix + `.pkl` | Classic lexical baseline |
| **BM25** | Probabilistic BM25 (k₁=1.5, b=0.75) | `rank-bm25` tokenized lists | Non-linear TF saturation + length norm |
| **Dense** | Sentence Transformer embeddings | FAISS `IndexFlatIP` (cosine, L2-norm) | `all-MiniLM-L6-v2` (384-dim) |
| **Hybrid RRF** | Reciprocal Rank Fusion (k=60) | Fuses ranks from all three above | Most resilient top-k ranking |

**Field weighting** during indexing (configurable):

| Field | Weight |
|-------|--------|
| Subject | 2.0× |
| Body | 1.0× |
| Sender | 0.5× |
| Recipients | 0.5× |

---

## Evaluation Results

Benchmark: **12 curated enterprise queries · 67 relevance judgments · 10,000 indexed emails (demo mode)**

| Retrieval Method | Precision@10 | Recall | MAP | nDCG@10 |
|:---|:---:|:---:|:---:|:---:|
| **TF-IDF (Cosine)** | 0.1750 | 0.4700 | 0.2440 | 0.3476 |
| **BM25 (Probabilistic)** | **0.2333** | **0.5409** | **0.3283** | **0.4506** |
| **Dense (MiniLM-L6-v2)** | 0.1333 | 0.3629 | 0.1484 | 0.2960 |
| **Hybrid RRF (k=60)** | 0.1833 | 0.5242 | 0.2248 | 0.3643 |

**Key findings:**
1. **BM25** leads across all metrics in this lexically-rich enterprise domain with precise identifiers and acronyms.
2. **Hybrid RRF** provides the most *resilient* top-10 ranking — mitigating vocabulary mismatch while respecting domain tokens.
3. **Dense retrieval** excels on conceptual/paraphrase queries where exact tokens are missing.
4. **TF-IDF** remains a solid baseline; BM25's TF saturation and length normalization consistently push it ahead.

---

## Tech Stack

**Backend**
- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- SQLite (via stdlib `sqlite3`)
- `scikit-learn` — TF-IDF sparse matrix
- `rank-bm25` — BM25
- `sentence-transformers` — Dense embeddings
- `faiss-cpu` — ANN vector search
- `nltk` — Tokenization & stopword removal
- `pydantic-settings` — Config management

**Frontend**
- React 18 + TypeScript
- [Vite](https://vitejs.dev/) build tool
- Tailwind CSS
- Recharts — Precision/Recall charts
- Lucide React — Icons

---

## Project Structure

```
IR_Project/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   │   ├── search.py       # /api/search & /api/search/compare
│   │   │   ├── evaluation.py   # /api/evaluation/*
│   │   │   ├── analytics.py    # /api/analytics/*
│   │   │   └── health.py       # /api/health
│   │   ├── retrieval/      # Retrieval engine implementations
│   │   │   ├── base.py         # Abstract BaseRetriever interface
│   │   │   ├── tfidf_retriever.py
│   │   │   ├── bm25_retriever.py
│   │   │   ├── dense_retriever.py
│   │   │   ├── rrf_retriever.py
│   │   │   └── result_types.py
│   │   ├── core/           # Preprocessing, evaluation logic
│   │   ├── storage/        # EmailRepository (SQLite)
│   │   ├── config.py       # Pydantic settings
│   │   ├── main.py         # FastAPI app entrypoint
│   │   └── schemas.py      # Request/Response schemas
│   ├── tests/              # Pytest unit & integration tests
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # SearchPage · AnalyticsPage · EvaluationPage · AboutPage
│   │   ├── services/api.ts # Backend API client
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Formatting helpers
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/                # One-off data pipeline scripts
│   ├── download_dataset.py
│   ├── ingest_dataset.py
│   ├── preprocess_dataset.py
│   ├── build_threads.py
│   ├── build_tfidf_index.py
│   ├── build_bm25_index.py
│   ├── build_dense_index.py
│   ├── build_all_indexes.py
│   ├── run_evaluation.py
│   └── health_check.py
│
├── data/                   # ⚠️ gitignored — generated locally
│   ├── raw/                # Downloaded Enron corpus
│   ├── interim/            # Parsed email records
│   ├── processed/          # SQLite database
│   └── indexes/            # Built index artifacts
│
├── models/                 # ⚠️ gitignored — downloaded at runtime
├── evaluation/             # Evaluation result artifacts & figures
├── .env.example            # Environment variable template
├── run.ps1                 # PowerShell task runner
└── pytest.ini
```

---

## Getting Started

### Prerequisites

- Python **3.10+**
- Node.js **18+** and npm
- Git

### 1 — Clone the Repository

```bash
git clone https://github.com/DevanshShukla702/Enron-Email-Search-Engine.git
cd Enron-Email-Search-Engine
```

### 2 — Set Up the Python Environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3 — Configure Environment Variables

```bash
cp .env.example .env
# Edit .env if you want to change paths or switch to full dataset mode
```

> **Tip:** Leave `DATASET_MODE=demo` for a fast 10k-email setup. Set it to `full` to index the complete ~517k Enron corpus (takes significantly longer to build indexes).

### 4 — Download & Ingest the Dataset

```powershell
# Using the PowerShell task runner (Windows)
.\run.ps1 download
.\run.ps1 ingest
.\run.ps1 preprocess
```

Or run scripts directly:
```bash
python scripts/download_dataset.py
python scripts/ingest_dataset.py
python scripts/preprocess_dataset.py
```

### 5 — Build Search Indexes

```powershell
.\run.ps1 build-all   # TF-IDF + BM25 + Dense FAISS
```

Or selectively:
```powershell
.\run.ps1 build-tfidf
.\run.ps1 build-bm25
.\run.ps1 build-dense   # Downloads ~90MB MiniLM model on first run
```

### 6 — Start the Backend

```powershell
.\run.ps1 backend
# → http://127.0.0.1:8000
# → API docs at http://127.0.0.1:8000/docs
```

### 7 — Start the Frontend

```powershell
.\run.ps1 frontend
# → http://localhost:5173
```

### 8 — Run Tests (Optional)

```powershell
.\run.ps1 test
```

### 9 — Run Evaluation Benchmark (Optional)

```powershell
.\run.ps1 evaluate
# Results written to evaluation/results/
```

---

## Configuration

All configuration is managed via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATASET_MODE` | `demo` | `demo` (10k emails) or `full` (~517k emails) |
| `DEMO_EMAIL_LIMIT` | `10000` | Emails to ingest in demo mode |
| `DATABASE_PATH` | `data/processed/enron_emails.db` | SQLite database path |
| `INDEX_DIR` | `data/indexes` | Directory for built index artifacts |
| `DENSE_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace model for dense retrieval |
| `DEFAULT_TOP_K` | `10` | Default number of results to return |
| `RRF_K` | `60` | RRF constant (higher = softer rank fusion) |
| `BM25_K1` | `1.5` | BM25 term frequency saturation parameter |
| `BM25_B` | `0.75` | BM25 document length normalization |
| `WEIGHT_SUBJECT` | `2.0` | Index weight for email subject field |
| `API_HOST` | `127.0.0.1` | Backend host |
| `API_PORT` | `8000` | Backend port |
| `FRONTEND_URL` | `http://localhost:5173` | CORS allowed frontend origin |

---

## API Reference

All endpoints are documented interactively at `http://127.0.0.1:8000/docs` (Swagger UI) once the backend is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | System info & endpoint map |
| `POST` | `/api/search` | Execute a search with chosen retrieval method |
| `POST` | `/api/search/compare` | Compare all four methods on the same query |
| `GET` | `/api/evaluation/summary` | Return evaluation metrics for all methods |
| `GET` | `/api/analytics/overview` | Dataset-level statistics |
| `GET` | `/api/health` | System health & index readiness check |

**Example search request:**
```json
POST /api/search
{
  "query": "energy trading risk management",
  "method": "bm25",
  "top_k": 10,
  "filters": {
    "sender": "jeff.skilling@enron.com"
  }
}
```

---

## Scripts Reference

Use `.\run.ps1 <command>` (Windows PowerShell) or call scripts directly with `python scripts/<script>.py`:

| Command | Script | Description |
|---------|--------|-------------|
| `download` | `download_dataset.py` | Download CMU Enron corpus |
| `ingest` | `ingest_dataset.py` | Parse raw emails → SQLite |
| `preprocess` | `preprocess_dataset.py` | Tokenize, clean, build search text |
| `preprocess` | `build_threads.py` | Reconstruct email thread relationships |
| `build-tfidf` | `build_tfidf_index.py` | Build TF-IDF sparse matrix + pickle |
| `build-bm25` | `build_bm25_index.py` | Build BM25 tokenized index |
| `build-dense` | `build_dense_index.py` | Embed all docs + build FAISS index |
| `build-all` | `build_all_indexes.py` | Run all three index builds |
| `evaluate` | `run_evaluation.py` | Run benchmark & write results |
| `health` | `health_check.py` | Verify index files & DB integrity |
| `test` | — | `pytest backend/tests -v` |
| `clean` | — | Remove `__pycache__` and pytest caches |

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built as an academic Information Retrieval project · Enron Corpus · 2026
</p>
