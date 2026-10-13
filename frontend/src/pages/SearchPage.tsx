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

  const handleSearch = async (searchQuery: string = query) => {
    const q = searchQuery.trim();
    if (!q) return;

    setLoading(true);
    setError(null);

    try {
      if (isCompareMode) {
        const res = await compareAllModels({
          query: q,
          method: 'rrf',
          top_k: topK,
          filters,
          thread_mode: threadMode
        });
        setCompareResponse(res);
        setSingleResponse(null);
      } else {
        const res = await searchEmails({
          query: q,
          method,
          top_k: topK,
          filters,
          thread_mode: threadMode
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
    handleSearch(suggestedQuery);
  };

  return (
    <div className="space-y-4">
      {/* Search Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
              Enterprise Email Retrieval Engine
            </h1>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
              Academic Information Retrieval system executing over 10,000 authentic Enron email records across 
              classical (TF-IDF), probabilistic (BM25), dense semantic (MiniLM), and hybrid (RRF) paradigms.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Corpus: 10,000 Emails
            </span>
          </div>
        </div>

        <div className="mt-5">
          <SearchBar
            query={query}
            onQueryChange={setQuery}
            onSearch={() => handleSearch()}
            topK={topK}
            onTopKChange={setTopK}
            threadMode={threadMode}
            onThreadModeToggle={setThreadMode}
            isLoading={loading}
          />

          <RankingSelector
            currentMethod={method}
            onMethodChange={(m) => {
              setMethod(m);
              if (query.trim()) {
                // Rerun search with new method
                setTimeout(() => handleSearch(), 50);
              }
            }}
            isCompareMode={isCompareMode}
            onCompareToggle={(enabled) => {
              setIsCompareMode(enabled);
              if (query.trim()) {
                setTimeout(() => handleSearch(), 50);
              }
            }}
          />

          <FilterPanel
            filters={filters}
            onChange={(f) => setFilters(f)}
            onClear={() => setFilters({})}
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
