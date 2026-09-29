import React from 'react';
import { ShieldCheck, AlertTriangle, FileText, Database, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { QueryResponse, Citation } from '../types';

interface ExecutiveAnswerProps {
  response: QueryResponse;
  onOpenEvidence: (citation: Citation) => void;
  onOpenConflict: () => void;
}

export const ExecutiveAnswer: React.FC<ExecutiveAnswerProps> = ({
  response,
  onOpenEvidence,
  onOpenConflict,
}) => {
  const hasConflicts = response.conflicts && response.conflicts.length > 0;

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-6 shadow-xl shadow-black/40">
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 text-xs font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Grounding: {Math.round(response.grounding_confidence * 100)}%</span>
          </div>

          <span className="text-xs text-slate-500 font-mono">
            {response.execution_time_ms}ms total execution
          </span>
        </div>

        {/* Conflict Trigger Banner */}
        {hasConflicts && (
          <button
            onClick={onOpenConflict}
            className="flex items-center space-x-2 px-3.5 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/40 hover:bg-amber-500/20 transition text-xs font-semibold animate-pulse"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>{response.conflicts.length} Data Discrepancy Detected (Inspect)</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* 1. Executive Summary */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Executive Summary
        </h3>
        <p className="text-base text-slate-100 leading-relaxed font-normal bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
          {response.executive_summary}
        </p>
      </div>

      {/* 2. Key Operational Findings */}
      <div className="space-y-2.5">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Key Findings & Root Causes
        </h3>
        <ul className="space-y-2">
          {response.key_findings.map((finding, idx) => (
            <li
              key={idx}
              className="flex items-start space-x-3 text-sm text-slate-300 bg-slate-950/30 p-3 rounded-lg border border-slate-800/40"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{finding}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* 3. Quantitative Data Table */}
      {response.metrics_table && response.metrics_table.rows.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center">
              <Database className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
              Operational Metrics (Extracted from Operational Database)
            </h3>
            <span className="text-[11px] text-slate-500">Read-only SQL Provenance Verified</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
                <tr>
                  {response.metrics_table.headers.map((h, i) => (
                    <th key={i} className="py-2.5 px-4 font-semibold">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {response.metrics_table.rows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-900/40 transition">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="py-2.5 px-4 font-mono">
                        {typeof cell === 'number' && !Number.isInteger(cell)
                          ? cell.toFixed(2)
                          : cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4. Evidence & Source Traceability */}
      <div className="space-y-2.5 pt-2 border-t border-slate-800">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center">
          <FileText className="w-3.5 h-3.5 mr-1.5 text-amber-400" />
          Evidence & Source Traceability
        </h3>
        <p className="text-xs text-slate-500">
          Click any citation below to inspect the verified page, section, or database query:
        </p>

        <div className="flex flex-wrap gap-2 pt-1">
          {response.citations.map((c) => (
            <button
              key={c.citation_id}
              onClick={() => onOpenEvidence(c)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/50 text-xs text-slate-300 hover:text-white transition group"
            >
              {c.source_type === 'document' ? (
                <FileText className="w-3.5 h-3.5 text-amber-400" />
              ) : (
                <Database className="w-3.5 h-3.5 text-blue-400" />
              )}
              <span className="font-medium truncate max-w-xs">{c.source_name}</span>
              {c.page_number && (
                <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-emerald-400 font-mono">
                  p.{c.page_number}
                </span>
              )}
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-emerald-400 transition" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
