import React from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';

interface SearchBarProps {
  query: string;
  onQueryChange: (q: string) => void;
  onSearch: () => void;
  topK: number;
  onTopKChange: (k: number) => void;
  threadMode: boolean;
  onThreadModeToggle: (enabled: boolean) => void;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  onQueryChange,
  onSearch,
  topK,
  onTopKChange,
  threadMode,
  onThreadModeToggle,
  isLoading
}) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm mb-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search email subjects, bodies, senders, and threads (e.g. 'California power market FERC')..."
            className="w-full text-sm pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all text-slate-800 placeholder-slate-400"
          />
        </div>

        <button
          onClick={onSearch}
          disabled={isLoading || !query.trim()}
          className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white font-medium text-sm rounded-lg shadow-sm transition-colors flex items-center gap-2"
        >
          {isLoading ? (
            <span>Retrieving...</span>
          ) : (
            <>
              <span>Search</span>
            </>
          )}
        </button>
      </div>

      {/* Auxiliary controls: Top-K & Thread View Mode */}
      <div className="flex flex-wrap items-center justify-between gap-4 mt-3 pt-2.5 border-t border-slate-100 text-xs text-slate-600">
        <div className="flex items-center gap-3">
          <span className="font-medium text-slate-500 flex items-center gap-1">
            <SlidersHorizontal className="w-3.5 h-3.5" /> Top K:
          </span>
          <div className="flex items-center gap-1.5">
            {[10, 20, 50].map((k) => (
              <button
                key={k}
                onClick={() => onTopKChange(k)}
                className={`px-2.5 py-1 rounded text-xs font-semibold transition-all ${
                  topK === k
                    ? 'bg-slate-800 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {k}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={threadMode}
              onChange={(e) => onThreadModeToggle(e.target.checked)}
              className="rounded border-slate-300 text-sky-600 focus:ring-sky-500 w-3.5 h-3.5"
            />
            <span className="font-medium text-slate-700">Group by Thread View</span>
          </label>
        </div>
      </div>
    </div>
  );
};
