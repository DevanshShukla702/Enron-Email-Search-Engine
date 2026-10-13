export interface SearchFilters {
  sender?: string;
  folder?: string;
  date_from?: string;
  date_to?: string;
}

export interface SearchRequest {
  query: string;
  method: 'tfidf' | 'bm25' | 'dense' | 'rrf';
  top_k: number;
  filters?: SearchFilters;
  thread_mode?: boolean;
}

export interface SearchResultItem {
  document_id: string;
  rank: number;
  score: number;
  subject: string;
  sender: string;
  recipients: string;
  date?: string;
  folder?: string;
  snippet: string;
  thread_id?: string;
  highlighted_snippet?: string;
  explanation?: {
    method: string;
    raw_score?: number;
    cosine_similarity?: number;
    semantic_similarity?: number;
    rrf_score?: number;
    rrf_k?: number;
    tfidf_rank?: number;
    tfidf_contrib?: number;
    bm25_rank?: number;
    bm25_contrib?: number;
    dense_rank?: number;
    dense_contrib?: number;
    models_contributing?: number;
    [key: string]: any;
  };
}

export interface SearchResponse {
  query: string;
  method: string;
  total_results: number;
  execution_time_ms: number;
  results: SearchResultItem[];
}

export interface CompareResponse {
  query: string;
  execution_time_ms: number;
  tfidf: SearchResultItem[];
  bm25: SearchResultItem[];
  dense: SearchResultItem[];
  rrf: SearchResultItem[];
}

export interface EmailDetail {
  document_id: string;
  message_id?: string;
  sender: string;
  sender_name?: string;
  recipients: string;
  cc?: string;
  bcc?: string;
  subject: string;
  date?: string;
  mailbox?: string;
  folder?: string;
  body: string;
  thread_id?: string;
  file_path?: string;
}

export interface ThreadResponse {
  thread_id: string;
  subject: string;
  message_count: number;
  messages: EmailDetail[];
}

export interface MetricScores {
  precision_at_10: number;
  recall: number;
  map: number;
  ndcg: number;
  precision_recall_curve: Array<{ recall: number; precision: number }>;
}

export interface EvaluationSummary {
  status: string;
  dataset_mode: string;
  corpus_size: number;
  query_count: number;
  qrels_count: number;
  metrics: {
    tfidf: MetricScores;
    bm25: MetricScores;
    dense: MetricScores;
    rrf: MetricScores;
  };
  metadata: Record<string, any>;
}

export interface PRPoint {
  recall: number;
  tfidf: number;
  bm25: number;
  dense: number;
  rrf: number;
}

export interface AnalyticsOverview {
  total_emails: number;
  unique_senders: number;
  unique_recipients: number;
  unique_mailboxes: number;
  date_range: { min?: string; max?: string };
  avg_body_length: number;
  top_senders: Array<{ sender: string; count: number }>;
  top_folders: Array<{ folder: string; count: number }>;
  emails_by_year: Array<{ year: string; count: number }>;
  thread_stats: {
    total_threads: number;
    avg_depth: number;
    max_depth: number;
  };
  index_stats: Record<string, boolean>;
}

export interface HealthStatus {
  status: string;
  database_connected: boolean;
  indexed_documents: number;
  dataset_mode: string;
  indexes: Record<string, boolean>;
}
