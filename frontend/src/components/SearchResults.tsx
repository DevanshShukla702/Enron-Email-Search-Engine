import React from 'react';
import { SearchResponse, CompareResponse } from '../types';
import { SearchResultCard } from './SearchResultCard';
import { getMethodBadgeColor } from '../utils/formatting';

interface SearchResultsProps {
  singleResponse: SearchResponse | null;
  compareResponse: CompareResponse | null;
  isCompareMode: boolean;
  onOpenDetail: (docId: string) => void;
  onOpenThread: (threadId: string) => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  singleResponse,
  compareResponse,
  isCompareMode,
  onOpenDetail,
  onOpenThread
}) => {
  if (isCompareMode && compareResponse) {
    const columns: Array<{ key: 'tfidf' | 'bm25' | 'dense' | 'rrf'; title: string; subtitle: string }> = [
      { key: 'tfidf', title: 'TF-IDF', subtitle: 'Sublinear TF x IDF Cosine' },
      { key: 'bm25', title: 'BM25', subtitle: 'Okapi Probabilistic' },
      { key: 'dense', title: 'Dense Semantic', subtitle: 'all-MiniLM-L6-v2 FAISS' },
      { key: 'rrf', title: 'Hybrid RRF', subtitle: 'Reciprocal Rank Fusion (k=60)' },
    ];

    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-500 pb-2 border-b border-slate-200 gap-2">
          <div>
            <span>Comparative Retrieval for: <strong className="text-slate-800">"{compareResponse.query}"</strong></span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              Notice: Each model computes native scores (BM25 log-odds, TF-IDF/Dense cosine, RRF reciprocal sum). Compare by ranking order, not raw score magnitudes.
            </span>
          </div>
          <span className="flex-shrink-0 text-slate-600 font-medium">All 4 models executed in {compareResponse.execution_time_ms} ms</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {columns.map((col) => {
            const list = compareResponse[col.key] || [];
            return (
              <div key={col.key} className="flex flex-col bg-slate-100/60 p-3 rounded-xl border border-slate-200">
                <div className="mb-3 pb-2 border-b border-slate-200/80">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-800">{col.title}</span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getMethodBadgeColor(col.key)}`}>
                      {list.length} results
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500 block mt-0.5">{col.subtitle}</span>
                </div>

                <div className="space-y-3 flex-1 overflow-y-auto max-h-[750px] pr-1">
                  {list.length === 0 ? (
                    <div className="p-4 text-center text-xs text-slate-400">No results found</div>
                  ) : (
                    list.map((item) => (
                      <SearchResultCard
                        key={`${col.key}-${item.document_id}`}
                        item={item}
                        method={col.key}
                        onOpenDetail={onOpenDetail}
                        onOpenThread={onOpenThread}
                      />
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (singleResponse) {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-500 pb-2 border-b border-slate-200">
          <span>
            Found <strong className="text-slate-800">{singleResponse.total_results}</strong> ranked emails for{' '}
            <strong className="text-slate-800">"{singleResponse.query}"</strong> using{' '}
            <strong className="text-slate-800">{singleResponse.method.toUpperCase()}</strong>
          </span>
          <span>Retrieved in {singleResponse.execution_time_ms} ms</span>
        </div>

        <div className="space-y-3">
          {singleResponse.results.map((item) => (
            <SearchResultCard
              key={item.document_id}
              item={item}
              method={singleResponse.method}
              onOpenDetail={onOpenDetail}
              onOpenThread={onOpenThread}
            />
          ))}
        </div>
      </div>
    );
  }

  return null;
};
