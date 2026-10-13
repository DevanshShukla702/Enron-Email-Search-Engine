import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = "Executing ranked retrieval..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-16 text-center">
      <Loader2 className="w-8 h-8 text-sky-600 animate-spin mb-3" />
      <p className="text-sm font-medium text-slate-600">{message}</p>
      <span className="text-xs text-slate-400 mt-1">Ranking over 10,000 indexed Enron emails</span>
    </div>
  );
};
