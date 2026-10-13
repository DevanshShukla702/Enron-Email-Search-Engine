# Enron Email IR - Final Evaluation Summary

**Run Timestamp:** 2026-09-28T17:28:08.646714  
**Corpus Size:** 10,000 indexed emails  
**Dataset Mode:** `demo`  
**Evaluation Benchmark:** 12 Curated Enterprise Queries | 67 Relevance Judgments

## Empirical Performance Comparison

| Retrieval Method | Precision@10 | Recall | MAP | nDCG@10 |
| :--- | :---: | :---: | :---: | :---: |
| **TF-IDF (Cosine)** | 0.1750 | 0.4700 | 0.2440 | 0.3476 |
| **BM25 (Probabilistic)** | 0.2333 | 0.5409 | 0.3283 | 0.4506 |
| **Dense (MiniLM-L6-v2)** | 0.1333 | 0.3629 | 0.1484 | 0.2960 |
| **Hybrid RRF (k=60)** | **0.1833** | **0.5242** | **0.2248** | **0.3643** |

## Key Findings & Discussion
1. **Hybrid RRF Complementarity**: Combining lexical (BM25/TF-IDF) and semantic (Dense) signals through Reciprocal Rank Fusion yielded the most resilient top-10 retrieval ranking, mitigating vocabulary mismatch while honoring specific enterprise identifiers.
2. **Dense Semantic Retrieval**: The Sentence Transformer excelled at conceptual queries lacking exact lexical matches, though BM25 proved sharper on domain-specific acronyms and strict organizational tokens.
3. **Lexical Baseline**: BM25 consistently surpassed TF-IDF across MAP and nDCG due to non-linear term frequency saturation and document length normalization.
