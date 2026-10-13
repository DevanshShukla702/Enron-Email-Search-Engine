import React from 'react';
import { Search } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  onSuggestionClick?: (query: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No Emails Found",
  description = "Try refining your search terms, changing the ranking method, or clearing active filters.",
  onSuggestionClick
}) => {
  const suggestions = [
    "California wholesale power market FERC",
    "CAISO automated dispatch system",
    "employee retention bonus agreements",
    "Transwestern pipeline capacity"
  ];

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm my-6">
      <div className="w-14 h-14 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 mb-4">
        <Search className="w-7 h-7" />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-md mb-6">{description}</p>

      {onSuggestionClick && (
        <div className="flex flex-col items-center">
          <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-2">Try searching for:</span>
          <div className="flex flex-wrap gap-2 justify-center max-w-lg">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => onSuggestionClick(s)}
                className="px-3 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition-colors"
              >
                "{s}"
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
