import React, { useState, useEffect } from 'react';
import { Send, RefreshCw } from 'lucide-react';
import { Header } from './components/Header';
import { ScenarioCards } from './components/ScenarioCards';
import { AgentActivityFeed } from './components/AgentActivityFeed';
import { ExecutiveAnswer } from './components/ExecutiveAnswer';
import { EvidenceDrawer } from './components/EvidenceDrawer';
import { ConflictModal } from './components/ConflictModal';
import { AuditTelemetryModal } from './components/AuditTelemetryModal';
import { IndustrySummary, Scenario, QueryResponse, Citation, UserSession } from './types';

export const App: React.FC = () => {
  // State
  const [industries, setIndustries] = useState<IndustrySummary[]>([]);
  const [selectedIndustryId, setSelectedIndustryId] = useState<string>('manufacturing');
  const [industryPack, setIndustryPack] = useState<any>(null);
  const [currentUser, setCurrentUser] = useState<UserSession>({
    user_id: 'usr_exec_01',
    username: 'executive',
    display_name: 'Chief Operating Officer',
    role: 'Executive',
    allowed_workspaces: ['plant_a', 'plant_b']
  });

  const [inputQuery, setInputQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);

  // Modals & Drawers
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [isConflictOpen, setIsConflictOpen] = useState<boolean>(false);
  const [isAuditOpen, setIsAuditOpen] = useState<boolean>(false);

  // 1. Fetch available industries on mount
  useEffect(() => {
    fetchIndustries();
  }, []);

  // 2. Fetch specific industry configuration when selected
  useEffect(() => {
    if (selectedIndustryId) {
      fetchIndustryDetails(selectedIndustryId);
      // Reset state for clean switch
      setResponse(null);
    }
  }, [selectedIndustryId]);

  const fetchIndustries = async () => {
    try {
      const res = await fetch('/api/industries');
      if (res.ok) {
        const data = await res.json();
        setIndustries(data);
      }
    } catch (e) {
      console.error('Failed to load industries', e);
    }
  };

  const fetchIndustryDetails = async (id: string) => {
    try {
      const res = await fetch(`/api/industries/${id}`);
      if (res.ok) {
        const data = await res.json();
        setIndustryPack(data);
      }
    } catch (e) {
      console.error(`Failed to load industry pack for ${id}`, e);
    }
  };

  const toggleUserRole = () => {
    if (currentUser.role === 'Executive') {
      setCurrentUser({
        user_id: 'usr_audit_01',
        username: 'auditor',
        display_name: 'Compliance & Security Auditor',
        role: 'Auditor',
        allowed_workspaces: ['all']
      });
    } else {
      setCurrentUser({
        user_id: 'usr_exec_01',
        username: 'executive',
        display_name: 'Chief Operating Officer',
        role: 'Executive',
        allowed_workspaces: ['plant_a', 'plant_b']
      });
    }
  };

  const executeQuery = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;
    setIsLoading(true);
    setResponse(null);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          industry_id: selectedIndustryId,
          workspace_id: 'plant_a'
        })
      });

      if (res.ok) {
        const data = await res.json();
        setResponse(data);
      } else {
        console.error('Query execution error');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectScenario = (sc: Scenario) => {
    setInputQuery(sc.question);
    executeQuery(sc.question);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeQuery(inputQuery);
  };

  const scenarios: Scenario[] = industryPack?.scenarios?.scenarios || [];
  const kpis = industryPack?.industry?.kpis || [];

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Header
        industries={industries}
        selectedIndustryId={selectedIndustryId}
        onSelectIndustry={setSelectedIndustryId}
        currentUser={currentUser}
        onToggleUserRole={toggleUserRole}
        onOpenAudit={() => setIsAuditOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Industry Banner & KPIs */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 relative overflow-hidden">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
                  Zero-Code Declarative Pack
                </span>
                <span className="text-xs text-slate-500 font-mono">v1.0.0</span>
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-white">
                {industryPack?.industry?.name || 'Loading Domain Pack...'}
              </h1>
              <p className="text-sm text-slate-400 mt-1 max-w-2xl">
                {industryPack?.industry?.tagline ||
                  'Unified multi-agent intelligence across enterprise operational databases, engineering archives, and supplier advisories.'}
              </p>
            </div>

            {/* Live Domain KPIs */}
            {kpis.length > 0 && (
              <div className="flex items-center gap-4 bg-slate-950/80 p-3.5 rounded-2xl border border-slate-800">
                {kpis.map((kpi: any) => (
                  <div key={kpi.id} className="text-center px-2">
                    <span className="text-[11px] text-slate-400 uppercase font-medium block">
                      {kpi.label}
                    </span>
                    <span className="text-lg font-bold text-emerald-400 font-mono">
                      {kpi.target}
                      <span className="text-xs ml-0.5 text-slate-400">{kpi.unit}</span>
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Query Input Section */}
        <section className="space-y-4">
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask any cross-source operational question (e.g. downtime root causes, supplier anomalies)..."
              disabled={isLoading}
              className="w-full bg-slate-900 border border-slate-800 focus:border-emerald-500 rounded-2xl py-4 pl-5 pr-32 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition shadow-lg shadow-black/20"
            />
            <button
              type="submit"
              disabled={isLoading || !inputQuery.trim()}
              className="absolute right-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 disabled:hover:bg-emerald-500 text-white font-medium text-xs flex items-center space-x-2 transition shadow-md shadow-emerald-500/20"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Reasoning...</span>
                </>
              ) : (
                <>
                  <span>Run Analysis</span>
                  <Send className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Curated CXO Scenarios */}
          <ScenarioCards
            scenarios={scenarios}
            onSelectScenario={handleSelectScenario}
            isLoading={isLoading}
          />
        </section>

        {/* Live Multi-Agent Reasoning Feed */}
        {(isLoading || (response && response.agent_trace.length > 0)) && (
          <section>
            <AgentActivityFeed
              traces={response ? response.agent_trace : []}
              isLoading={isLoading}
            />
          </section>
        )}

        {/* Executive Structured Answer */}
        {response && (
          <section>
            <ExecutiveAnswer
              response={response}
              onOpenEvidence={(c) => setActiveCitation(c)}
              onOpenConflict={() => setIsConflictOpen(true)}
            />
          </section>
        )}
      </main>

      {/* Drawers & Modals */}
      <EvidenceDrawer citation={activeCitation} onClose={() => setActiveCitation(null)} />
      <ConflictModal
        conflicts={response?.conflicts || []}
        isOpen={isConflictOpen}
        onClose={() => setIsConflictOpen(false)}
      />
      <AuditTelemetryModal isOpen={isAuditOpen} onClose={() => setIsAuditOpen(false)} />
    </div>
  );
};

export default App;
