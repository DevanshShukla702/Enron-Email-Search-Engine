import React, { useState, useEffect } from 'react';
import { MetricCard } from '../components/MetricCard';
import { ComparisonTable } from '../components/ComparisonTable';
import { PrecisionRecallChart } from '../components/PrecisionRecallChart';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { getEvaluationSummary, getPrecisionRecallData } from '../services/api';
import { EvaluationSummary, PRPoint } from '../types';
import { CheckCircle2, ShieldCheck, Database, Calendar } from 'lucide-react';

export const EvaluationPage: React.FC = () => {
  const [summary, setSummary] = useState<EvaluationSummary | null>(null);
  const [prPoints, setPrPoints] = useState<PRPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEvaluationData();
  }, []);

  const fetchEvaluationData = async () => {
    setLoading(true);
    setError(null);
    try {
      const summaryData = await getEvaluationSummary();
      const prData = await getPrecisionRecallData();
      setSummary(summaryData);
      setPrPoints(prData.points);
    } catch (err: any) {
      setError(err.message || 'Failed to load evaluation metrics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading evaluation benchmark data..." />;
  if (error) return <ErrorState title="Evaluation Data Unavailable" message={error} onRetry={fetchEvaluationData} />;
  if (!summary) return null;

  const { metrics, metadata } = summary;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Empirical IR Evaluation Dashboard
            </h1>
            <span className="flex items-center gap-1 text-[11px] font-semibold bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full border border-slate-200">
              <ShieldCheck className="w-3.5 h-3.5 text-slate-500" />
              Offline Benchmark (12 Queries · 67 Judgments)
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
            Standard Information Retrieval evaluation metrics computed across {summary.query_count} curated enterprise information needs
            and {summary.qrels_count} graded relevance judgments over {summary.corpus_size.toLocaleString()} indexed Enron documents.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-1.5 text-slate-600">
            <Database className="w-3.5 h-3.5 text-slate-400" />
            <span>Corpus: <strong>{summary.corpus_size.toLocaleString()}</strong></span>
          </div>
          <div className="px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center gap-1.5 text-slate-600">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>Date: <strong>{metadata.timestamp ? new Date(metadata.timestamp).toLocaleDateString() : 'Recent'}</strong></span>
          </div>
        </div>
      </div>

      {/* KPI Cards: P@10, Recall, MAP, nDCG */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Precision @ 10"
          value={metrics.bm25.precision_at_10.toFixed(4)}
          bestMethod="BM25"
          color="emerald"
          description="Proportion of relevant emails among the top 10 retrieved documents. BM25 achieved highest precision on exact technical queries."
        />
        <MetricCard
          label="Recall"
          value={metrics.bm25.recall.toFixed(4)}
          bestMethod="BM25"
          color="blue"
          description="Fraction of all relevant information needs successfully retrieved. Hybrid RRF also attained high recall (0.5242)."
        />
        <MetricCard
          label="Mean Average Precision (MAP)"
          value={metrics.bm25.map.toFixed(4)}
          bestMethod="BM25"
          color="purple"
          description="Mean area under the precision-recall curve across queries. Measures early precision and ranking quality."
        />
        <MetricCard
          label="nDCG @ 10 (Graded)"
          value={metrics.bm25.ndcg.toFixed(4)}
          bestMethod="BM25"
          color="amber"
          description="Normalized Discounted Cumulative Gain utilizing graded relevance (0=None, 1=Partial, 2=High). Heavy penalty for misplacing top docs."
        />
      </div>

      {/* Comparison Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">Retrieval Model Comparison</h2>
          <span className="text-xs text-slate-500 font-medium">Evaluated across all 12 queries</span>
        </div>
        <ComparisonTable metrics={metrics} />
      </div>

      {/* Precision-Recall Curves Chart */}
      {prPoints.length > 0 && <PrecisionRecallChart data={prPoints} />}

      {/* Evaluation Run Metadata & Methodology Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 text-xs text-slate-600 shadow-sm space-y-4">
        <div>
          <h4 className="font-bold text-slate-800 text-sm mb-1 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Benchmark Methodology & Empirical Findings</span>
          </h4>
          <p className="leading-relaxed text-slate-500">
            Computed offline by executing all 12 curated information needs against the 10,000 indexed documents and scoring against graded relevance judgments in <code className="font-mono bg-slate-100 px-1 py-0.5 rounded border border-slate-200">data/evaluation/qrels.tsv</code>.
          </p>
        </div>

        {/* Technical Explanations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/80">
            <span className="font-bold text-slate-800 block mb-1">Why BM25 Leads Across Metrics on Enron:</span>
            <p className="leading-relaxed text-slate-600 text-[11px]">
              Corporate correspondence heavily features domain-specific acronyms (e.g., <code className="bg-white px-1 rounded">CAISO</code>, <code className="bg-white px-1 rounded">FERC</code>, <code className="bg-white px-1 rounded">ADS</code>), executive names (<code className="bg-white px-1 rounded">Skilling</code>, <code className="bg-white px-1 rounded">Lay</code>), and contract identifiers. BM25’s non-linear term frequency saturation (k1=1.5) and document length normalization (b=0.75) prioritize exact token occurrences while preventing lengthy reply chains from dominating.
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/80">
            <span className="font-bold text-slate-800 block mb-1">Dense Semantic Retrieval Behavior:</span>
            <p className="leading-relaxed text-slate-600 text-[11px]">
              The pre-trained bi-encoder (<code className="bg-white px-1 rounded">all-MiniLM-L6-v2</code>) excels at conceptual paraphrases without exact keyword overlap, but maps specialized corporate acronyms and project codes to out-of-distribution vector representations unless fine-tuned on energy trading archives.
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/80">
            <span className="font-bold text-slate-800 block mb-1">Hybrid RRF Complementarity:</span>
            <p className="leading-relaxed text-slate-600 text-[11px]">
              Reciprocal Rank Fusion (<code className="bg-white px-1 rounded">k=60</code>) fuses ordinal ranks (RRF(d) = Σ 1 / (60 + rank_m)) without requiring uncalibrated score normalization between BM25 (unbounded log-odds) and Dense/TF-IDF (cosine). It produces a resilient top-10 ranking that bridges lexical and conceptual matches.
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/80">
            <span className="font-bold text-slate-800 block mb-1">Relevance Grading Scheme:</span>
            <p className="leading-relaxed text-slate-600 text-[11px]">
              Evaluated using 3-level graded relevance (0 = Not Relevant, 1 = Partially Relevant, 2 = Highly Relevant). Precision@10, Recall, and MAP apply binary threshold (rel ≥ 1). nDCG@10 weights graded relevance via (2^rel - 1) / log2(i + 1) with ideal discounted cumulative gain.
            </p>
          </div>
        </div>

        {/* Configuration Metadata Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 text-[11px]">
          <div><span className="text-slate-400 block text-[10px] uppercase">Dense Model:</span> <strong>{metadata.dense_model || 'all-MiniLM-L6-v2'}</strong></div>
          <div><span className="text-slate-400 block text-[10px] uppercase">BM25 Params:</span> <strong>k1 = 1.5, b = 0.75</strong></div>
          <div><span className="text-slate-400 block text-[10px] uppercase">RRF Smoothing:</span> <strong>k = 60</strong></div>
          <div><span className="text-slate-400 block text-[10px] uppercase">Index Scale:</span> <strong>10,000 Documents</strong></div>
        </div>
      </div>
    </div>
  );
};
