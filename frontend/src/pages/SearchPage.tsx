import React, { useState } from 'react';
import { SearchBar } from '../components/SearchBar';
import { RankingSelector, RankingMethod } from '../components/RankingSelector';
import { FilterPanel } from '../components/FilterPanel';
import { SearchResults } from '../components/SearchResults';
import { EmailDetailModal } from '../components/EmailDetailModal';
import { EmptyState } from '../components/EmptyState';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { searchEmails, compareAllModels } from '../services/api';
import { SearchFilters, SearchResponse, CompareResponse } from '../types';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState<RankingMethod>('rrf');
  const [isCompareMode, setIsCompareMode] = useState(false);
  const [topK, setTopK] = useState(10);
  const [threadMode, setThreadMode] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [singleResponse, setSingleResponse] = useState<SearchResponse | null>(null);
  const [compareResponse, setCompareResponse] = useState<CompareResponse | null>(null);

  // Modal state
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);

  const handleSearch = async (
    searchQuery?: string,
    compareOverride?: boolean,
    methodOverride?: RankingMethod,
    topKOverride?: number,
    filtersOverride?: SearchFilters,
    threadModeOverride?: boolean
  ) => {
    let q = (searchQuery !== undefined ? searchQuery : query).trim();
    const useCompare = compareOverride !== undefined ? compareOverride : isCompareMode;
    const currentMethod = methodOverride !== undefined ? methodOverride : method;
    const currentTopK = topKOverride !== undefined ? topKOverride : topK;
    const currentFilters = filtersOverride !== undefined ? filtersOverride : filters;
    const currentThreadMode = threadModeOverride !== undefined ? threadModeOverride : threadMode;

    // If user clicked compare with an empty query, provide a representative query to immediately showcase comparison
    if (!q) {
      if (useCompare) {
        q = 'CAISO automated dispatch system';
        setQuery(q);
      } else {
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      if (useCompare) {
        const res = await compareAllModels({
          query: q,
          method: 'rrf',
          top_k: currentTopK,
          filters: currentFilters,
          thread_mode: currentThreadMode
        });
        setCompareResponse(res);
        setSingleResponse(null);
      } else {
        const res = await searchEmails({
          query: q,
          method: currentMethod,
          top_k: currentTopK,
          filters: currentFilters,
          thread_mode: currentThreadMode
        });
        setSingleResponse(res);
        setCompareResponse(null);
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred during search.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestedQuery: string) => {
    setQuery(suggestedQuery);
    handleSearch(suggestedQuery, isCompareMode);
  };

  return (
    <div className="space-y-4">
      {/* Search Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Search enterprise email
            </h1>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
              Search email correspondence across 10,000 indexed Enron emails using lexical (TF-IDF), 
              probabilistic (BM25), dense semantic (MiniLM), or hybrid (RRF) retrieval.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Corpus: 10,000 Emails (Enron Subset)
            </span>
          </div>
        </div>

        <div className="mt-5">
          <SearchBar
            query={query}
            onQueryChange={setQuery}
            onSearch={() => handleSearch(query, isCompareMode)}
            topK={topK}
            onTopKChange={(k) => {
              setTopK(k);
              if (query.trim() || compareResponse || singleResponse) {
                handleSearch(query, isCompareMode, method, k);
              }
            }}
            threadMode={threadMode}
            onThreadModeToggle={(tm) => {
              setThreadMode(tm);
              if (query.trim() || compareResponse || singleResponse) {
                handleSearch(query, isCompareMode, method, topK, filters, tm);
              }
            }}
            isLoading={loading}
          />

          {/* Quick Example Query Chips */}
          <div className="flex flex-wrap items-center gap-1.5 mb-3 text-xs">
            <span className="text-[11px] font-medium text-slate-400 mr-1">Example queries:</span>
            {[
              'outlook migration',
              'CAISO automated dispatch system',
              'contract approval',
              'meeting schedule',
              'pipeline capacity'
            ].map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => handleSuggestionClick(example)}
                className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 text-[11px] font-medium transition-colors border border-slate-200/60"
              >
                {example}
              </button>
            ))}
          </div>

          <RankingSelector
            currentMethod={method}
            onMethodChange={(m) => {
              setMethod(m);
              setIsCompareMode(false);
              if (query.trim() || compareResponse || singleResponse) {
                handleSearch(query, false, m);
              }
            }}
            isCompareMode={isCompareMode}
            onCompareToggle={(enabled) => {
              setIsCompareMode(enabled);
              handleSearch(query, enabled);
            }}
          />

          <FilterPanel
            filters={filters}
            onChange={(f) => {
              setFilters(f);
              if (query.trim() || compareResponse || singleResponse) {
                handleSearch(query, isCompareMode, method, topK, f);
              }
            }}
            onClear={() => {
              setFilters({});
              if (query.trim() || compareResponse || singleResponse) {
                handleSearch(query, isCompareMode, method, topK, {});
              }
            }}
            isOpen={isFilterOpen}
            onToggle={() => setIsFilterOpen(!isFilterOpen)}
          />
        </div>
      </div>

      {/* Results Area */}
      {loading && <LoadingState />}

      {error && <ErrorState message={error} onRetry={() => handleSearch()} />}

      {!loading && !error && !singleResponse && !compareResponse && (
        <EmptyState
          title="Begin an Enterprise IR Search"
          description="Type a search query or select an authentic corporate inquiry below to explore retrieval rankings across models."
          onSuggestionClick={handleSuggestionClick}
        />
      )}

      {!loading && !error && (singleResponse || compareResponse) && (
        <SearchResults
          singleResponse={singleResponse}
          compareResponse={compareResponse}
          isCompareMode={isCompareMode}
          onOpenDetail={(docId) => {
            setActiveDocId(docId);
            setActiveThreadId(null);
          }}
          onOpenThread={(threadId) => {
            setActiveThreadId(threadId);
            setActiveDocId(null);
          }}
        />
      )}

      {/* Email / Thread Detail Modal */}
      <EmailDetailModal
        documentId={activeDocId}
        threadId={activeThreadId}
        onClose={() => {
          setActiveDocId(null);
          setActiveThreadId(null);
        }}
        onSelectThread={(tId) => {
          setActiveDocId(null);
          setActiveThreadId(tId);
        }}
      />
    </div>
  );
};
