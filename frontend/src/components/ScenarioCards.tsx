import React from 'react';
import { ChevronRight, Sparkles } from 'lucide-react';
import { Scenario } from '../types';

interface ScenarioCardsProps {
  scenarios: Scenario[];
  onSelectScenario: (scenario: Scenario) => void;
  isLoading: boolean;
}

export const ScenarioCards: React.FC<ScenarioCardsProps> = ({
  scenarios,
  onSelectScenario,
  isLoading,
}) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center">
          <Sparkles className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
          Suggested Executive Scenarios (Cross-Source)
        </h3>
        <span className="text-xs text-slate-500">Click to run multi-agent analysis</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {scenarios.map((sc) => (
          <button
            key={sc.id}
            disabled={isLoading}
            onClick={() => onSelectScenario(sc)}
            className="text-left p-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-emerald-500/50 transition-all duration-200 group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
                  {sc.badge}
                </span>
                <span className="text-[11px] text-slate-500">{sc.difficulty}</span>
              </div>
              <h4 className="text-sm font-medium text-slate-200 group-hover:text-emerald-300 transition-colors">
                {sc.title}
              </h4>
              <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                {sc.question}
              </p>
            </div>
            <div className="flex items-center text-xs text-emerald-400 font-medium mt-3 pt-2 border-t border-slate-800/60 group-hover:translate-x-0.5 transition-transform">
              <span>Execute Scenario</span>
              <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
