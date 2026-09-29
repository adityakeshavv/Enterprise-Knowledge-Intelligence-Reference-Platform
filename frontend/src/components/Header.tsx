import React from 'react';
import { Layers, ShieldCheck, Database, Activity } from 'lucide-react';
import { IndustrySummary, UserSession } from '../types';

interface HeaderProps {
  industries: IndustrySummary[];
  selectedIndustryId: string;
  onSelectIndustry: (id: string) => void;
  currentUser: UserSession;
  onToggleUserRole: () => void;
  onOpenAudit: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  industries,
  selectedIndustryId,
  onSelectIndustry,
  currentUser,
  onToggleUserRole,
  onOpenAudit,
}) => {

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-30 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Platform Identity */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold tracking-tight text-white text-base">Nebula9</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                Reference Platform
              </span>
            </div>
            <p className="text-xs text-slate-400">Enterprise Knowledge Intelligence</p>
          </div>
        </div>

        {/* Center: Zero-Code Industry Selector */}
        <div className="flex items-center space-x-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <div className="flex items-center px-2.5 text-xs text-slate-400">
            <Database className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
            <span className="hidden sm:inline font-medium">Domain:</span>
          </div>
          <div className="flex space-x-1">
            {industries.map((ind) => {
              const active = ind.id === selectedIndustryId;
              return (
                <button
                  key={ind.id}
                  onClick={() => onSelectIndustry(ind.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    active
                      ? 'bg-emerald-500 text-white shadow-sm shadow-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  {ind.name.split('&')[0].trim()}
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Security Role & Governance Console */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenAudit}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 transition"
            title="Inspect System Audit Log"
          >
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            <span className="hidden md:inline font-medium">Audit Telemetry</span>
          </button>

          <button
            onClick={onToggleUserRole}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition"
            title="Switch User / Auditor Role"
          >
            <ShieldCheck
              className={`w-3.5 h-3.5 ${
                currentUser.role === 'Auditor' ? 'text-amber-400' : 'text-emerald-400'
              }`}
            />
            <span className="font-semibold text-slate-200">{currentUser.role}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
