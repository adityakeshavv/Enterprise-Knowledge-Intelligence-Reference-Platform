import React, { useState } from "react";
import type { QueryResponse, CitationItem } from "../types";
import { AgentTrace } from "./AgentTrace";
import { EvidenceGraphView } from "./EvidenceGraph";
import type { NavTabId } from "./Sidebar";
import {
  Cpu,
  Clock,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  ListTree,
  Network
} from "lucide-react";

interface TraceTabProps {
  queryResult: QueryResponse | null;
  onOpenCitation: (citation: CitationItem) => void;
  onNavigate: (tab: NavTabId) => void;
  onRunDefaultScenario: () => void;
}

export const TraceTab: React.FC<TraceTabProps> = ({
  queryResult,
  onOpenCitation,
  onNavigate,
  onRunDefaultScenario,
}) => {
  const [viewMode, setViewMode] = useState<"BOTH" | "STEPS" | "GRAPH">("BOTH");

  if (!queryResult) {
    return (
      <div className="tab-page trace-tab">
        <section className="trace-empty-container">
          <div className="empty-state-card">
            <div className="empty-state-icon accent-purple">
              <Cpu size={36} />
            </div>
            <h3>Your investigation trace</h3>
            <p>
              No investigation has been run in this session. Submit a question to see the execution steps and evidence links returned for that response.
            </p>

            <div className="empty-actions">
              <button className="btn-primary-action" onClick={onRunDefaultScenario}>
                <Sparkles size={16} />
                <span>Start with a suggested question</span>
              </button>
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="tab-page trace-tab">
      {/* Trace Header / Control Bar */}
      <section className="trace-dashboard-header">
        <div className="trace-dashboard-title">
          <div className="icon-badge accent-purple">
            <Cpu size={20} />
          </div>
          <div>
            <h3>Multi-Agent Investigation Trace & Relational Graph</h3>
            <span className="trace-subtitle">
              Query: {queryResult.query_text}
            </span>
          </div>
        </div>

        <div className="trace-dashboard-meta">
          <div className="trace-meta-stat">
            <Clock size={15} className="text-muted" />
            <span>Total Latency: <strong>{(queryResult.total_latency_ms / 1000).toFixed(2)}s</strong></span>
          </div>
          <div className="trace-meta-stat">
            <ShieldCheck size={15} className="text-success" />
            <span>{queryResult.validation_report?.grounding_score !== undefined ? "Grounding score" : "Confidence"}: <strong>{((queryResult.validation_report?.grounding_score ?? queryResult.confidence_score) * 100).toFixed(0)}%</strong></span>
          </div>
          <div className="trace-view-toggle">
            <button
              className="toggle-btn"
              onClick={() => onNavigate("query")}
              aria-label="Return to Ask Intelligence"
              title="Return to Ask Intelligence"
            >
              <span>Back to Briefing</span>
              <ArrowRight size={13} />
            </button>
            <button
              className={`toggle-btn ${viewMode === "BOTH" ? "active" : ""}`}
              onClick={() => setViewMode("BOTH")}
              aria-pressed={viewMode === "BOTH"}
              title="Show Both Trace and Graph"
            >
              Both Views
            </button>
            <button
              className={`toggle-btn ${viewMode === "STEPS" ? "active" : ""}`}
              onClick={() => setViewMode("STEPS")}
              aria-pressed={viewMode === "STEPS"}
              title="Step-by-step trace only"
            >
              <ListTree size={14} />
              <span>Agent Steps</span>
            </button>
            <button
              className={`toggle-btn ${viewMode === "GRAPH" ? "active" : ""}`}
              onClick={() => setViewMode("GRAPH")}
              aria-pressed={viewMode === "GRAPH"}
              title="Interactive Evidence Graph only"
            >
              <Network size={14} />
              <span>Evidence Graph</span>
            </button>
          </div>
        </div>
      </section>

      {/* Trace Views */}
      <div className="trace-views-container">
        {(viewMode === "BOTH" || viewMode === "STEPS") && (
          <div className="trace-steps-panel">
            <div className="panel-title-bar">
              <ListTree size={16} className="text-accent" />
              <h4>Sequential Agent Execution Steps ({queryResult.trace_steps.length})</h4>
            </div>
            <AgentTrace
              steps={queryResult.trace_steps}
              totalLatencyMs={queryResult.total_latency_ms}
            />
          </div>
        )}

        {(viewMode === "BOTH" || viewMode === "GRAPH") && (
          <div className="trace-graph-panel">
            <div className="panel-title-bar">
              <Network size={16} className="text-accent" />
              <h4>Relational Evidence Graph (DAG)</h4>
            </div>
            <EvidenceGraphView
              graph={queryResult.evidence_graph}
              citations={queryResult.citations}
              onOpenCitation={onOpenCitation}
            />
          </div>
        )}
      </div>
    </div>
  );
};
