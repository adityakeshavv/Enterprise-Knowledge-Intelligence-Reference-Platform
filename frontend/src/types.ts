export interface IndustrySummary {
  id: string;
  name: string;
  tagline: string;
  badge_color: string;
  icon: string;
  version: string;
  kpis: Array<{ id: string; label: string; unit: string; target: number }>;
  scenarios_count: number;
}

export interface Scenario {
  id: string;
  title: string;
  badge: string;
  question: string;
  description: string;
  suggested: boolean;
  difficulty: string;
}

export interface AgentTrace {
  agent: string;
  action: string;
  duration_ms: number;
  status: string;
  details?: Record<string, any>;
}

export interface Citation {
  citation_id: string;
  source_type: 'document' | 'structured_data' | 'external';
  source_name: string;
  page_number?: number;
  section?: string;
  excerpt?: string;
  query_executed?: string;
  record_count?: number;
}

export interface Conflict {
  conflict_id: string;
  topic: string;
  statement_a: string;
  statement_b: string;
  discrepancy_reason: string;
  status: string;
}

export interface MetricsTable {
  headers: string[];
  rows: (string | number)[][];
}

export interface QueryResponse {
  query_id: string;
  industry_id: string;
  execution_time_ms: number;
  executive_summary: string;
  key_findings: string[];
  metrics_table: MetricsTable;
  grounding_confidence: number;
  citations: Citation[];
  conflicts: Conflict[];
  agent_trace: AgentTrace[];
}

export interface UserSession {
  user_id: string;
  username: string;
  display_name: string;
  role: 'Executive' | 'Auditor';
  allowed_workspaces: string[];
}
