import {
  SearchRequest,
  SearchResponse,
  CompareResponse,
  EmailDetail,
  ThreadResponse,
  EvaluationSummary,
  AnalyticsOverview,
  HealthStatus,
  PRPoint
} from '../types';

const BASE_URL = ''; // Relative path leverages Vite's proxy to http://127.0.0.1:8000

export async function searchEmails(params: SearchRequest): Promise<SearchResponse> {
  const res = await fetch(`${BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Search failed with status ${res.status}`);
  }
  return res.json();
}

export async function compareAllModels(params: SearchRequest): Promise<CompareResponse> {
  const res = await fetch(`${BASE_URL}/api/search/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Comparison failed with status ${res.status}`);
  }
  return res.json();
}

export async function getEmailDetail(documentId: string): Promise<EmailDetail> {
  const res = await fetch(`${BASE_URL}/api/email/${encodeURIComponent(documentId)}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch email detail');
  }
  return res.json();
}

export async function getThreadDetail(threadId: string): Promise<ThreadResponse> {
  const res = await fetch(`${BASE_URL}/api/thread/${encodeURIComponent(threadId)}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch thread detail');
  }
  return res.json();
}

export async function getEvaluationSummary(): Promise<EvaluationSummary> {
  const res = await fetch(`${BASE_URL}/api/evaluation/summary`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Evaluation summary unavailable');
  }
  return res.json();
}

export async function getPrecisionRecallData(): Promise<{ points: PRPoint[] }> {
  const res = await fetch(`${BASE_URL}/api/evaluation/precision-recall`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Precision-recall data unavailable');
  }
  return res.json();
}

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const res = await fetch(`${BASE_URL}/api/analytics/overview`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Analytics overview unavailable');
  }
  return res.json();
}

export async function getSystemHealth(): Promise<HealthStatus> {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Health check failed');
  }
  return res.json();
}
