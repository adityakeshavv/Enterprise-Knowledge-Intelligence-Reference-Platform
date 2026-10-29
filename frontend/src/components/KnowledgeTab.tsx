import React, { useEffect, useState } from "react";
import type { IndustryDetail } from "../types";
import {
  Database,
  FileText,
  FileSpreadsheet,
  Sparkles,
  Search,
  ChevronDown,
  ChevronUp
} from "lucide-react";

interface KnowledgeTabProps {
  activeIndustry: IndustryDetail | null;
}

interface IngestedDoc {
  id: string;
  filename: string;
  format: "PDF" | "CSV" | "DOCX" | "SQL";
  ingestionEngine: "Docling" | "PyMuPDF4LLM" | "Pandas/SQL";
  pagesOrRows: string;
  chunks: number;
  latencyMs: number;
  status: "INDEXED" | "ACTIVE";
  description: string;
  sampleExcerpt?: string;
}

export const KnowledgeTab: React.FC<KnowledgeTabProps> = ({ activeIndustry }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedDocId, setExpandedDocId] = useState<string | null>(null);

  useEffect(() => {
    setExpandedDocId(null);
    setSearchTerm("");
  }, [activeIndustry?.id]);

  const isPharma = activeIndustry?.id === "pharma";

  // Static examples for the current demo UI; this screen has no inventory API yet.
  const sampleDocs: IngestedDoc[] = isPharma ? [
    {
      id: "doc-protocol",
      filename: "Clinical_Trial_Protocol_CardioVastin_PH3.pdf",
      format: "PDF",
      ingestionEngine: "Docling",
      pagesOrRows: "2 Pages",
      chunks: 3,
      latencyMs: 84.2,
      status: "INDEXED",
      description: "Randomized, double-blind Phase 3 study (CV-301) evaluating LDL-C reduction across 1,200 participants.",
      sampleExcerpt: `# [Document: Clinical_Trial_Protocol_CardioVastin_PH3.pdf | Section: 3.0 Primary Efficacy Endpoint | Page: 2]
CardioVastin achieved a statistically significant 48.4% mean reduction in LDL-C at Week 24 (p < 0.001 versus placebo). Placebo demonstrated a 1.2% reduction. The primary efficacy endpoint was formally met across all pre-specified patient subgroups.`
    },
    {
      id: "doc-fda",
      filename: "FDA_Regulatory_Approval_Summary_CardioVastin.pdf",
      format: "PDF",
      ingestionEngine: "Docling",
      pagesOrRows: "1 Page",
      chunks: 2,
      latencyMs: 62.0,
      status: "INDEXED",
      description: "FDA CDER approval dossier under NDA 218492 for adult primary hyperlipidemia.",
      sampleExcerpt: `# [Document: FDA_Regulatory_Approval_Summary_CardioVastin.pdf | Section: 1. Executive Action | Page: 1]
The FDA has granted formal marketing approval for CardioVastin (20 mg oral film-coated tablets) as an adjunct to diet alone or in combination with statins. No Boxed Warning was required.`
    },
    {
      id: "doc-pv-sop",
      filename: "SOP-PV-042_Adverse_Event_Reporting_Triage.pdf",
      format: "PDF",
      ingestionEngine: "Docling",
      pagesOrRows: "1 Page",
      chunks: 2,
      latencyMs: 58.5,
      status: "INDEXED",
      description: "Global pharmacovigilance procedure enforcing FDA 21 CFR 314.80 15-day alert requirements for serious adverse events.",
      sampleExcerpt: `# [Document: SOP-PV-042_Adverse_Event_Reporting_Triage.pdf | Section: 2.0 Expedited Reporting | Page: 1]
Serious, Unexpected Adverse Events (SUSARs) causing inpatient hospitalization must be submitted to the FDA within 15 calendar days. Latency exceeding 15 days constitutes a critical compliance violation.`
    },
    {
      id: "doc-gmp-sop",
      filename: "Quality_Batch_Release_SOP_Cleanroom_GMP.pdf",
      format: "PDF",
      ingestionEngine: "Docling",
      pagesOrRows: "1 Page",
      chunks: 2,
      latencyMs: 55.0,
      status: "INDEXED",
      description: "Finished product commercial lot release specifications under 21 CFR Part 211 (Purity >= 98.5%, Dissolution >= 85%).",
      sampleExcerpt: `# [Document: Quality_Batch_Release_SOP_Cleanroom_GMP.pdf | Section: 2.0 Lot 4891 Release Investigation | Page: 1]
Lot 4891 achieved 99.2% purity, an average 88.5% dissolution at 30 minutes, and a microbial count of 12 CFU/g. All parameters fully conform to release specifications.`
    },
    {
      id: "doc-pharma-testing",
      filename: "Pharma_Batch_Analytical_Testing_Q1.xlsx",
      format: "CSV",
      ingestionEngine: "Pandas/SQL",
      pagesOrRows: "2 Sheets / 9 Rows",
      chunks: 2,
      latencyMs: 41.0,
      status: "INDEXED",
      description: "Analytical release chemistry testing (HPLC assay, dissolution rate, bioburden CFU) and clinical safety log.",
      sampleExcerpt: `Batch_ID,Drug_Name,Manufacturing_Date,Lot_Size_Kg,Purity_HPLC_Pct,Dissolution_30min_Pct,Quality_Decision
LOT-4890-CV,CardioVastin 20mg,2026-01-10,250.0,99.4,91.2,RELEASED
LOT-4891-CV,CardioVastin 20mg,2026-02-14,250.0,99.2,88.5,RELEASED
LOT-4892-CV,CardioVastin 20mg,2026-03-01,250.0,97.8,79.4,QUARANTINED_REJECTED`
    }
  ] : [
    {
      id: "doc-prd",
      filename: "Nebula9_Enterprise_Knowledge_Intelligence_PRD_Updated.pdf",
      format: "PDF",
      ingestionEngine: "Docling",
      pagesOrRows: "34 Pages",
      chunks: 35,
      latencyMs: 250.5,
      status: "INDEXED",
      description: "Full production architecture, 9-stage multi-agent pipeline specs, and traceability contracts.",
      sampleExcerpt: `# [Document: Nebula9_Enterprise_Knowledge_Intelligence_PRD_Updated.pdf | Section: 1. Executive Summary | Page: 1]

# Nebula9 Enterprise Knowledge Intelligence Platform
## Product Requirements Document (PRD) — Production Release v2.4

### 1. Executive Summary
The Nebula9 Enterprise Knowledge Intelligence Platform is designed to unify enterprise 
structured and unstructured repositories into a traceable, multi-agent AI knowledge interface...`
    },
    {
      id: "doc-tracker",
      filename: "Nebula9_Manufacturing_Knowledge_Intelligence_Weekly_Tracker.pdf",
      format: "PDF",
      ingestionEngine: "PyMuPDF4LLM",
      pagesOrRows: "10 Pages",
      chunks: 12,
      latencyMs: 1420.0,
      status: "INDEXED",
      description: "10-week delivery schedule, milestone definitions, hours allocated, and enterprise controls.",
      sampleExcerpt: `# [Document: Nebula9_Weekly_Tracker.pdf | Section: Week 7 Enterprise Controls | Page: 1]
Week 7: Enterprise Controls — Add the controls required for a credible enterprise demo: RBAC, server-side authorization, source/workspace access boundaries, audit logging, observability, prompt-injection tests.`
    },
    {
      id: "doc-downtime",
      filename: "Plant_A_Production_Downtime_Logs.csv",
      format: "CSV",
      ingestionEngine: "Pandas/SQL",
      pagesOrRows: "2,480 Rows",
      chunks: 1,
      latencyMs: 45.2,
      status: "INDEXED",
      description: "Hourly timestamped manufacturing downtime logs, machine IDs, fault codes, and duration in minutes.",
      sampleExcerpt: `plant_id,line_id,timestamp,downtime_minutes,category,root_cause,technician_id
PLANT_A,LINE_2,2026-03-14T08:15:00,145,HYDRAULIC_SEAL_FAILURE,O-ring wear,TECH_48
PLANT_A,LINE_1,2026-03-15T11:30:00,42,SENSOR_MISALIGNMENT,Optic calibration,TECH_12`
    },
    {
      id: "doc-sop",
      filename: "Hydraulic_Seal_Maintenance_SOP_v4.2.docx",
      format: "DOCX",
      ingestionEngine: "Docling",
      pagesOrRows: "14 Pages",
      chunks: 16,
      latencyMs: 180.0,
      status: "INDEXED",
      description: "Standard operating procedure for Line 2 hydraulic press preventative inspection and seal replacements.",
      sampleExcerpt: `# [Document: Hydraulic_Seal_SOP_v4.2.docx | Section: 4.1 Preventative Maintenance | Page: 6]
Technicians must inspect hydraulic seals at 250 operating hour intervals. Lubrication failure during cycle start accounts for premature wear.`
    }
  ];

  const filteredDocs = sampleDocs.filter(d =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="tab-page knowledge-tab">
      {/* Knowledge Base Header */}
      <section className="knowledge-header-card">
        <div className="knowledge-header-main">
          <div className="icon-badge accent-blue">
            <Database size={22} />
          </div>
          <div>
            <h3>Knowledge sources</h3>
            <p>Browse representative documents and data sources for the selected industry. Inventory, indexing status, and parse metrics are illustrative demo content.</p>
          </div>
        </div>

        <div className="knowledge-stat-pills">
          <div className="k-stat-pill">
            <span className="k-stat-num">{sampleDocs.length}</span>
            <span className="k-stat-lbl">Example sources</span>
          </div>
          <div className="k-stat-pill">
            <span className="k-stat-num">Qdrant</span>
            <span className="k-stat-lbl">Example vector engine</span>
          </div>
          <div className="k-stat-pill">
            <span className="k-stat-num">SQLite</span>
            <span className="k-stat-lbl">Example data store</span>
          </div>
        </div>
      </section>

      {/* Filter and Search Bar */}
      <section className="knowledge-controls-row">
        <span className="demo-only-pill">DEMO CATALOG</span>
        <div className="knowledge-search-wrap">
          <Search size={16} className="text-muted" />
          <input
            aria-label="Search example knowledge sources"
            type="text"
            placeholder="Search documents, tables, or SOP manuals..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <span className="text-muted text-xs">
          Showing {filteredDocs.length} of {sampleDocs.length} repositories for {activeIndustry?.metadata.name || "Enterprise"}
        </span>
      </section>

      {/* Documents Table */}
      <section className="knowledge-documents-section">
        <div className="knowledge-table-card" tabIndex={0} role="region" aria-label="Scrollable example source catalog">
          <table className="knowledge-table">
            <thead>
              <tr>
                <th>Source Document</th>
                <th>Format</th>
                <th>Engine</th>
                <th>Size / Scale</th>
                <th>Chunks</th>
                <th>Parse Time</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocs.map((doc) => {
                const isExpanded = expandedDocId === doc.id;
                return (
                  <React.Fragment key={doc.id}>
                    <tr className={isExpanded ? "row-expanded" : ""}>
                      <td className="doc-name-cell">
                        <div className="doc-icon-wrap">
                          {doc.format === "CSV" || doc.format === "SQL" ? (
                            <FileSpreadsheet size={16} className="text-success" />
                          ) : (
                            <FileText size={16} className="text-accent" />
                          )}
                        </div>
                        <div>
                          <strong>{doc.filename}</strong>
                          <p className="doc-desc">{doc.description}</p>
                        </div>
                      </td>
                      <td>
                        <span className="format-badge">{doc.format}</span>
                      </td>
                      <td>
                        <span className="engine-badge">{doc.ingestionEngine}</span>
                      </td>
                      <td>{doc.pagesOrRows}</td>
                      <td>{doc.chunks}</td>
                      <td>{doc.latencyMs.toFixed(1)} ms</td>
                      <td>
                        <span className="demo-only-pill">EXAMPLE</span>
                      </td>
                      <td>
                        <button
                          className="btn-inspect-doc"
                          onClick={() => setExpandedDocId(isExpanded ? null : doc.id)}
                          aria-expanded={isExpanded}
                          aria-label={`${isExpanded ? "Hide" : "Show"} example excerpt for ${doc.filename}`}
                        >
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          <span>{isExpanded ? "Hide Excerpt" : "Preview"}</span>
                        </button>
                      </td>
                    </tr>
                    {isExpanded && doc.sampleExcerpt && (
                      <tr className="excerpt-row">
                        <td colSpan={8}>
                          <div className="doc-excerpt-container">
                            <div className="excerpt-header">
                              <Sparkles size={14} className="text-accent" />
                              <span>Illustrative excerpt ({doc.ingestionEngine})</span>
                            </div>
                            <pre className="excerpt-code">{doc.sampleExcerpt}</pre>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
              {filteredDocs.length === 0 && (
                <tr><td colSpan={8}><div className="knowledge-empty-state">No example sources match “{searchTerm}”. Try another search.</div></td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
