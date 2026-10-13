import React from 'react';
import { Filter, X } from 'lucide-react';
import { SearchFilters } from '../types';

interface FilterPanelProps {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
  onClear: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onChange,
  onClear,
  isOpen,
  onToggle
}) => {
  const hasActiveFilters = Boolean(
    filters.sender || filters.folder || filters.date_from || filters.date_to
  );

  return (
    <div className="border border-slate-200 bg-white rounded-xl shadow-sm mb-4 transition-all">
      <div className="flex items-center justify-between px-4 py-2.5">
        <button
          onClick={onToggle}
          className="flex items-center gap-2 text-xs font-semibold text-slate-700 hover:text-slate-900 transition-colors"
        >
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span>Metadata Filters</span>
          {hasActiveFilters && (
            <span className="w-2 h-2 rounded-full bg-sky-500 inline-block"></span>
          )}
        </button>

        {hasActiveFilters && (
          <button
            onClick={onClear}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-red-600 transition-colors"
          >
            <X className="w-3 h-3" />
            <span>Clear Filters</span>
          </button>
        )}
      </div>

      {isOpen && (
        <div className="px-4 pb-4 pt-1 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 border-t border-slate-100">
          <div>
            <label className="block text-[11px] font-medium text-slate-600 mb-1">Sender Email</label>
            <input
              type="text"
              placeholder="e.g. michelle.cash@enron.com"
              value={filters.sender || ''}
              onChange={(e) => onChange({ ...filters, sender: e.target.value || undefined })}
              className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-600 mb-1">Folder Name</label>
            <input
              type="text"
              placeholder="e.g. sent_items or meetings"
              value={filters.folder || ''}
              onChange={(e) => onChange({ ...filters, folder: e.target.value || undefined })}
              className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-600 mb-1">Date From</label>
            <input
              type="date"
              value={filters.date_from || ''}
              onChange={(e) => onChange({ ...filters, date_from: e.target.value || undefined })}
              className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-600 mb-1">Date To</label>
            <input
              type="date"
              value={filters.date_to || ''}
              onChange={(e) => onChange({ ...filters, date_to: e.target.value || undefined })}
              className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};
