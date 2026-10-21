import React from "react";
import type { QueryResponse, CitationItem } from "../types";
import { AlertTriangle, ShieldCheck, Database, FileText, CheckCircle2, TrendingDown, TrendingUp, Minus } from "lucide-react";

interface AnswerViewProps {
  data: QueryResponse;
  onOpenCitation: (citation: CitationItem) => void;
}

export const AnswerView: React.FC<AnswerViewProps> = ({ data, onOpenCitation }) => {
  const findCitation = (id: string) => data.citations.find((c) => c.citation_id === id);

  // Helper to render text with clickable citation badges
  const renderTextWithCitations = (text: string) => {
    const parts = text.split(/(\[[A-Za-z0-9_\-\.]+\])/g);
    return parts.map((part, index) => {
      if (part.startsWith("[") && part.endsWith("]")) {
        const citationId = part.slice(1, -1);
        const citation = findCitation(citationId);
        if (citation) {
          return (
            <button
              key={index}
              className="citation-pill"
              onClick={() => onOpenCitation(citation)}
              title={`Inspect proof: ${citation.title}`}
            >
              {part}
            </button>
          );
        }
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="answer-view-container">
      {/* Metrics Row */}
      {data.metrics && data.metrics.length > 0 && (
        <div className="metrics-grid">
          {data.metrics.map((m, idx) => (
            <div key={idx} className="metric-card">
              <span className="metric-label">{m.label}</span>
              <div className="metric-value-row">
                <span className="metric-value">{m.value}</span>
                {m.change_type === "negative" && <TrendingDown size={16} className="text-danger" />}
                {m.change_type === "positive" && <TrendingUp size={16} className="text-success" />}
                {m.change_type === "neutral" && <Minus size={16} className="text-muted" />}
              </div>
              {m.subtext && <span className="metric-subtext">{m.subtext}</span>}
            </div>
          ))}
        </div>
      )}

      {/* Discrepancy & Conflict Banner (PRD Section 5.4) */}
      {data.conflicts && data.conflicts.length > 0 && (
        <div className="conflict-banner">
          <div className="conflict-icon-col">
            <AlertTriangle className="icon-warning" size={20} />
          </div>
          <div className="conflict-content">
            <div className="conflict-header">
              <span className="conflict-tag">Enterprise Conflict Detected</span>
              <h4 className="conflict-title">{data.conflicts[0].title}</h4>
            </div>
            <p className="conflict-desc">{data.conflicts[0].description}</p>
            <div className="conflict-sources">
              <div className="source-box">
                <span className="source-tag">Source 1:</span> {data.conflicts[0].source_a}
              </div>
              <div className="source-box">
                <span className="source-tag">Source 2:</span> {data.conflicts[0].source_b}
              </div>
            </div>
            <div className="conflict-rec">
              <strong>Recommendation:</strong> {data.conflicts[0].recommendation}
            </div>
          </div>
        </div>
      )}

      {/* Executive Summary */}
      <div className="executive-summary-card">
        <div className="summary-header">
          <ShieldCheck size={18} className="text-accent" />
          <h3 className="section-title">Executive Summary</h3>
          <span className="grounding-badge">
            Grounding Confidence: {(data.confidence_score * 100).toFixed(0)}%
          </span>
        </div>
        <div className="summary-text">
          {renderTextWithCitations(data.executive_summary)}
        </div>
      </div>

      {/* Key Findings */}
      <div className="findings-card">
        <h3 className="section-title">Key Operational Findings</h3>
        <ul className="findings-list">
          {data.key_findings.map((finding, idx) => (
            <li key={idx} className="finding-item">
              <CheckCircle2 size={16} className="finding-bullet" />
              <span>{renderTextWithCitations(finding)}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Citations Footer Shelf */}
      <div className="citations-shelf">
        <span className="shelf-label">Verifiable Knowledge Sources:</span>
        <div className="citation-buttons">
          {data.citations.map((c) => (
            <button
              key={c.citation_id}
              className="shelf-btn"
              onClick={() => onOpenCitation(c)}
            >
              {c.source_type === "SQL_QUERY" ? (
                <Database size={13} className="text-blue-400" />
              ) : (
                <FileText size={13} className="text-amber-400" />
              )}
              <span>{c.citation_id}: {c.reference}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
