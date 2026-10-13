import React, { useState, useEffect } from 'react';
import { X, Mail, Calendar, Folder, MessageSquare, User, Users, Copy, Check } from 'lucide-react';
import { EmailDetail, ThreadResponse } from '../types';
import { getEmailDetail, getThreadDetail } from '../services/api';
import { formatDate } from '../utils/formatting';

interface EmailDetailModalProps {
  documentId: string | null;
  threadId: string | null;
  onClose: () => void;
  onSelectThread: (threadId: string) => void;
}

export const EmailDetailModal: React.FC<EmailDetailModalProps> = ({
  documentId,
  threadId,
  onClose,
  onSelectThread
}) => {
  const [email, setEmail] = useState<EmailDetail | null>(null);
  const [threadData, setThreadData] = useState<ThreadResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'single' | 'thread'>(threadId ? 'thread' : 'single');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (threadId) {
      setViewMode('thread');
      fetchThread(threadId);
    } else if (documentId) {
      setViewMode('single');
      fetchEmail(documentId);
    }
  }, [documentId, threadId]);

  const fetchEmail = async (id: string) => {
    setLoading(true);
    try {
      const data = await getEmailDetail(id);
      setEmail(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchThread = async (tId: string) => {
    setLoading(true);
    try {
      const data = await getThreadDetail(tId);
      setThreadData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyBody = () => {
    if (email?.body) {
      navigator.clipboard.writeText(email.body);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!documentId && !threadId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200 animate-fadeIn">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center">
              {viewMode === 'thread' ? <MessageSquare className="w-5 h-5" /> : <Mail className="w-5 h-5" />}
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 truncate max-w-xl">
                {viewMode === 'thread'
                  ? `Conversation Thread: ${threadData?.subject || '(Loading...)'}`
                  : email?.subject || '(No Subject)'}
              </h2>
              <span className="text-xs text-slate-500">
                {viewMode === 'thread'
                  ? `${threadData?.message_count || 0} chronological messages`
                  : `Document ID: ${email?.document_id || ''}`}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {email?.thread_id && viewMode === 'single' && (
              <button
                onClick={() => {
                  setViewMode('thread');
                  fetchThread(email.thread_id!);
                }}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5"
              >
                <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
                <span>View Full Thread</span>
              </button>
            )}

            {viewMode === 'thread' && email && (
              <button
                onClick={() => setViewMode('single')}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
              >
                Back to Email
              </button>
            )}

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg hover:bg-slate-200 text-slate-500 hover:text-slate-800 flex items-center justify-center transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-20 text-center text-sm text-slate-500">Loading message details...</div>
          ) : viewMode === 'thread' && threadData ? (
            /* Thread Chronological View */
            <div className="space-y-6">
              <div className="text-xs text-slate-500 pb-2 border-b border-slate-100">
                Thread ID: <code className="font-mono bg-slate-100 px-1 py-0.5 rounded">{threadData.thread_id}</code>
              </div>
              <div className="space-y-4">
                {threadData.messages.map((msg, i) => (
                  <div key={msg.document_id} className="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                    <div className="flex items-start justify-between border-b border-slate-200/60 pb-2 mb-3 text-xs">
                      <div>
                        <span className="font-bold text-slate-900">#{i + 1} {msg.sender}</span>
                        <div className="text-slate-500 mt-0.5">To: {msg.recipients || 'Undisclosed'}</div>
                      </div>
                      <div className="text-right text-slate-500">
                        <span>{formatDate(msg.date)}</span>
                        {msg.folder && <div className="text-[10px] text-slate-400">{msg.folder}</div>}
                      </div>
                    </div>
                    <pre className="text-xs font-sans text-slate-800 whitespace-pre-wrap leading-relaxed">
                      {msg.body || '(Empty body)'}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          ) : email ? (
            /* Single Email View */
            <div className="space-y-4">
              {/* Header Fields Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                <div className="flex items-start gap-2">
                  <User className="w-4 h-4 text-slate-400 mt-0.5" />
                  <div>
                    <span className="text-slate-400 font-medium block">From:</span>
                    <span className="font-semibold text-slate-800">{email.sender_name ? `${email.sender_name} <${email.sender}>` : email.sender}</span>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <Users className="w-4 h-4 text-slate-400 mt-0.5" />
                  <div>
                    <span className="text-slate-400 font-medium block">To:</span>
                    <span className="font-medium text-slate-700 break-words">{email.recipients || '(None)'}</span>
                  </div>
                </div>

                {email.cc && (
                  <div className="flex items-start gap-2 sm:col-span-2">
                    <span className="text-slate-400 font-medium w-4">CC:</span>
                    <span className="font-medium text-slate-700 break-words">{email.cc}</span>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <div>
                    <span className="text-slate-400 font-medium">Date: </span>
                    <span className="font-medium text-slate-700">{formatDate(email.date)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Folder className="w-4 h-4 text-slate-400" />
                  <div>
                    <span className="text-slate-400 font-medium">Folder: </span>
                    <span className="font-medium text-slate-700">{email.folder || 'inbox'} (Mailbox: {email.mailbox})</span>
                  </div>
                </div>
              </div>

              {/* Email Body */}
              <div className="relative">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-xs font-semibold text-slate-700">
                  <span>Message Body</span>
                  <button
                    onClick={handleCopyBody}
                    className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-800 transition-colors"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy Text'}</span>
                  </button>
                </div>
                <div className="p-4 bg-white border border-slate-200 rounded-xl overflow-x-auto">
                  <pre className="text-xs font-mono text-slate-800 whitespace-pre-wrap leading-relaxed">
                    {email.body || '(Empty body)'}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-400">Failed to load email.</div>
          )}
        </div>
      </div>
    </div>
  );
};
