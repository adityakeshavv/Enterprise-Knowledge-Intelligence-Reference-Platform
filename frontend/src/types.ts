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

export type FactClassification = "VERIFIED_FACT" | "ANALYTICAL_INFERENCE";

export interface FindingItem {
  statement: string;
  classification: FactClassification;
  citation_ids: string[];
  confidence: number;
}

export interface ValidationReport {
  grounding_score: number;
  supported_claims: string[];
  unsupported_claims: string[];
  conflicts: ConflictItem[];
  is_abstained: boolean;
  abstention_reason?: string;
}

export interface EvidenceGraphNode {
  id: string;
  label: string;
  node_type: "query" | "finding" | "sql_source" | "doc_source" | "conflict";
  category?: string;
  metadata?: Record<string, any>;
}

export interface EvidenceGraphEdge {
  source: string;
  target: string;
  relation: string;
  is_conflict?: boolean;
}

export interface EvidenceGraph {
  nodes: EvidenceGraphNode[];
  edges: EvidenceGraphEdge[];
}

export interface QueryResponse {
  query_id: string;
  industry_id: string;
  query_text: string;
  executive_summary: string;
  key_findings: string[];
  findings?: FindingItem[];
  metrics: MetricItem[];
  citations: CitationItem[];
  conflicts: ConflictItem[];
  confidence_score: number;
  validation_report?: ValidationReport;
  evidence_graph?: EvidenceGraph;
  is_abstained?: boolean;
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
