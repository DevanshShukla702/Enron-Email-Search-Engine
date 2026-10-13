import React from 'react';
import { ArrowDown, Database, Cpu, Layers, GitMerge, BarChart2 } from 'lucide-react';

export const ArchitectureCard: React.FC = () => {
  const steps = [
    {
      icon: <Database className="w-5 h-5 text-sky-600" />,
      title: "Raw Enron Corpus Acquisition",
      desc: "CMU May 2015 release (500k+ emails), sampled to 10,000 document demo corpus in data/raw/maildir"
    },
    {
      icon: <Cpu className="w-5 h-5 text-indigo-600" />,
      title: "Email Parsing & Thread Reconstruction",
      desc: "Standard RFC-2822 parsing into SQLite. In-Reply-To & Subject grouping via Disjoint-Set Union (5,675 threads)"
    },
    {
      icon: <Layers className="w-5 h-5 text-emerald-600" />,
      title: "Text Preprocessing & Field Weighting",
      desc: "Unicode NFKD, HTML strip, lowercasing, stop-word removal, Porter stemming. Subject: 2.0x, Body: 1.0x"
    },
    {
      icon: <Cpu className="w-5 h-5 text-purple-600" />,
      title: "Multi-Paradigm Indexing",
      desc: "1) TF-IDF Sparse Matrix (212k features), 2) BM25 Okapi Index, 3) Sentence Transformer (all-MiniLM-L6-v2) FAISS Index"
    },
    {
      icon: <GitMerge className="w-5 h-5 text-rose-600" />,
      title: "Hybrid Reciprocal Rank Fusion",
      desc: "RRF(d) = Σ 1 / (60 + rank_m(d)) combining lexical and dense semantic rankings without uncalibrated score distortion"
    },
    {
      icon: <BarChart2 className="w-5 h-5 text-amber-600" />,
      title: "Evaluation & FastAPI/React UI",
      desc: "TREC-style benchmark with 12 enterprise queries, P@10, Recall, MAP, nDCG, and 11-point PR curves"
    }
  ];

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <h3 className="text-base font-bold text-slate-900 mb-1">Information Retrieval Pipeline Architecture</h3>
      <p className="text-xs text-slate-500 mb-6">
        End-to-end data lifecycle from raw maildir files to ranked retrieval and benchmark evaluation
      </p>

      <div className="relative border-l-2 border-slate-200 ml-4 space-y-6">
        {steps.map((step, idx) => (
          <div key={idx} className="relative pl-6">
            <div className="absolute -left-3.5 top-0.5 w-7 h-7 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center shadow-xs">
              {step.icon}
            </div>
            <div>
              <span className="text-xs font-bold text-slate-900">{step.title}</span>
              <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
