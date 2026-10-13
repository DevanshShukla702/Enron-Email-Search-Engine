import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { PRPoint } from '../types';

interface PrecisionRecallChartProps {
  data: PRPoint[];
}

export const PrecisionRecallChart: React.FC<PrecisionRecallChartProps> = ({ data }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
      <div className="mb-4">
        <h4 className="text-sm font-bold text-slate-900">Interpolated Precision-Recall Curves</h4>
        <p className="text-xs text-slate-500 mt-0.5">
          Standard 11-point interpolated precision ($p_{'{'}interp{'}'}(r) = \max_{'{'}r' \ge r{'}'} p(r')$) across evaluation benchmark queries
        </p>
      </div>

      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="recall"
              label={{ value: 'Recall', position: 'insideBottom', offset: -10, fontSize: 12, fill: '#64748b' }}
              tick={{ fontSize: 11, fill: '#64748b' }}
              domain={[0, 1]}
            />
            <YAxis
              label={{ value: 'Precision', angle: -90, position: 'insideLeft', offset: 10, fontSize: 12, fill: '#64748b' }}
              tick={{ fontSize: 11, fill: '#64748b' }}
              domain={[0, 1]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '0.5rem',
                fontSize: '12px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />
            <Line
              type="monotone"
              dataKey="tfidf"
              name="TF-IDF (Cosine)"
              stroke="#2563eb"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="bm25"
              name="BM25 (Okapi)"
              stroke="#16a34a"
              strokeWidth={2}
              strokeDasharray="3 3"
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="dense"
              name="Dense (MiniLM)"
              stroke="#9333ea"
              strokeWidth={2}
              strokeDasharray="2 2"
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="rrf"
              name="Hybrid RRF (k=60)"
              stroke="#dc2626"
              strokeWidth={2.5}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
