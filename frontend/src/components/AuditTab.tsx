import React, { useState, useEffect } from "react";
import type {
  AuthSession,
  AuditLogItem,
  AuditSummaryMetrics,
  EvaluationSuiteReport,
  EvaluationItemResult
} from "../services/api";
import {
  fetchAuditLogs,
  fetchAuditSummary,
  fetchEvaluationReport,
  triggerEvaluationRun
} from "../services/api";
import type { QueryResponse } from "../types";
import {
  ShieldCheck,
  UserRound,
  Clock,
  Database,
  Search,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Activity,
  BarChart3,
  Play,
  X
} from "lucide-react";

interface AuditTabProps {
  currentUser: AuthSession;
  queryResult: QueryResponse | null;
  activeIndustryId: string;
}

export const AuditTab: React.FC<AuditTabProps> = ({
  currentUser,
  queryResult: _queryResult,
  activeIndustryId: _activeIndustryId
}) => {
  const [activeSubView, setActiveSubView] = useState<"logs" | "benchmark">("logs");

  // Audit Logs State
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [summary, setSummary] = useState<AuditSummaryMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Audit Filters
  const [search, setSearch] = useState<string>("");
  const [industryFilter, setIndustryFilter] = useState<string>("");
  const [roleFilter, setRoleFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  // Detailed inspect modal for Audit Logs
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  // Evaluation & Benchmark State (PRD Section 26)
  const [evalReports, setEvalReports] = useState<Record<string, EvaluationSuiteReport> | null>(null);
  const [evalLoading, setEvalLoading] = useState<boolean>(false);
  const [evalIndustry, setEvalIndustry] = useState<string>("all");
  const [selectedEvalItem, setSelectedEvalItem] = useState<EvaluationItemResult | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [logsRes, summaryRes] = await Promise.all([
        fetchAuditLogs({
          search: search || undefined,
          industry: industryFilter || undefined,
          role: roleFilter || undefined,
          status: statusFilter || undefined,
          page_size: 50
        }),
        fetchAuditSummary()
      ]);
      setLogs(logsRes.logs);
      setSummary(summaryRes);
    } catch (err: any) {
      setError(err?.message || "Failed to load audit events from governance ledger");
    } finally {
      setLoading(false);
    }
  };

  const loadEvaluation = async () => {
    setEvalLoading(true);
    try {
      const data = await fetchEvaluationReport();
      setEvalReports(data);
    } catch (err: any) {
      console.error("Failed to load evaluation report:", err);
    } finally {
      setEvalLoading(false);
    }
  };

  const handleTriggerEval = async () => {
    setEvalLoading(true);
    try {
      const res = await triggerEvaluationRun("all");
      setEvalReports(res.reports);
    } catch (err: any) {
      alert("Failed to run evaluation suite: " + err.message);
    } finally {
      setEvalLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [industryFilter, roleFilter, statusFilter]);

  useEffect(() => {
    if (activeSubView === "benchmark" && !evalReports) {
      loadEvaluation();
    }
  }, [activeSubView]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "SUCCESS":
        return (
          <span className="audit-status-badge status-success">
            <CheckCircle2 size={13} /> SUCCESS
          </span>
        );
      case "ABSTAINED":
        return (
          <span className="audit-status-badge status-abstained">
            <AlertTriangle size={13} /> SAFE ABSTAINED
          </span>
        );
      case "BLOCKED_SECURITY":
        return (
          <span className="audit-status-badge status-blocked">
            <XCircle size={13} /> SECURITY BLOCKED
          </span>
        );
      default:
        return (
          <span className="audit-status-badge status-default">
            <Activity size={13} /> {status}
          </span>
        );
    }
  };

  // Filter benchmark cases
  const displayedEvalItems: EvaluationItemResult[] = [];
  if (evalReports) {
    if (evalIndustry === "all" || evalIndustry === "manufacturing") {
      if (evalReports.manufacturing) {
        displayedEvalItems.push(...evalReports.manufacturing.results);
      }
    }
    if (evalIndustry === "all" || evalIndustry === "pharma") {
      if (evalReports.pharma) {
        displayedEvalItems.push(...evalReports.pharma.results);
      }
    }
  }

  return (
    <div className="tab-page audit-tab">
      {/* 1. Header & Governance Context */}
      <section className="audit-header-card">
        <div className="audit-header-content">
          <div className="icon-badge accent-purple"><ShieldCheck size={24} /></div>
          <div>
            <h3>Enterprise Governance & Quality Evaluation</h3>
            <p>
              Immutable record of queries, source access boundaries, and empirical benchmark evaluations
              proving grounding accuracy, conflict detection, and threat defense (PRD Sections 24 & 26).
            </p>
          </div>
        </div>
        <div className="audit-user-card">
          <UserRound size={18} className="text-accent" />
          <div>
            <span className="audit-user-title">Auditor / Operator Context</span>
            <span className="audit-user-details">
              <strong>{currentUser.full_name}</strong> · <span className="role-tag">{currentUser.role}</span>
            </span>
          </div>
        </div>
      </section>

      {/* Sub-view Navigation Switcher */}
      <div className="eval-subnav-bar">
        <div className="eval-subnav-buttons">
          <button
            type="button"
            className={`btn-subnav ${activeSubView === "logs" ? "active" : ""}`}
            onClick={() => setActiveSubView("logs")}
          >
            <Clock size={16} /> Audit Ledger & Session Telemetry
          </button>
          <button
            type="button"
            className={`btn-subnav ${activeSubView === "benchmark" ? "active" : ""}`}
            onClick={() => setActiveSubView("benchmark")}
          >
            <BarChart3 size={16} /> Gold Benchmark Evaluation (PRD §26)
          </button>
        </div>
      </div>

      {activeSubView === "logs" ? (
        <>
          {/* Executive KPI Overview Cards */}
          {summary && (
            <section className="audit-kpi-grid">
              <div className="kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">TOTAL QUERIES</span>
                  <Activity size={16} className="text-muted" />
                </div>
                <div className="kpi-value">{summary.total_queries}</div>
                <div className="kpi-sub">
                  {summary.successful_queries} verified · {summary.abstained_queries} abstained
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">AVG LATENCY</span>
                  <Clock size={16} className="text-muted" />
                </div>
                <div className="kpi-value">{summary.avg_latency_ms.toFixed(0)} <small>ms</small></div>
                <div className="kpi-sub">Stage-level telemetry logged</div>
              </div>

              <div className="kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">GROUNDING RATE</span>
                  <ShieldCheck size={16} className="text-emerald" />
                </div>
                <div className="kpi-value">{(summary.avg_grounding_score * 100).toFixed(0)}%</div>
                <div className="kpi-sub">Verified entity / fact grounding</div>
              </div>

              <div className="kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">CONFLICTS FLAGGED</span>
                  <AlertTriangle size={16} className="text-amber" />
                </div>
                <div className="kpi-value">{summary.total_conflicts_detected}</div>
                <div className="kpi-sub">Cross-source discrepancies</div>
              </div>

              <div className="kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">THREATS INTERCEPTED</span>
                  <XCircle size={16} className="text-rose" />
                </div>
                <div className="kpi-value">{summary.security_blocked_queries}</div>
                <div className="kpi-sub">Injection & exfiltration blocked</div>
              </div>
            </section>
          )}

          {/* Search & Filter Bar */}
          <section className="audit-filter-bar">
            <form onSubmit={handleSearchSubmit} className="audit-search-box">
              <Search size={16} className="text-muted" />
              <input
                type="text"
                placeholder="Search by query text, audit ID, or user..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </form>

            <div className="audit-dropdown-filters">
              <select value={industryFilter} onChange={(e) => setIndustryFilter(e.target.value)}>
                <option value="">All Industries</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="pharma">Pharmaceutical</option>
              </select>

              <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                <option value="">All Roles</option>
                <option value="CXO">CXO</option>
                <option value="Admin">Admin</option>
                <option value="Auditor">Auditor</option>
                <option value="Quality Analyst">Quality Analyst</option>
                <option value="Operator">Operator</option>
              </select>

              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="">All Statuses</option>
                <option value="SUCCESS">Success</option>
                <option value="ABSTAINED">Abstained</option>
                <option value="BLOCKED_SECURITY">Blocked Security</option>
              </select>

              <button type="button" className="btn-refresh" onClick={loadData} title="Refresh Ledger">
                <RefreshCw size={15} className={loading ? "spin" : ""} />
              </button>
            </div>
          </section>

          {/* Live Audit Ledger Table */}
          <section className="audit-ledger-section">
            <div className="section-header-row">
              <div className="section-header-title">
                <Clock size={18} className="text-accent" />
                <h3>Persistent Audit Ledger</h3>
              </div>
              <span className="status-live-pill">IMMUTABLE LOGS ({logs.length})</span>
            </div>

            {error && (
              <div className="audit-error-banner" role="alert">
                <AlertTriangle size={16} /> {error}
              </div>
            )}

            {loading && logs.length === 0 ? (
              <div className="audit-loading-state">
                <RefreshCw size={24} className="spin text-accent" />
                <p>Retrieving immutable audit records from database...</p>
              </div>
            ) : logs.length === 0 ? (
              <div className="audit-empty-state">
                <ShieldCheck size={28} />
                <p>No audit records match your current filter criteria.</p>
              </div>
            ) : (
              <div className="audit-table-wrap">
                <table className="audit-table">
                  <thead>
                    <tr>
                      <th>Audit ID & Time</th>
                      <th>User & Role</th>
                      <th>Industry</th>
                      <th>Query Preview</th>
                      <th>Status</th>
                      <th>Latency</th>
                      <th>Grounding</th>
                      <th>Sources Cited</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id} onClick={() => setSelectedLog(log)} className="audit-row-clickable">
                        <td>
                          <code className="audit-id-badge">{log.audit_id}</code>
                          <div className="audit-time-sub">
                            {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </div>
                        </td>
                        <td>
                          <strong>{log.username}</strong>
                          <div className="text-muted small">{log.role}</div>
                        </td>
                        <td>
                          <span className="audit-industry-tag">{log.industry_id}</span>
                        </td>
                        <td className="query-preview-col" title={log.query_text}>
                          {log.query_text}
                        </td>
                        <td>{getStatusBadge(log.status)}</td>
                        <td>{log.execution_time_ms.toFixed(0)} ms</td>
                        <td>
                          {log.grounding_score !== null && log.grounding_score !== undefined ? (
                            <span className={`grounding-score-pill ${log.grounding_score >= 0.8 ? "score-high" : log.grounding_score > 0 ? "score-med" : "score-zero"}`}>
                              {(log.grounding_score * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>
                        <td>{log.citations_count} sources</td>
                        <td>
                          <button
                            type="button"
                            className="btn-inspect-trail"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedLog(log);
                            }}
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      ) : (
        /* Benchmark Evaluation View (PRD Section 26) */
        <section className="eval-benchmark-container">
          <div className="eval-benchmark-header-row">
            <div>
              <h3>Gold-Standard Benchmark Suite (30 Curated Cases)</h3>
              <p>Rigorous automated evaluation assessing Grounding, Citations, Conflicts, Safe Abstention, and AI Security.</p>
            </div>
            <div className="eval-actions-group">
              <select value={evalIndustry} onChange={(e) => setEvalIndustry(e.target.value)} className="eval-industry-select">
                <option value="all">All Industries (30 Cases)</option>
                <option value="manufacturing">Manufacturing (15 Cases)</option>
                <option value="pharma">Pharmaceutical (15 Cases)</option>
              </select>
              <button
                type="button"
                className="btn-run-eval"
                onClick={handleTriggerEval}
                disabled={evalLoading}
              >
                {evalLoading ? <RefreshCw size={15} className="spin" /> : <Play size={15} />}
                <span>{evalLoading ? "Executing Suite..." : "Run Benchmark Suite"}</span>
              </button>
            </div>
          </div>

          {/* Benchmark KPI Cards */}
          {evalReports && (
            <div className="eval-summary-cards-row">
              {evalReports.manufacturing && (evalIndustry === "all" || evalIndustry === "manufacturing") && (
                <div className="eval-industry-card">
                  <div className="eval-card-header">
                    <strong>Manufacturing Benchmark</strong>
                    <span className="status-live-pill">{evalReports.manufacturing.overall_pass_rate}% PASS</span>
                  </div>
                  <div className="eval-card-metrics">
                    <div><span>Grounding:</span> <strong>{(evalReports.manufacturing.avg_grounding_score * 100).toFixed(0)}%</strong></div>
                    <div><span>Conflict Acc:</span> <strong>{evalReports.manufacturing.conflict_accuracy}%</strong></div>
                    <div><span>Abstention Acc:</span> <strong>{evalReports.manufacturing.abstention_accuracy}%</strong></div>
                    <div><span>Security Acc:</span> <strong>{evalReports.manufacturing.security_accuracy}%</strong></div>
                    <div><span>Median Latency:</span> <strong>{evalReports.manufacturing.median_latency_ms.toFixed(0)} ms</strong></div>
                  </div>
                </div>
              )}

              {evalReports.pharma && (evalIndustry === "all" || evalIndustry === "pharma") && (
                <div className="eval-industry-card">
                  <div className="eval-card-header">
                    <strong>Pharma & Life Sciences</strong>
                    <span className="status-live-pill">{evalReports.pharma.overall_pass_rate}% PASS</span>
                  </div>
                  <div className="eval-card-metrics">
                    <div><span>Grounding:</span> <strong>{(evalReports.pharma.avg_grounding_score * 100).toFixed(0)}%</strong></div>
                    <div><span>Conflict Acc:</span> <strong>{evalReports.pharma.conflict_accuracy}%</strong></div>
                    <div><span>Abstention Acc:</span> <strong>{evalReports.pharma.abstention_accuracy}%</strong></div>
                    <div><span>Security Acc:</span> <strong>{evalReports.pharma.security_accuracy}%</strong></div>
                    <div><span>Median Latency:</span> <strong>{evalReports.pharma.median_latency_ms.toFixed(0)} ms</strong></div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Benchmark Cases Table */}
          <div className="audit-table-wrap" style={{ marginTop: "1rem" }}>
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Category</th>
                  <th>Test Query</th>
                  <th>Status</th>
                  <th>Grounding</th>
                  <th>Latency</th>
                  <th>Result Validation</th>
                </tr>
              </thead>
              <tbody>
                {displayedEvalItems.map((item) => (
                  <tr key={item.eval_id} className="audit-row-clickable" onClick={() => setSelectedEvalItem(item)}>
                    <td><code>{item.eval_id}</code></td>
                    <td><span className="category-pill">{item.category.replace(/_/g, " ")}</span></td>
                    <td className="query-preview-col" title={item.query}>{item.query}</td>
                    <td>
                      {item.passed ? (
                        <span className="audit-status-badge status-success"><CheckCircle2 size={13} /> PASS</span>
                      ) : (
                        <span className="audit-status-badge status-blocked"><XCircle size={13} /> FAIL</span>
                      )}
                    </td>
                    <td>{(item.grounding_score * 100).toFixed(0)}%</td>
                    <td>{item.latency_ms.toFixed(0)} ms</td>
                    <td>
                      {item.passed ? (
                        <span className="text-emerald" style={{ fontSize: "0.76rem" }}>Fully Grounded</span>
                      ) : (
                        <span className="text-rose" style={{ fontSize: "0.76rem" }}>{item.failure_reasons.join(", ")}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Inspect Modal for Audit Logs */}
      {selectedLog && (
        <div className="audit-modal-backdrop" onClick={() => setSelectedLog(null)}>
          <div className="audit-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="audit-modal-header">
              <div className="audit-modal-title">
                <ShieldCheck size={20} className="text-accent" />
                <h3>Audit Event: <code>{selectedLog.audit_id}</code></h3>
              </div>
              <button
                type="button"
                className="btn-modal-close"
                onClick={() => setSelectedLog(null)}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            <div className="audit-modal-body">
              <div className="modal-field-group">
                <label>User Query</label>
                <p className="modal-query-text">{selectedLog.query_text}</p>
              </div>

              <div className="modal-grid-row">
                <div>
                  <label>Actor / Role</label>
                  <div><strong>{selectedLog.username}</strong> ({selectedLog.role})</div>
                </div>
                <div>
                  <label>Timestamp</label>
                  <div>{new Date(selectedLog.timestamp).toLocaleString()}</div>
                </div>
                <div>
                  <label>Industry Scope</label>
                  <div><code>{selectedLog.industry_id}</code></div>
                </div>
                <div>
                  <label>Execution Status</label>
                  <div>{getStatusBadge(selectedLog.status)}</div>
                </div>
              </div>

              <div className="modal-grid-row">
                <div>
                  <label>Total Duration</label>
                  <div>{selectedLog.execution_time_ms.toFixed(1)} ms</div>
                </div>
                <div>
                  <label>Grounding Score</label>
                  <div>
                    {selectedLog.grounding_score !== null && selectedLog.grounding_score !== undefined
                      ? `${(selectedLog.grounding_score * 100).toFixed(0)}%`
                      : "N/A"}
                  </div>
                </div>
                <div>
                  <label>Operational Conflicts</label>
                  <div>{selectedLog.conflicts_count} detected</div>
                </div>
                <div>
                  <label>Safe Abstention</label>
                  <div>{selectedLog.is_abstained ? "Yes (Zero Hallucination)" : "No"}</div>
                </div>
              </div>

              <div className="modal-field-group">
                <label>Dispatched Multi-Agent Pipeline</label>
                <div className="modal-agents-list">
                  {selectedLog.agents_invoked || "Security Guardrail Inspection"}
                </div>
              </div>

              {selectedLog.sources_accessed && selectedLog.sources_accessed.length > 0 && (
                <div className="modal-field-group">
                  <label>Heterogeneous Sources & Tables Accessed</label>
                  <ul className="modal-sources-list">
                    {selectedLog.sources_accessed.map((src, i) => (
                      <li key={i}>
                        <Database size={13} /> {src}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedLog.trace_stages && (
                <div className="modal-field-group">
                  <label>Telemetry: Stage Latencies (ms)</label>
                  <div className="trace-stages-bar">
                    {Object.entries(selectedLog.trace_stages).map(([stage, dur], i) => (
                      <div key={i} className="stage-pill">
                        <span>{stage.replace(/_/g, " ")}:</span> <strong>{dur} ms</strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="audit-modal-footer">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setSelectedLog(null)}
              >
                Close Audit Record
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Inspect Modal for Benchmark Item */}
      {selectedEvalItem && (
        <div className="audit-modal-backdrop" onClick={() => setSelectedEvalItem(null)}>
          <div className="audit-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="audit-modal-header">
              <div className="audit-modal-title">
                <BarChart3 size={20} className="text-accent" />
                <h3>Benchmark Case: <code>{selectedEvalItem.eval_id}</code></h3>
              </div>
              <button
                type="button"
                className="btn-modal-close"
                onClick={() => setSelectedEvalItem(null)}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            <div className="audit-modal-body">
              <div className="modal-field-group">
                <label>Evaluation Test Query</label>
                <p className="modal-query-text">{selectedEvalItem.query}</p>
              </div>

              <div className="modal-grid-row">
                <div>
                  <label>Category</label>
                  <div><code>{selectedEvalItem.category}</code></div>
                </div>
                <div>
                  <label>Overall Status</label>
                  <div>
                    {selectedEvalItem.passed ? (
                      <span className="audit-status-badge status-success"><CheckCircle2 size={13} /> PASS</span>
                    ) : (
                      <span className="audit-status-badge status-blocked"><XCircle size={13} /> FAIL</span>
                    )}
                  </div>
                </div>
                <div>
                  <label>Grounding Verification</label>
                  <div>{(selectedEvalItem.grounding_score * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <label>Execution Latency</label>
                  <div>{selectedEvalItem.latency_ms.toFixed(1)} ms</div>
                </div>
              </div>

              <div className="modal-field-group">
                <label>Validation Checks</label>
                <ul className="modal-sources-list">
                  <li>
                    {selectedEvalItem.expected_conflict_found ? (
                      <CheckCircle2 size={13} className="text-emerald" />
                    ) : (
                      <XCircle size={13} className="text-rose" />
                    )}
                    <span>Conflict Detection Check: {selectedEvalItem.expected_conflict_found ? "Verified" : "Missed"}</span>
                  </li>
                  <li>
                    {selectedEvalItem.expected_abstention_matched ? (
                      <CheckCircle2 size={13} className="text-emerald" />
                    ) : (
                      <XCircle size={13} className="text-rose" />
                    )}
                    <span>Safe Abstention Behavior: {selectedEvalItem.is_abstained ? "Abstained Safely" : "Answered Grounded"}</span>
                  </li>
                  <li>
                    {selectedEvalItem.expected_security_matched ? (
                      <CheckCircle2 size={13} className="text-emerald" />
                    ) : (
                      <XCircle size={13} className="text-rose" />
                    )}
                    <span>AI Security Guardrails: {selectedEvalItem.is_blocked_security ? "Threat Intercepted" : "Normal Flow"}</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="audit-modal-footer">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setSelectedEvalItem(null)}
              >
                Close Case Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
