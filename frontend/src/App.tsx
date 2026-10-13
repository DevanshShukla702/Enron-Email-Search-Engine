import React, { useState, useEffect } from 'react';
import { Search, BarChart3, Database, Info, Activity } from 'lucide-react';
import { SearchPage } from './pages/SearchPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AboutPage } from './pages/AboutPage';
import { getSystemHealth } from './services/api';
import { HealthStatus } from './types';

type ActiveTab = 'search' | 'evaluation' | 'analytics' | 'about';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('search');
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    getSystemHealth()
      .then(setHealth)
      .catch((err) => console.warn('Health check unavailable:', err));
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-900 font-sans selection:bg-sky-100 selection:text-sky-900">
      {/* Top Application Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Project Brand & Subtitle */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-sm font-black text-lg">
                IR
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-base text-slate-900 tracking-tight">
                    Enterprise Email Retrieval
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                    Project 16
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 font-medium">
                  TF-IDF · BM25 · Dense Semantic Retrieval · Hybrid RRF
                </div>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex items-center gap-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200/80">
              <button
                onClick={() => setActiveTab('search')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'search'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <Search className="w-3.5 h-3.5" />
                <span>Search</span>
              </button>

              <button
                onClick={() => setActiveTab('evaluation')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'evaluation'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <BarChart3 className="w-3.5 h-3.5" />
                <span>Evaluation</span>
              </button>

              <button
                onClick={() => setActiveTab('analytics')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'analytics'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <Database className="w-3.5 h-3.5" />
                <span>Corpus Analytics</span>
              </button>

              <button
                onClick={() => setActiveTab('about')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'about'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <Info className="w-3.5 h-3.5" />
                <span>About</span>
              </button>
            </nav>

            {/* Health / System Status Pill */}
            <div className="hidden lg:flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 text-[11px] font-medium border border-slate-200">
                <span
                  className={`w-2 h-2 rounded-full ${
                    health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'
                  }`}
                ></span>
                <span>
                  {health ? `${health.indexed_documents.toLocaleString()} emails indexed` : 'Connecting...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'search' && <SearchPage />}
        {activeTab === 'evaluation' && <EvaluationPage />}
        {activeTab === 'analytics' && <AnalyticsPage />}
        {activeTab === 'about' && <AboutPage />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            <strong>Enron Email Information Retrieval System</strong> · Academic IR Project 16
          </div>
          <div className="text-slate-400">
            Powered by scikit-learn · rank_bm25 · sentence-transformers · FAISS · FastAPI · React
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
