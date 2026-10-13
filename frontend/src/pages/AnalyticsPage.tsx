import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';
import { Mail, Users, Folder, MessageSquare, Database, ShieldCheck } from 'lucide-react';
import { getAnalyticsOverview } from '../services/api';
import { AnalyticsOverview } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAnalyticsOverview();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load corpus analytics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Aggregating corpus analytics from SQLite..." />;
  if (error) return <ErrorState title="Analytics Unavailable" message={error} onRetry={fetchAnalytics} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Corpus IR Analytics & Distribution
          </h1>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
            Structural insights into the indexed 10,000 document Enron collection: sender concentration, temporal distribution,
            folder allocations, and conversation thread topologies.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            Active SQLite Metadata Index
          </span>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center">
            <Mail className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Total Emails</span>
            <div className="text-xl font-black text-slate-900">{data.total_emails.toLocaleString()}</div>
            <span className="text-[11px] text-slate-500">Indexed documents</span>
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Unique Senders</span>
            <div className="text-xl font-black text-slate-900">{data.unique_senders.toLocaleString()}</div>
            <span className="text-[11px] text-slate-500">{data.unique_mailboxes} executive mailboxes</span>
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <MessageSquare className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Total Threads</span>
            <div className="text-xl font-black text-slate-900">{data.thread_stats.total_threads.toLocaleString()}</div>
            <span className="text-[11px] text-slate-500">Avg depth: {data.thread_stats.avg_depth} msgs</span>
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase">Avg Body Length</span>
            <div className="text-xl font-black text-slate-900">{Math.round(data.avg_body_length).toLocaleString()}</div>
            <span className="text-[11px] text-slate-500">Characters per message</span>
          </div>
        </div>
      </div>

      {/* Two Column Visualizations: Volume by Year & Top Senders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email Volume by Year */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-1">Email Volume Over Time (By Year)</h3>
          <p className="text-xs text-slate-500 mb-4">Chronological frequency capturing peak Enron corporate correspondence</p>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.emails_by_year}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.5rem',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" name="Emails" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top 10 Senders */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-1">Top Active Senders</h3>
          <p className="text-xs text-slate-500 mb-4">Prominent correspondents across indexed executive archives</p>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_senders.slice(0, 7)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis
                  dataKey="sender"
                  type="category"
                  width={140}
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  tickFormatter={(val) => val.split('@')[0]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.5rem',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" name="Emails Sent" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Folder Distribution Breakdown */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-1">Corpus Folder Distribution</h3>
        <p className="text-xs text-slate-500 mb-4">Categorization of emails by mailbox folder name</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {data.top_folders.map((f, i) => (
            <div key={i} className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs">
              <div className="flex items-center gap-1.5 text-slate-600 font-semibold truncate mb-1">
                <Folder className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                <span className="truncate">{f.folder || 'root'}</span>
              </div>
              <span className="text-base font-extrabold text-slate-900">{f.count.toLocaleString()}</span>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                {((f.count / data.total_emails) * 100).toFixed(1)}% of corpus
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
