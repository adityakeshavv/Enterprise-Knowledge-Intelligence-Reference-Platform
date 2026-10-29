import React, { useState } from "react";
import type { QueryResponse, CitationItem } from "../types";
import { EvidenceGraphView } from "./EvidenceGraph";
import {
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  Database,
  FileText,
  CheckCircle2,
  TrendingDown,
  TrendingUp,
  Minus,
  Copy,
  Check,
  Download,
  GitFork,
  FileSpreadsheet,
  Columns
} from "lucide-react";

interface AnswerViewProps {
  data: QueryResponse;
  onOpenCitation: (citation: CitationItem) => void;
}

export const AnswerView: React.FC<AnswerViewProps> = ({ data, onOpenCitation }) => {
  const [activeTab, setActiveTab] = useState<"BRIEFING" | "GRAPH" | "SPLIT">("BRIEFING");
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

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

  // Copy briefing to clipboard
  const handleCopyBriefing = async () => {
    const findingsText = (data.findings || [])
      .map((f) => `- [${f.classification}] ${f.statement}`)
      .join("\n");

    const citationsText = data.citations
      .map((c) => `- [${c.citation_id}] ${c.reference} (${c.title})`)
      .join("\n");

    const textToCopy = `
# Executive Briefing: ${data.query_text}

## Executive Summary
${data.executive_summary}

## Key Operational Findings
${findingsText || data.key_findings.map((f) => `- ${f}`).join("\n")}

## Citations
${citationsText}
    `.trim();

    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopyError(false);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2200);
    } catch {
      setCopied(false);
      setCopyError(true);
    }
  };

  // Export report as downloadable markdown file
  const handleExportReport = () => {
    const findingsText = (data.findings || [])
      .map((f) => `- [${f.classification}] ${f.statement}`)
      .join("\n");

    const citationsText = data.citations
      .map((c) => `- [${c.citation_id}] ${c.reference} (${c.title}):\n  > ${c.snippet}`)
      .join("\n\n");

    const content = `# Nebula9 Executive Decision Briefing
Query ID: ${data.query_id}
Industry: ${data.industry_id}
Grounding / confidence: ${((data.validation_report?.grounding_score ?? data.confidence_score) * 100).toFixed(0)}%
Total Latency: ${data.total_latency_ms} ms

## Query
${data.query_text}

---

## Executive Summary
${data.executive_summary}

---

## Key Operational Findings
${findingsText || data.key_findings.map((f) => `- ${f}`).join("\n")}

---

## Cited Sources
${citationsText}
    `.trim();

    const blob = new Blob([content], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Nebula9_Briefing_${data.query_id}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const groundingScore = data.validation_report?.grounding_score;

  const renderBriefingContent = () => (
    <div className="briefing-content-flow">
      {/* Safe Abstention Banner */}
      {data.is_abstained && (
        <div className="abstention-banner">
          <div className="abstention-icon-col">
            <ShieldAlert className="text-danger" size={24} />
          </div>
          <div className="abstention-content">
            <span className="abstention-tag">Response withheld</span>
            <h4 className="abstention-title">Knowledge Boundary Enforced</h4>
            <p className="abstention-desc">
              {data.validation_report?.abstention_reason ||
                "This query references facilities or operational domains outside the indexed enterprise knowledge base. In compliance with strict enterprise verification policies, the platform refrains from ungrounded extrapolation."}
            </p>
          </div>
        </div>
      )}

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

      {/* Discrepancy & Conflict Banners (PRD Section 5.4) */}
      {data.conflicts && data.conflicts.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {data.conflicts.map((conf) => (
            <div key={conf.conflict_id} className="conflict-banner">
              <div className="conflict-icon-col">
                <AlertTriangle className="icon-warning" size={20} />
              </div>
              <div className="conflict-content">
                <div className="conflict-header">
                  <span className="conflict-tag">Enterprise Conflict Detected</span>
                  <h4 className="conflict-title">{conf.title}</h4>
                </div>
                <p className="conflict-desc">{conf.description}</p>
                <div className="conflict-sources">
                  <div className="source-box">
                    <span className="source-tag">Source 1:</span> {conf.source_a}
                  </div>
                  <div className="source-box">
                    <span className="source-tag">Source 2:</span> {conf.source_b}
                  </div>
                </div>
                <div className="conflict-rec">
                  <strong>Recommendation:</strong> {conf.recommendation}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Executive Summary */}
      <div className="executive-summary-card">
        <div className="summary-header">
          <ShieldCheck size={18} className="text-accent" />
          <h3 className="section-title">Executive Summary</h3>
          <span className="grounding-badge">
            {groundingScore !== undefined
              ? `Grounding score: ${(groundingScore * 100).toFixed(0)}%`
              : `Confidence: ${(data.confidence_score * 100).toFixed(0)}%`}
          </span>
        </div>
        <div className="summary-text">
          {renderTextWithCitations(data.executive_summary)}
        </div>
      </div>

      {/* Key Findings with Fact vs Inference Tagging */}
      <div className="findings-card">
        <h3 className="section-title">Key Operational Findings</h3>
        <ul className="findings-list">
          {data.findings && data.findings.length > 0
            ? data.findings.map((item, idx) => (
                <li key={idx} className="finding-item">
                  <CheckCircle2 size={16} className="finding-bullet" />
                  <div className="finding-content">
                    <span className="finding-statement">
                      {renderTextWithCitations(item.statement)}
                    </span>
                    {item.citation_ids?.some((id) => !item.statement.includes(`[${id}]`)) && (
                      <div className="finding-citations" aria-label="Evidence for this finding">
                        {item.citation_ids.filter((id) => !item.statement.includes(`[${id}]`)).map((id) => {
                          const citation = findCitation(id);
                          return citation ? (
                            <button key={id} className="citation-pill" onClick={() => onOpenCitation(citation)}>
                              View evidence: {id}
                            </button>
                          ) : null;
                        })}
                      </div>
                    )}
                    <div className="finding-badge-row">
                      {item.classification === "VERIFIED_FACT" ? (
                        <span className="badge-fact">
                          <ShieldCheck size={11} /> Verified Fact
                        </span>
                      ) : (
                        <span className="badge-inference">
                          <Sparkles size={11} /> Analytical Inference
                        </span>
                      )}
                    </div>
                  </div>
                </li>
              ))
            : data.key_findings.map((finding, idx) => (
                <li key={idx} className="finding-item">
                  <CheckCircle2 size={16} className="finding-bullet" />
                  <div className="finding-content">
                    <span className="finding-statement">
                      {renderTextWithCitations(finding)}
                    </span>
                  </div>
                </li>
              ))}
        </ul>
      </div>

      {/* Citations Footer Shelf */}
      {data.citations && data.citations.length > 0 && (
        <div className="citations-shelf">
        <span className="shelf-label">Sources referenced in this answer:</span>
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
      )}
      {(!data.citations || data.citations.length === 0) && (
        <div className="answer-source-empty" role="status">No source citations were returned with this response.</div>
      )}
    </div>
  );

  return (
    <div className="answer-view-container">
      {/* Top Experience Navigation Toolbar */}
      <div className="answer-view-toolbar">
        <div className="view-mode-tabs">
          <button
            className={`view-tab-btn ${activeTab === "BRIEFING" ? "active" : ""}`}
            onClick={() => setActiveTab("BRIEFING")}
            aria-pressed={activeTab === "BRIEFING"}
          >
            <FileSpreadsheet size={14} /> Executive Briefing
          </button>
          <span className="sr-only" role="status" aria-live="polite">
            {copyError ? "Could not copy briefing. Check clipboard permissions." : copied ? "Briefing copied to clipboard." : ""}
          </span>
          <button
            className={`view-tab-btn ${activeTab === "GRAPH" ? "active" : ""}`}
            onClick={() => setActiveTab("GRAPH")}
            aria-pressed={activeTab === "GRAPH"}
          >
            <GitFork size={14} /> Evidence Graph
          </button>
          <button
            className={`view-tab-btn ${activeTab === "SPLIT" ? "active" : ""}`}
            onClick={() => setActiveTab("SPLIT")}
            aria-pressed={activeTab === "SPLIT"}
          >
            <Columns size={14} /> Split View
          </button>
        </div>

        <div className="export-action-group">
          <button
            className="btn-action-outline"
            onClick={handleCopyBriefing}
            title="Copy Executive Briefing to Clipboard"
          >
            {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
            <span>{copied ? "Copied!" : "Copy"}</span>
          </button>
          <button
            className="btn-action-outline"
            onClick={handleExportReport}
            title="Download Full Markdown Report"
          >
            <Download size={14} />
            <span>Export (.md)</span>
          </button>
        </div>
      </div>

      {/* Main View Display */}
      {activeTab === "BRIEFING" && renderBriefingContent()}

      {activeTab === "GRAPH" && (
        <EvidenceGraphView
          graph={data.evidence_graph}
          citations={data.citations}
          onOpenCitation={onOpenCitation}
        />
      )}

      {activeTab === "SPLIT" && (
        <div className="split-view-layout">
          <div className="split-left">{renderBriefingContent()}</div>
          <div className="split-right">
            <EvidenceGraphView
              graph={data.evidence_graph}
              citations={data.citations}
              onOpenCitation={onOpenCitation}
            />
          </div>
        </div>
      )}
    </div>
  );
};
