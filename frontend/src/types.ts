export interface IndustrySummary {
  id: string;
  name: string;
  description: string;
  version: string;
  scenario_count: number;
  is_active: boolean;
}

export interface ScenarioItem {
  id: string;
  title: string;
  category: string;
  difficulty: string;
  question: string;
  description?: string;
  expected_agents?: string[];
  highlight_metrics?: string[];
}

export interface IndustryDetail {
  id: string;
  metadata: {
    id: string;
    name: string;
    description: string;
    version: string;
    active: boolean;
    primary_entities?: string[];
  };
  terminology: Record<string, { full_name: string; definition: string }>;
  sources: Record<string, any>;
  scenarios: ScenarioItem[];
  prompts: Record<string, string>;
}

export interface MetricItem {
  label: string;
  value: string;
  subtext?: string;
  change_type?: "positive" | "negative" | "neutral";
}

export interface CitationItem {
  citation_id: string;
  title: string;
  source_type: "SQL_QUERY" | "DOCUMENT_SOP" | "EXTERNAL_API";
  reference: string;
  snippet: string;
  metadata?: Record<string, any>;
}

export interface ConflictItem {
  conflict_id: string;
  title: string;
  description: string;
  source_a: string;
  source_b: string;
  recommendation: string;
}

export interface TraceStep {
  step_id: number;
  agent_name: string;
  agent_label: string;
  status: "running" | "completed" | "warning";
  business_message: string;
  technical_detail?: string;
  duration_ms: number;
}

export interface QueryResponse {
  query_id: string;
  industry_id: string;
  query_text: string;
  executive_summary: string;
  key_findings: string[];
  metrics: MetricItem[];
  citations: CitationItem[];
  conflicts: ConflictItem[];
  confidence_score: number;
  trace_steps: TraceStep[];
  total_latency_ms: number;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: "CXO" | "Admin" | "Operator";
  is_active: boolean;
}
