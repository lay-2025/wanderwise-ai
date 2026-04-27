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
