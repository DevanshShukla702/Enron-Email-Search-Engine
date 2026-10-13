import React, { useState } from 'react';
import { Mail, Calendar, Folder, MessageSquare, ChevronDown, ChevronUp, User, Info } from 'lucide-react';
import { SearchResultItem } from '../types';
import { formatDate, getMethodBadgeColor, getMethodName } from '../utils/formatting';

interface SearchResultCardProps {
  item: SearchResultItem;
  method: string;
  onOpenDetail: (docId: string) => void;
  onOpenThread: (threadId: string) => void;
}

export const SearchResultCard: React.FC<SearchResultCardProps> = ({
  item,
  method,
  onOpenDetail,
  onOpenThread
}) => {
  const [showExplanation, setShowExplanation] = useState(false);

  return (
    <div className="bg-white border border-slate-200 hover:border-slate-300 rounded-xl p-4 shadow-sm hover:shadow-md transition-all">
      {/* Top Header: Rank, Score Badge, Subject */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5 flex-1 min-w-0">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-100 text-slate-700 text-xs font-bold flex items-center justify-center mt-0.5 border border-slate-200">
            {item.rank}
          </span>
          <div className="min-w-0 flex-1">
            <h3
              onClick={() => onOpenDetail(item.document_id)}
              className="text-base font-semibold text-slate-900 hover:text-sky-600 cursor-pointer truncate transition-colors"
              title={item.subject}
            >
              {item.subject || '(No Subject)'}
            </h3>
            
            {/* Metadata Bar */}
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500 mt-1">
              <span className="flex items-center gap-1">
                <User className="w-3 h-3 text-slate-400" />
                <span className="font-medium text-slate-700">{item.sender}</span>
              </span>

              {item.date && (
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  <span>{formatDate(item.date)}</span>
                </span>
              )}

              {item.folder && (
                <span className="flex items-center gap-1 bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[11px]">
                  <Folder className="w-3 h-3 text-slate-400" />
                  <span>{item.folder}</span>
                </span>
              )}

              {item.thread_id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenThread(item.thread_id!);
                  }}
                  className="flex items-center gap-1 text-sky-600 hover:text-sky-700 hover:underline font-medium text-[11px]"
                >
                  <MessageSquare className="w-3 h-3" />
                  <span>Thread: {item.thread_id.substring(0, 10)}</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Score Pill with Model-Specific Label */}
        <div className="flex flex-col items-end flex-shrink-0">
          <span
            title={
              method === 'bm25'
                ? 'Okapi BM25 score (unbounded log-odds term saturation)'
                : method === 'dense'
                ? 'Cosine similarity of normalized 384-d sentence embeddings'
                : method === 'tfidf'
                ? 'Cosine similarity over sublinear TF x IDF sparse vector'
                : 'Reciprocal Rank Fusion score: sum of 1/(60 + rank_m)'
            }
            className={`text-xs font-semibold px-2 py-0.5 rounded-full border cursor-help ${getMethodBadgeColor(
              method
            )}`}
          >
            {method === 'bm25'
              ? `BM25: ${item.score}`
              : method === 'tfidf'
              ? `Cosine: ${item.score}`
              : method === 'dense'
              ? `Cosine: ${item.score}`
              : `RRF: ${item.score}`}
          </span>
          <span className="text-[10px] text-slate-400 mt-0.5">{getMethodName(method)}</span>
        </div>
      </div>

      {/* Snippet */}
      <div className="mt-3 text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
        {item.snippet}
      </div>

      {/* Footer Actions & Expandable Explanation */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <button
            onClick={() => onOpenDetail(item.document_id)}
            className="font-medium text-sky-600 hover:text-sky-700 flex items-center gap-1"
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Read Full Email</span>
          </button>

          {item.thread_id && (
            <button
              onClick={() => onOpenThread(item.thread_id!)}
              className="font-medium text-slate-600 hover:text-slate-800 ml-2"
            >
              View Thread
            </button>
          )}
        </div>

        <button
          onClick={() => setShowExplanation(!showExplanation)}
          className="text-slate-500 hover:text-slate-700 flex items-center gap-1 text-[11px] font-medium transition-colors"
        >
          <Info className="w-3 h-3 text-slate-400" />
          <span>Why this result?</span>
          {showExplanation ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {/* Expandable "Why this result?" Ranking Breakdown */}
      {showExplanation && item.explanation && (
        <div className="mt-2.5 p-3 bg-slate-100/70 border border-slate-200 rounded-lg text-xs space-y-1.5 animate-fadeIn">
          <div className="font-semibold text-slate-700 mb-1 flex items-center gap-1">
            <span>Algorithm Attribution:</span>
            <span className="font-normal text-slate-500 uppercase text-[10px] px-1 bg-white rounded border">
              {item.explanation.method}
            </span>
          </div>

          {item.explanation.method === 'tfidf' && (
            <div className="grid grid-cols-2 gap-2 text-slate-600">
              <div>Cosine Similarity: <strong className="text-slate-800">{item.explanation.cosine_similarity}</strong></div>
              <div>Representation: <span className="text-slate-700">Sublinear TF x IDF (L2 norm)</span></div>
            </div>
          )}

          {item.explanation.method === 'bm25' && (
            <div className="grid grid-cols-2 gap-2 text-slate-600">
              <div>BM25 Score: <strong className="text-slate-800">{item.explanation.raw_score}</strong></div>
              <div>Parameters: <span className="text-slate-700">k1={item.explanation.k1}, b={item.explanation.b}</span></div>
            </div>
          )}

          {item.explanation.method === 'dense' && (
            <div className="grid grid-cols-2 gap-2 text-slate-600">
              <div>Semantic Similarity: <strong className="text-slate-800">{item.explanation.semantic_similarity}</strong></div>
              <div>Encoder: <span className="text-slate-700">MiniLM-L6-v2 (384-d FAISS)</span></div>
            </div>
          )}

          {item.explanation.method === 'rrf' && (
            <div className="space-y-1 text-slate-600">
              <div className="text-[11px] text-slate-500">
                Formula: <code className="bg-white px-1 py-0.5 rounded text-slate-800 font-mono text-[10px]">RRF(d) = Σ 1 / (60 + rank_m)</code>
              </div>
              <div className="grid grid-cols-3 gap-2 pt-1 border-t border-slate-200/60 text-[11px]">
                <div className="bg-white p-1.5 rounded border border-slate-200">
                  <span className="text-slate-400 block text-[9px] uppercase">TF-IDF</span>
                  <span className="font-semibold text-slate-700">
                    {item.explanation.tfidf_rank ? `Rank #${item.explanation.tfidf_rank}` : 'Unranked'}
                  </span>
                  <span className="text-[10px] text-slate-500 block">+{item.explanation.tfidf_contrib}</span>
                </div>
                <div className="bg-white p-1.5 rounded border border-slate-200">
                  <span className="text-slate-400 block text-[9px] uppercase">BM25</span>
                  <span className="font-semibold text-slate-700">
                    {item.explanation.bm25_rank ? `Rank #${item.explanation.bm25_rank}` : 'Unranked'}
                  </span>
                  <span className="text-[10px] text-slate-500 block">+{item.explanation.bm25_contrib}</span>
                </div>
                <div className="bg-white p-1.5 rounded border border-slate-200">
                  <span className="text-slate-400 block text-[9px] uppercase">Dense</span>
                  <span className="font-semibold text-slate-700">
                    {item.explanation.dense_rank ? `Rank #${item.explanation.dense_rank}` : 'Unranked'}
                  </span>
                  <span className="text-[10px] text-slate-500 block">+{item.explanation.dense_contrib}</span>
                </div>
              </div>
              <div className="pt-1 text-[11px] text-slate-700 font-medium">
                Final RRF Fusion Score: <strong className="text-slate-900">{item.explanation.rrf_score}</strong>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
