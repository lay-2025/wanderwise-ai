import type { TravelExtraction } from '@/types/extraction'

export type { TravelExtraction }

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} エラーが発生しました`);
  }
  return res.json();
}

export function login(email: string, password: string): Promise<User> {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(email: string, password: string, name: string): Promise<User> {
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, name }),
  });
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function getMe(): Promise<User | null> {
  try {
    return await request<User>("/api/auth/me");
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------
// セッション管理
// ---------------------------------------------------------------

export interface Session {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface SessionListResponse {
  sessions: Session[];
  total: number;
}

export interface SessionCreateResponse {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export function getSessions(): Promise<SessionListResponse> {
  return request<SessionListResponse>("/api/chat/sessions");
}

export function createSession(): Promise<SessionCreateResponse> {
  return request<SessionCreateResponse>("/api/chat/sessions", { method: "POST" });
}

export function renameSession(id: string, title: string): Promise<SessionCreateResponse> {
  return request<SessionCreateResponse>(`/api/chat/sessions/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

export async function deleteSession(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/chat/sessions/${id}`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) throw new Error(`${res.status} エラーが発生しました`);
}

// ---------------------------------------------------------------
// チャット
// ---------------------------------------------------------------

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface HistoryResponse {
  session_id: string;
  title: string | null;
  messages: ChatMessage[];
  total: number;
  limit: number;
  offset: number;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  extractions: unknown[];
}

export function getHistory(sessionId: string, limit = 100, offset = 0): Promise<HistoryResponse> {
  return request<HistoryResponse>(
    `/api/chat/history?session_id=${sessionId}&limit=${limit}&offset=${offset}`,
  );
}

export function sendChat(message: string, sessionId: string): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

// ---------------------------------------------------------------
// 旅行データ抽出 (travel_extractions)
// ---------------------------------------------------------------

export interface ExtractionsResponse {
  extractions: TravelExtraction[]
  total: number
}

export function getExtractions(sessionId: string): Promise<ExtractionsResponse> {
  return request<ExtractionsResponse>(`/api/data/travel?session_id=${sessionId}`)
}

// ---------------------------------------------------------------
// 学習ドキュメント (documents)
// ---------------------------------------------------------------

export type DocumentSource = 'chat' | 'upload' | 'manual'
export type DocumentStatus = 'pending' | 'processing' | 'vectorized' | 'failed'

export interface Document {
  id: string
  title: string
  source: DocumentSource
  status: DocumentStatus
  is_active: boolean
  chunks?: number | null
  size?: string
  url?: string | null
  created_at: string
  updated_at: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
}

/** ドキュメント一覧取得 */
export function getDocuments(): Promise<DocumentListResponse> {
  return request<DocumentListResponse>('/api/documents')
}

/** ドキュメント削除 */
export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/documents/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  })
  if (!res.ok) throw new Error(`${res.status} エラーが発生しました`)
}

/** RAG ON/OFF 切り替え */
export function toggleDocument(id: string): Promise<Document> {
  return request<Document>(`/api/documents/${id}/toggle`, { method: 'PATCH' })
}

/** URLからドキュメントを取り込む */
export function uploadDocumentFromUrl(title: string, url: string): Promise<Document> {
  return request<Document>('/api/documents/upload', {
    method: 'POST',
    body: JSON.stringify({ title, url }),
  })
}

// ---------------------------------------------------------------
// 学習・ベクトル検索 (learning)
// ---------------------------------------------------------------

export interface SearchResult {
  document_id: string
  document_title: string
  source: DocumentSource
  chunk: string
  score: number
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
}

export interface VisualizeResponse {
  clusters: { label: string; count: number; color?: string }[]
  points: { x: number; y: number; label: string; document_id: string }[]
  total_vectors: number
}

export interface RagCompareResponse {
  query: string
  without_rag: string
  with_rag: string
  sources_used: string[]
}

/** RAG類似度検索 */
export function searchDocuments(query: string): Promise<SearchResponse> {
  return request<SearchResponse>(`/api/learning/search?q=${encodeURIComponent(query)}`)
}

/** ベクトルデータ可視化情報取得 */
export function getVisualize(): Promise<VisualizeResponse> {
  return request<VisualizeResponse>('/api/learning/visualize')
}

/** RAGあり・なし比較 */
export function compareRag(query: string, sessionId: string): Promise<RagCompareResponse> {
  return request<RagCompareResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: query, session_id: sessionId, compare_mode: true }),
  })
}

/** ドキュメントをベクトル化 */
export function vectorizeDocument(documentId: string): Promise<{ task_id: string }> {
  return request<{ task_id: string }>('/api/learning/vectorize', {
    method: 'POST',
    body: JSON.stringify({ document_id: documentId }),
  })
}
