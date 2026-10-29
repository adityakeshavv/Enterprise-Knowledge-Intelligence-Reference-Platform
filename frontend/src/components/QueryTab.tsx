import React from "react";
import type { QueryResponse, CitationItem, IndustryDetail } from "../types";
import { AnswerView } from "./AnswerView";
import type { NavTabId } from "./Sidebar";
import {
  Send,
  Sparkles,
  Loader2,
  Cpu,
  ArrowRight,
  Clock,
  ShieldCheck
} from "lucide-react";

interface QueryTabProps {
  queryInput: string;
  onQueryInputChange: (val: string) => void;
  onRunQuery: (q?: string) => void;
  queryResult: QueryResponse | null;
  onOpenCitation: (citation: CitationItem) => void;
  isLoading: boolean;
  activeIndustry: IndustryDetail | null;
  onNavigate: (tab: NavTabId) => void;
}

export const QueryTab: React.FC<QueryTabProps> = ({
  queryInput,
  onQueryInputChange,
  onRunQuery,
  queryResult,
  onOpenCitation,
  isLoading,
  activeIndustry,
  onNavigate,
}) => {
  const scenarios = activeIndustry?.scenarios || [];

  return (
    <div className="tab-page query-tab">
      {/* Top Query Input Section */}
      <section className="query-input-section">
        <div className="query-box-header">
          <div className="query-box-title">
            <Sparkles size={18} className="text-accent" />
            <h3>Ask Enterprise Intelligence</h3>
          </div>
          <span className="query-box-subtitle">
            Ask a question, then inspect the returned answer, sources, and trace.
          </span>
        </div>

        <form className="query-box" onSubmit={(event) => { event.preventDefault(); if (!isLoading) onRunQuery(); }}>
          <label className="sr-only" htmlFor="enterprise-query">Your question</label>
          <input
            id="enterprise-query"
            type="text"
            className="query-input"
            value={queryInput}
            onChange={(e) => onQueryInputChange(e.target.value)}
            placeholder="E.g. What are the major factors contributing to downtime at Plant A, and what actions reduced it?"
            disabled={isLoading}
          />
          <button
            className="btn-submit"
            type="submit"
            disabled={isLoading || !queryInput.trim()}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                <span>Investigating...</span>
              </>
            ) : (
              <>
                <Send size={16} />
                <span>Ask Intelligence</span>
              </>
            )}
          </button>
        </form>

        {/* Suggestion Chips */}
        {scenarios.length > 0 && (
          <div className="query-suggestion-chips">
            <span className="chips-label">Suggested Inquiries:</span>
            <div className="chips-list">
              {scenarios.slice(0, 3).map((sc) => (
                <button
                  key={sc.id}
                  className="chip-btn"
                  onClick={() => {
                    onQueryInputChange(sc.question);
                    onRunQuery(sc.question);
                  }}
                  disabled={isLoading}
                  title={sc.question}
                >
                  <Sparkles size={12} className="chip-icon" />
                  <span>{sc.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Query Results / Empty State */}
      {queryResult ? (
        <section className="query-results-container">
          {/* Quick jump banner to Agent Trace */}
          <div className="trace-jump-banner">
            <div className="trace-jump-info">
              <Cpu size={18} className="text-accent" />
              <div>
                <strong>Multi-Agent Investigation Completed in {(queryResult.total_latency_ms / 1000).toFixed(2)}s</strong>
                <p>{queryResult.trace_steps.length} execution steps · {queryResult.citations.length} cited sources</p>
              </div>
            </div>
            <button
              className="btn-jump-trace"
              onClick={() => onNavigate("trace")}
            >
              <span>Inspect Agent Trace & Graph</span>
              <ArrowRight size={15} />
            </button>
          </div>

          {/* Answer View */}
          <AnswerView
            data={queryResult}
            onOpenCitation={onOpenCitation}
          />
        </section>
      ) : (
        <section className="query-empty-state">
          <div className="empty-state-card">
            <div className="empty-state-icon">
              <Sparkles size={32} />
            </div>
            <h3>Ready for Enterprise Investigation</h3>
            <p>
              Enter an operational or strategic question, or select one of the suggested inquiries. Review the response and its available sources after it runs.
            </p>
            <div className="empty-state-features">
              <div className="feature-pill">
                <ShieldCheck size={14} className="text-success" />
                <span>Source links</span>
              </div>
              <div className="feature-pill">
                <Clock size={14} className="text-accent" />
                <span>Execution trace</span>
              </div>
              <div className="feature-pill">
                <Cpu size={14} className="text-warning" />
                <span>Traceable Agent State</span>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
