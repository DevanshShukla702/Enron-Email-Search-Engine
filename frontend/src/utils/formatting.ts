export function formatDate(dateStr?: string): string {
  if (!dateStr) return 'Unknown Date';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
}

export function formatScore(score: number, method: string): string {
  if (method === 'rrf') {
    return score.toFixed(5);
  }
  if (method === 'tfidf' || method === 'dense') {
    return score.toFixed(4);
  }
  return score.toFixed(2);
}

export function getMethodBadgeColor(method: string): string {
  switch (method.toLowerCase()) {
    case 'tfidf':
      return 'bg-blue-50 text-blue-700 border-blue-200';
    case 'bm25':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'dense':
      return 'bg-purple-50 text-purple-700 border-purple-200';
    case 'rrf':
      return 'bg-rose-50 text-rose-700 border-rose-200';
    default:
      return 'bg-slate-50 text-slate-700 border-slate-200';
  }
}

export function getMethodName(method: string): string {
  switch (method.toLowerCase()) {
    case 'tfidf':
      return 'TF-IDF (Cosine)';
    case 'bm25':
      return 'BM25 (Probabilistic)';
    case 'dense':
      return 'Dense Semantic';
    case 'rrf':
      return 'Hybrid RRF';
    default:
      return method.toUpperCase();
  }
}
