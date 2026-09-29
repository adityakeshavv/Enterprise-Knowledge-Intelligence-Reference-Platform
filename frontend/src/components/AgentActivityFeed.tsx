import React from 'react';
import { CheckCircle2, Clock, Bot, Cpu, FileText, Database, ShieldAlert, Sparkles } from 'lucide-react';
import { AgentTrace } from '../types';

interface AgentActivityFeedProps {
  traces: AgentTrace[];
  isLoading: boolean;
}

const getAgentIcon = (agent: string) => {
  if (agent.includes('Router')) return <Cpu className="w-4 h-4 text-purple-400" />;
  if (agent.includes('Structured')) return <Database className="w-4 h-4 text-blue-400" />;
  if (agent.includes('Document')) return <FileText className="w-4 h-4 text-amber-400" />;
  if (agent.includes('Validation')) return <ShieldAlert className="w-4 h-4 text-emerald-400" />;
  if (agent.includes('Synthesis')) return <Sparkles className="w-4 h-4 text-pink-400" />;
  return <Bot className="w-4 h-4 text-slate-400" />;
};

export const AgentActivityFeed: React.FC<AgentActivityFeedProps> = ({ traces, isLoading }) => {
  if (traces.length === 0 && !isLoading) return null;

  return (
    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Multi-Agent Reasoning Activity (Governed Workflow)
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          {traces.length} Specialized Agents Invoked
        </span>
      </div>

      <div className="space-y-2.5">
        {traces.map((trace, idx) => (
          <div
            key={idx}
            className="flex items-start justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 hover:border-slate-700 transition"
          >
            <div className="flex items-start space-x-3">
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 shrink-0 mt-0.5">
                {getAgentIcon(trace.agent)}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-semibold text-slate-200">{trace.agent}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    {trace.duration_ms}ms
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{trace.action}</p>

                {trace.details?.sql_executed && (
                  <div className="mt-1.5 p-2 rounded bg-slate-900/90 border border-slate-800 font-mono text-[11px] text-emerald-400 overflow-x-auto">
                    <code>{trace.details.sql_executed}</code>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center text-emerald-400 shrink-0 ml-2">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-950/40 border border-slate-800/40 animate-pulse">
            <Clock className="w-4 h-4 text-emerald-400 animate-spin" />
            <span className="text-xs text-slate-400">
              Agents coordinating cross-source retrieval and validation...
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
