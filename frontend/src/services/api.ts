import type { IndustrySummary, IndustryDetail, QueryResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export interface AuthSession {
  access_token: string;
  token_type: string;
  role: "CXO" | "Admin" | "Operator" | "Auditor" | "Quality Analyst" | string;
  username: string;
  full_name: string;
}

export interface AuditLogItem {
  id: number;
  audit_id: string;
  timestamp: string;
  user_id?: number;
  username: string;
  role: string;
  industry_id: string;
  query_text: string;
  status: string;
  execution_time_ms: number;
  agents_invoked?: string;
  sources_accessed?: string[];
  citations_count: number;
  grounding_score?: number;
  conflicts_count: number;
  is_abstained: boolean;
  ip_address?: string;
  trace_stages?: Record<string, any>;
}

export interface AuditSummaryMetrics {
  total_queries: number;
  successful_queries: number;
  abstained_queries: number;
  security_blocked_queries: number;
  avg_latency_ms: number;
  avg_grounding_score: number;
  total_conflicts_detected: number;
  industries_breakdown: Record<string, number>;
  roles_breakdown: Record<string, number>;
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
  const response = await fetch(input, { ...init, headers });
  if (response.status === 401 && session?.access_token) {
    clearAuthSession();
    window.dispatchEvent(new Event("nebula9:session-expired"));
    throw new Error("Your session expired. Please sign in again.");
  }
  return response;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
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

export async function fetchAuditLogs(filters?: {
  page?: number;
  page_size?: number;
  industry?: string;
  role?: string;
  status?: string;
  search?: string;
}): Promise<{ total: number; page: number; page_size: number; logs: AuditLogItem[] }> {
  const params = new URLSearchParams();
  if (filters?.page) params.set("page", String(filters.page));
  if (filters?.page_size) params.set("page_size", String(filters.page_size));
  if (filters?.industry) params.set("industry", filters.industry);
  if (filters?.role) params.set("role", filters.role);
  if (filters?.status) params.set("status", filters.status);
  if (filters?.search) params.set("search", filters.search);

  const res = await authorizedFetch(`${API_BASE}/audit/logs?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function fetchAuditSummary(): Promise<AuditSummaryMetrics> {
  const res = await authorizedFetch(`${API_BASE}/audit/summary`);
  if (!res.ok) throw new Error("Failed to fetch audit summary");
  return res.json();
}

export interface EvaluationItemResult {
  eval_id: string;
  category: string;
  query: string;
  passed: boolean;
  grounding_score: number;
  target_min_grounding_score: number;
  citations_count: number;
  sources_found: string[];
  conflicts_detected: string[];
  expected_conflict_found: boolean;
  is_abstained: boolean;
  expected_abstention_matched: boolean;
  is_blocked_security: boolean;
  expected_security_matched: boolean;
  latency_ms: number;
  stage_latencies: Record<string, number>;
  failure_reasons: string[];
}

export interface EvaluationSuiteReport {
  run_timestamp: string;
  industry_id: string;
  total_cases: number;
  passed_cases: number;
  overall_pass_rate: number;
  avg_grounding_score: number;
  avg_latency_ms: number;
  median_latency_ms: number;
  p95_latency_ms: number;
  conflict_accuracy: number;
  abstention_accuracy: number;
  security_accuracy: number;
  results: EvaluationItemResult[];
}

export async function fetchEvaluationReport(): Promise<Record<string, EvaluationSuiteReport>> {
  const res = await authorizedFetch(`${API_BASE}/evaluation/latest`);
  if (!res.ok) throw new Error("Failed to load evaluation report");
  return res.json();
}

export async function triggerEvaluationRun(industryId: string = "all"): Promise<any> {
  const res = await authorizedFetch(`${API_BASE}/evaluation/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ industry_id: industryId }),
  });
  if (!res.ok) throw new Error("Failed to trigger evaluation run");
  return res.json();
}
