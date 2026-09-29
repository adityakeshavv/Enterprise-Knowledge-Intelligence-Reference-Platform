import React, { useEffect, useState } from 'react';
import { X, Activity, RefreshCw } from 'lucide-react';

interface AuditTelemetryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuditTelemetryModal: React.FC<AuditTelemetryModalProps> = ({ isOpen, onClose }) => {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchAuditEvents = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/audit/events?limit=25');
      if (res.ok) {
        const data = await res.json();
        setEvents(data.events || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchAuditEvents();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-4xl w-full p-6 space-y-5 shadow-2xl max-h-[85vh] flex flex-col justify-between">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">
                Enterprise Audit & Observability Console
              </h3>
              <p className="text-xs text-slate-400">
                Immutable, tamper-evident telemetry logs across user queries, agents, and source accesses
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchAuditEvents}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              title="Refresh Logs"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {events.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No audit records logged yet. Execute an executive query to observe telemetry.
            </div>
          ) : (
            events.map((ev, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 text-[10px] font-mono">
                      {ev.event_type}
                    </span>
                    <span className="font-semibold text-slate-300">
                      User: {ev.user_id} ({ev.user_role})
                    </span>
                  </div>
                  <span className="text-slate-500 font-mono text-[10px]">
                    {new Date(ev.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <p className="text-slate-200 font-medium">"{ev.query}"</p>

                <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400 font-mono">
                  <span>Latency: {ev.latency_ms}ms</span>
                  <span>•</span>
                  <span>Grounding: {Math.round(ev.grounding_score * 100)}%</span>
                  <span>•</span>
                  <span>Agents: {ev.agents_invoked?.join(', ')}</span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
