import React from 'react';

interface MetricCardProps {
  label: string;
  value: number | string;
  bestMethod?: string;
  description: string;
  color?: 'blue' | 'emerald' | 'purple' | 'amber';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  bestMethod,
  description,
  color = 'blue'
}) => {
  const colorMap = {
    blue: 'border-l-sky-500 text-sky-600 bg-sky-50/30',
    emerald: 'border-l-emerald-500 text-emerald-600 bg-emerald-50/30',
    purple: 'border-l-purple-500 text-purple-600 bg-purple-50/30',
    amber: 'border-l-amber-500 text-amber-600 bg-amber-50/30'
  };

  return (
    <div className={`p-4 rounded-xl border border-slate-200 border-l-4 ${colorMap[color]} bg-white shadow-sm`}>
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
      <div className="flex items-baseline justify-between mt-2">
        <span className="text-2xl font-extrabold text-slate-900 tracking-tight">{value}</span>
        {bestMethod && (
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full">
            Best: {bestMethod}
          </span>
        )}
      </div>
      <p className="text-xs text-slate-500 mt-2 leading-relaxed">{description}</p>
    </div>
  );
};
