import React from 'react';
import { X, FileText, Database, ShieldCheck } from 'lucide-react';
import { Citation } from '../types';

interface EvidenceDrawerProps {
  citation: Citation | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl z-50 p-6 flex flex-col justify-between overflow-y-auto">
      <div className="space-y-5">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-sm text-slate-100">Evidence Verification Drawer</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Source Identification
          </span>
          <div className="mt-1 flex items-center space-x-2">
            {citation.source_type === 'document' ? (
              <FileText className="w-4 h-4 text-amber-400" />
            ) : (
              <Database className="w-4 h-4 text-blue-400" />
            )}
            <h4 className="text-sm font-medium text-slate-200">{citation.source_name}</h4>
          </div>
        </div>

        {citation.section && (
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Section Header
            </span>
            <p className="mt-0.5 text-xs text-emerald-400 font-mono">{citation.section}</p>
          </div>
        )}

        {citation.page_number && (
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Document Coordinate
            </span>
            <p className="mt-0.5 text-xs text-slate-300 font-mono">Page {citation.page_number}</p>
          </div>
        )}

        {citation.excerpt && (
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Verified Source Excerpt
            </span>
            <div className="mt-1.5 p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs text-slate-300 leading-relaxed italic border-l-4 border-l-emerald-500">
              "{citation.excerpt}"
            </div>
          </div>
        )}

        {citation.query_executed && (
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Read-Only SQL Query Provenance
            </span>
            <div className="mt-1.5 p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-emerald-400 overflow-x-auto">
              <code>{citation.query_executed}</code>
            </div>
          </div>
        )}
      </div>

      <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
        <span>Verified by EvidenceValidationAgent</span>
        <span className="text-emerald-400">Status: GROUNDED</span>
      </div>
    </div>
  );
};
