import React from 'react';
import { X, AlertTriangle, Scale, Clock } from 'lucide-react';
import { Conflict } from '../types';

interface ConflictModalProps {
  conflicts: Conflict[];
  isOpen: boolean;
  onClose: () => void;
}

export const ConflictModal: React.FC<ConflictModalProps> = ({ conflicts, isOpen, onClose }) => {
  if (!isOpen || conflicts.length === 0) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-amber-500/30 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Cross-Source Conflict Detected</h3>
              <p className="text-xs text-slate-400">
                Governed discrepancy handling — presenting contradictory enterprise records
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {conflicts.map((conflict) => (
          <div key={conflict.conflict_id} className="space-y-4">
            <div className="flex items-center space-x-2 text-xs font-semibold text-amber-300">
              <Scale className="w-4 h-4" />
              <span>{conflict.topic}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Record A */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Source A (Operational Database)
                </span>
                <p className="text-xs text-slate-200 leading-relaxed font-mono">
                  {conflict.statement_a}
                </p>
              </div>

              {/* Record B */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Source B (Engineering Teardown Memo)
                </span>
                <p className="text-xs text-slate-200 leading-relaxed font-mono">
                  {conflict.statement_b}
                </p>
              </div>
            </div>

            {/* Analysis & Chronology */}
            <div className="p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs text-amber-200/90 flex items-start space-x-2.5">
              <Clock className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-amber-300">Chronological Explanation: </span>
                <span>{conflict.discrepancy_reason}</span>
              </div>
            </div>
          </div>
        ))}

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition"
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
};
