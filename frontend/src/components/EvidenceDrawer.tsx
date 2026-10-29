import React, { useEffect, useRef } from "react";
import type { CitationItem } from "../types";
import { X, FileText, Database, Info, FileSpreadsheet, ScanLine } from "lucide-react";

interface EvidenceDrawerProps {
  citation: CitationItem | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ citation, onClose }) => {
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    if (!citation) return;
    const previousFocus = document.activeElement as HTMLElement | null;
    panelRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeRef.current();
      if (event.key === "Tab" && panelRef.current) {
        const focusable = panelRef.current.querySelectorAll<HTMLElement>('button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (document.activeElement === panelRef.current) { event.preventDefault(); (event.shiftKey ? last : first).focus(); }
        else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      previousFocus?.focus();
    };
  }, [citation]);
  if (!citation) return null;

  const getSourceIcon = (type: string, ref: string) => {
    if (type === "SQL_QUERY") return <Database size={18} className="text-blue-400" />;
    if (ref.includes(".xlsx") || ref.includes("Sheet:")) return <FileSpreadsheet size={18} className="text-emerald-400" />;
    if (ref.includes("OCR") || ref.includes("Scan") || type === "ocr_scan") return <ScanLine size={18} className="text-purple-400" />;
    return <FileText size={18} className="text-amber-400" />;
  };

  return (
    <div className="drawer-overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <div className="drawer-panel" role="dialog" aria-modal="true" aria-labelledby="evidence-dialog-title" tabIndex={-1} ref={panelRef}>
        <div className="drawer-header">
          <div className="drawer-title-group">
            {getSourceIcon(citation.source_type, citation.reference)}
            <div>
              <span className="source-tag">{citation.source_type.replace("_", " ")}</span>
              <h2 className="drawer-title" id="evidence-dialog-title">{citation.title}</h2>
            </div>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close evidence details">
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
            <span className="section-label">Evidence excerpt</span>
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
            <Info size={14} className="text-accent" />
            <span>Review the source reference and excerpt when assessing this evidence.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
