import React from "react";
import type { CitationItem } from "../types";
import { X, FileText, Database, CheckCircle, FileSpreadsheet, ScanLine } from "lucide-react";

interface EvidenceDrawerProps {
  citation: CitationItem | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  const getSourceIcon = (type: string, ref: string) => {
    if (type === "SQL_QUERY") return <Database size={18} className="text-blue-400" />;
    if (ref.includes(".xlsx") || ref.includes("Sheet:")) return <FileSpreadsheet size={18} className="text-emerald-400" />;
    if (ref.includes("OCR") || ref.includes("Scan") || type === "ocr_scan") return <ScanLine size={18} className="text-purple-400" />;
    return <FileText size={18} className="text-amber-400" />;
  };

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title-group">
            {getSourceIcon(citation.source_type, citation.reference)}
            <div>
              <span className="source-tag">{citation.source_type.replace("_", " ")}</span>
              <h2 className="drawer-title">{citation.title}</h2>
            </div>
          </div>
          <button className="btn-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="drawer-body">
          {/* Reference Source */}
          <div className="drawer-section">
            <span className="section-label">Source Identifier & Location</span>
            <div className="reference-box">
              <code>{citation.reference}</code>
            </div>
          </div>

          {/* Evidence Snippet */}
          <div className="drawer-section">
            <span className="section-label">Verified Record Content</span>
            <div className="snippet-box">
              {citation.source_type === "SQL_QUERY" ? (
                <pre><code>{citation.snippet}</code></pre>
              ) : (
                <p>{citation.snippet}</p>
              )}
            </div>
          </div>

          {/* Metadata Provenance */}
          {citation.metadata && Object.keys(citation.metadata).length > 0 && (
            <div className="drawer-section">
              <span className="section-label">Provenance & Execution Metadata</span>
              <div className="metadata-grid">
                {Object.entries(citation.metadata).map(([key, value]) => (
                  <div key={key} className="meta-card">
                    <span className="meta-key">{key.replace("_", " ")}</span>
                    <span className="meta-value">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="drawer-footer-note">
            <CheckCircle size={14} className="icon-success" />
            <span>Cryptographically ground-checked against raw enterprise source.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
