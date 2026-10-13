# Enron Email IR Evaluation Benchmark

## Academic Integrity & Benchmark Provenance

As documented in the Information Retrieval Project 16 specification, the raw Enron Email Corpus does not natively supply standardized TREC-style query-relevance benchmarks matching the specific mailbox folder hierarchies of the CMU May 2015 release. 

To maintain strict academic integrity and avoid fabricated evaluation claims:
1. **Benchmark Nature**: This evaluation benchmark consists of **12 carefully curated enterprise information needs** designed specifically around the authentic correspondence topics present in the indexed corpus.
2. **Relevance Judgments**: Judgments in `qrels.tsv` are **locally constructed relevance judgments**, manually audited against the indexed documents. They are **not** labeled as synthetic or official CMU ground truth.
3. **Relevance Grading**: Graded relevance scale is implemented to support accurate Normalized Discounted Cumulative Gain (nDCG):
   - **Grade 2 (Highly Relevant)**: The email directly addresses the information need, containing specific decisions, regulatory filings, contractual agreements, or operational notifications.
   - **Grade 1 (Partially Relevant)**: The email discusses related topics, background context, adjacent proceedings, or high-level summaries.
   - **Grade 0 (Not Relevant)**: The email is non-relevant noise, off-topic administrative traffic, or an unrelated correspondence.

## File Formats

### 1. `queries.tsv`
Standard tab-separated format:
```tsv
query_id    query_text    description
```

### 2. `qrels.tsv`
Standard TREC 4-column format:
```tsv
query_id    iteration    document_id    relevance_grade
```
- `query_id`: Identifier corresponding to `queries.tsv` (e.g. `q01` through `q12`).
- `iteration`: Reserved for TREC compatibility (always `0`).
- `document_id`: Unique document ID matching the SQLite `emails` table.
- `relevance_grade`: Integer `0`, `1`, or `2`.

## Information Needs Covered
1. **q01**: FERC California wholesale power market investigation
2. **q02**: CAISO automated dispatch system II notification
3. **q03**: Cal PX bid cap resolution and price caps
4. **q04**: CAISO firm energy trade confirmation template
5. **q05**: Path 26 OTC transmission capacity increase
6. **q06**: Northern Natural Gas pipeline customer meetings
7. **q07**: Transwestern pipeline capacity allocation and reports
8. **q08**: Employee retention bonus agreements and contracts
9. **q09**: Severance agreements and employment litigation risks
10. **q10**: Personnel promotion and performance review committee
11. **q11**: Natural gas curtailment and generation emergency bids
12. **q12**: Enron transportation services regulatory filings
