import React from 'react';
import { MetricScores } from '../types';

interface ComparisonTableProps {
  metrics: {
    tfidf: MetricScores;
    bm25: MetricScores;
    dense: MetricScores;
    rrf: MetricScores;
  };
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({ metrics }) => {
  const methods = [
    { key: 'tfidf', name: 'TF-IDF (Cosine)', type: 'Classical Lexical' },
    { key: 'bm25', name: 'BM25 (Okapi)', type: 'Probabilistic Lexical' },
    { key: 'dense', name: 'Sentence Transformer', type: 'Dense Semantic' },
    { key: 'rrf', name: 'Hybrid RRF (k=60)', type: 'Reciprocal Rank Fusion' },
  ];

  // Find max values for each column to highlight
  const maxP10 = Math.max(...Object.values(metrics).map((m) => m.precision_at_10));
  const maxRec = Math.max(...Object.values(metrics).map((m) => m.recall));
  const maxMap = Math.max(...Object.values(metrics).map((m) => m.map));
  const maxNdcg = Math.max(...Object.values(metrics).map((m) => m.ndcg));

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left border-collapse text-xs">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
            <th className="py-3 px-4">Retrieval Method</th>
            <th className="py-3 px-4">Paradigm</th>
            <th className="py-3 px-4 text-right">Precision@10</th>
            <th className="py-3 px-4 text-right">Recall</th>
            <th className="py-3 px-4 text-right">MAP</th>
            <th className="py-3 px-4 text-right">nDCG@10</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
          {methods.map((m) => {
            const data = metrics[m.key as keyof typeof metrics];
            if (!data) return null;

            const isBestP10 = data.precision_at_10 === maxP10;
            const isBestRec = data.recall === maxRec;
            const isBestMap = data.map === maxMap;
            const isBestNdcg = data.ndcg === maxNdcg;

            return (
              <tr key={m.key} className="hover:bg-slate-50/80 transition-colors">
                <td className="py-3 px-4 font-bold text-slate-900">{m.name}</td>
                <td className="py-3 px-4 text-slate-500">{m.type}</td>
                <td className="py-3 px-4 text-right">
                  <span
                    className={`inline-block px-2 py-0.5 rounded ${
                      isBestP10 ? 'bg-emerald-100 text-emerald-800 font-bold' : ''
                    }`}
                  >
                    {data.precision_at_10.toFixed(4)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span
                    className={`inline-block px-2 py-0.5 rounded ${
                      isBestRec ? 'bg-emerald-100 text-emerald-800 font-bold' : ''
                    }`}
                  >
                    {data.recall.toFixed(4)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span
                    className={`inline-block px-2 py-0.5 rounded ${
                      isBestMap ? 'bg-emerald-100 text-emerald-800 font-bold' : ''
                    }`}
                  >
                    {data.map.toFixed(4)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span
                    className={`inline-block px-2 py-0.5 rounded ${
                      isBestNdcg ? 'bg-emerald-100 text-emerald-800 font-bold' : ''
                    }`}
                  >
                    {data.ndcg.toFixed(4)}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
