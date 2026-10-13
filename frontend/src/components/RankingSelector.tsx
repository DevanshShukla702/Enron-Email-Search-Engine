import React from 'react';

export type RankingMethod = 'tfidf' | 'bm25' | 'dense' | 'rrf';

interface RankingSelectorProps {
  currentMethod: RankingMethod;
  onMethodChange: (method: RankingMethod) => void;
  isCompareMode: boolean;
  onCompareToggle: (enabled: boolean) => void;
}

export const RankingSelector: React.FC<RankingSelectorProps> = ({
  currentMethod,
  onMethodChange,
  isCompareMode,
  onCompareToggle
}) => {
  const methods: Array<{ id: RankingMethod; label: string; badge: string; desc: string }> = [
    { id: 'tfidf', label: 'TF-IDF', badge: 'Classical', desc: 'Term frequency - Inverse document frequency with cosine similarity' },
    { id: 'bm25', label: 'BM25', badge: 'Probabilistic', desc: 'Okapi BM25 with term saturation and document length normalization' },
    { id: 'dense', label: 'Dense', badge: 'Semantic', desc: 'Sentence Transformer (all-MiniLM-L6-v2) embeddings with FAISS vector index' },
    { id: 'rrf', label: 'Hybrid RRF', badge: 'Fusion', desc: 'Reciprocal Rank Fusion (k=60) combining all 3 ranking streams' },
  ];

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 py-2 border-b border-slate-200">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-1">Ranking:</span>
        {methods.map((m) => {
          const isSelected = !isCompareMode && currentMethod === m.id;
          return (
            <button
              key={m.id}
              onClick={() => {
                if (isCompareMode) onCompareToggle(false);
                onMethodChange(m.id);
              }}
              title={m.desc}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isSelected
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <span>{m.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                  isSelected ? 'bg-sky-700 text-sky-100' : 'bg-slate-100 text-slate-500'
                }`}
              >
                {m.badge}
              </span>
            </button>
          );
        })}
      </div>

      <div>
        <button
          onClick={() => onCompareToggle(!isCompareMode)}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            isCompareMode
              ? 'bg-indigo-600 text-white shadow-sm ring-2 ring-indigo-300'
              : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200'
          }`}
        >
          <span>⚖️ Compare All 4 Models</span>
        </button>
      </div>
    </div>
  );
};
