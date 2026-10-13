import React from 'react';
import { ArchitectureCard } from '../components/ArchitectureCard';
import { BookOpen, CheckCircle, ShieldAlert, Cpu, ExternalLink } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          About the Enterprise Email Information Retrieval Project
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-3xl leading-relaxed">
          Information Retrieval Project 16 · Academic implementation and comparative analysis of classical, probabilistic,
          dense semantic, and hybrid retrieval techniques on the historic Enron Email Corpus.
        </p>
      </div>

      {/* Visual Pipeline */}
      <ArchitectureCard />

      {/* Methodological Details Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Classical: TF-IDF */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-lg bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">1</span>
            <h3 className="text-sm font-bold text-slate-900">TF-IDF Retrieval (Cosine Similarity)</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Constructed using <code className="text-xs font-mono bg-slate-100 px-1 py-0.5 rounded">TfidfVectorizer</code> with sublinear term frequency scaling (1 + log(tf)) and inverse document frequency (log((1 + N)/(1 + df)) + 1).
          </p>
          <div className="p-3 bg-slate-50 rounded-xl font-mono text-[11px] text-slate-700 border border-slate-100">
            cos(q, d) = (v_q · v_d) / (||v_q||₂ · ||v_d||₂)
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Sparse CSR matrix representation spanning 212,498 features across unigrams and bigrams with min_df=2 and max_df=0.90.
          </p>
        </div>

        {/* Probabilistic: BM25 */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 font-bold text-xs flex items-center justify-center">2</span>
            <h3 className="text-sm font-bold text-slate-900">BM25 Retrieval (Okapi BM25)</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Probabilistic retrieval incorporating term saturation and non-linear document length normalization. Exposes configurable $k_1 = 1.5$ and $b = 0.75$.
          </p>
          <div className="p-3 bg-slate-50 rounded-xl font-mono text-[11px] text-slate-700 border border-slate-100">
            Score(D, Q) = Σ IDF(q_i) · (f(q_i, D) · (k1 + 1)) / (f(q_i, D) + k1 · (1 - b + b · |D| / avgdl))
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Prevents document length bias while dampening excessive term frequency spikes common in corporate email threads.
          </p>
        </div>

        {/* Dense Semantic: Sentence Transformer */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-lg bg-purple-100 text-purple-700 font-bold text-xs flex items-center justify-center">3</span>
            <h3 className="text-sm font-bold text-slate-900">Sentence Transformer Dense Retrieval</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Bi-encoder neural semantic retrieval utilizing <code className="text-xs font-mono bg-slate-100 px-1 py-0.5 rounded">sentence-transformers/all-MiniLM-L6-v2</code>. Documents are embedded into a dense 384-dimensional latent space.
          </p>
          <div className="p-3 bg-slate-50 rounded-xl font-mono text-[11px] text-slate-700 border border-slate-100">
            Similarity(q, d) = &lt;E(q), E(d)&gt; over unit-normalized embeddings
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Indexed with FAISS <code className="font-mono text-[11px]">IndexFlatIP</code> for sub-millisecond approximate nearest neighbor retrieval, resolving vocabulary mismatch.
          </p>
        </div>

        {/* Hybrid RRF */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-lg bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center">4</span>
            <h3 className="text-sm font-bold text-slate-900">Hybrid Reciprocal Rank Fusion (RRF)</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Score-agnostic ranking fusion that combines ordinal candidate positions without requiring score calibration or threshold tuning across disparate models.
          </p>
          <div className="p-3 bg-slate-50 rounded-xl font-mono text-[11px] text-slate-700 border border-slate-100">
            RRF_score(d) = Σ_(m ∈ M) 1 / (k + rank_m(d)), with default k = 60
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Smooths out noise while combining lexical exact-match signals (BM25) with semantic conceptual recall (Dense).
          </p>
        </div>
      </div>

      {/* Dataset & Academic Scope */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 text-xs text-slate-600 leading-relaxed">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
          <BookOpen className="w-4 h-4 text-sky-600" />
          <span>The Enron Email Dataset & Ethical Notice</span>
        </h3>
        <p>
          The Enron corpus is a historical archive of real enterprise correspondence collected by the Federal Energy Regulatory Commission (FERC) during its inquiry into the collapse of Enron Corporation. It was subsequently processed and released to the research community by William Cohen and researchers at Carnegie Mellon University (CMU).
        </p>
        <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2.5 text-amber-900 text-xs">
          <ShieldAlert className="w-4 h-4 text-amber-700 mt-0.5 flex-shrink-0" />
          <div>
            <strong>Academic Research Use Disclaimer:</strong> The emails indexed in this application represent authentic historical business records. They are presented strictly for academic research, education, and algorithmic comparison in Information Retrieval.
          </div>
        </div>
      </div>

      {/* Academic Citations */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 text-xs text-slate-600">
        <h3 className="text-sm font-bold text-slate-900">Key Academic References</h3>
        <ul className="list-disc pl-5 space-y-1.5 text-slate-600">
          <li>
            <strong>Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009).</strong> <em>Reciprocal rank fusion outperforms condorcet and individual rank learning methods.</em> SIGIR '09.
          </li>
          <li>
            <strong>Robertson, S., & Zaragoza, H. (2009).</strong> <em>The probabilistic relevance framework: BM25 and beyond.</em> Foundations and Trends in Information Retrieval.
          </li>
          <li>
            <strong>Reimers, N., & Gurevych, I. (2019).</strong> <em>Sentence-BERT: Sentence embeddings using Siamese BERT-networks.</em> EMNLP 2019.
          </li>
          <li>
            <strong>Klimt, B., & Yang, Y. (2004).</strong> <em>The Enron Mobile Dataset: New Resources for E-Mail Analysis.</em> CEAS 2004.
          </li>
          <li>
            <strong>Järvelin, K., & Kekäläinen, J. (2002).</strong> <em>Cumulated gain-based evaluation of retrieval techniques.</em> ACM TOIS.
          </li>
        </ul>
      </div>
    </div>
  );
};
