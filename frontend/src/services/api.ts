import type { IndustrySummary, IndustryDetail, QueryResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export interface AuthSession {
  access_token: string;
  token_type: string;
  role: "CXO" | "Admin" | "Operator";
  username: string;
  full_name: string;
}

const SESSION_KEY = "nebula9.session";

export function getAuthSession(): AuthSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as AuthSession) : null;
  } catch {
    return null;
  }
}

function saveAuthSession(session: AuthSession) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearAuthSession() {
  sessionStorage.removeItem(SESSION_KEY);
}

async function authorizedFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const session = getAuthSession();
  const headers = new Headers(init.headers);
  if (session?.access_token) headers.set("Authorization", `Bearer ${session.access_token}`);
  return fetch(input, { ...init, headers });
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchAvailableIndustries(): Promise<IndustrySummary[]> {
  const res = await fetch(`${API_BASE}/config/industries`);
  if (!res.ok) throw new Error("Failed to load industries");
  return res.json();
}

export async function fetchActiveIndustry(): Promise<IndustryDetail> {
  const res = await fetch(`${API_BASE}/config/active`);
  if (!res.ok) throw new Error("Failed to load active industry");
  return res.json();
}

export async function switchActiveIndustry(industryId: string): Promise<any> {
  const res = await authorizedFetch(`${API_BASE}/config/active`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ industry_id: industryId }),
  });
  if (!res.ok) throw new Error("Failed to switch industry");
  return res.json();
}

export async function executeQuery(query: string, industryId?: string): Promise<QueryResponse> {
  const res = await authorizedFetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      industry_id: industryId,
    }),
  });
  if (!res.ok) throw new Error("Query execution failed");
  return res.json();
}

export async function loginUser(username: string, password: string): Promise<AuthSession> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail || "We couldn’t sign you in. Check your username and password.");
  }
  const session = (await res.json()) as AuthSession;
  saveAuthSession(session);
  return session;
}
