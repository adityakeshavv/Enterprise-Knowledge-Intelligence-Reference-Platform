import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { ScenarioCard } from "./components/ScenarioCard";
import { AgentTrace } from "./components/AgentTrace";
import { AnswerView } from "./components/AnswerView";
import { EvidenceDrawer } from "./components/EvidenceDrawer";
import { LoginPage } from "./components/LoginPage";
import type {
  IndustrySummary,
  IndustryDetail,
  QueryResponse,
  CitationItem,
} from "./types";
import type { AuthSession } from "./services/api";
import {
  fetchAvailableIndustries,
  fetchActiveIndustry,
  switchActiveIndustry,
  executeQuery,
  loginUser,
  getAuthSession,
  clearAuthSession,
} from "./services/api";
import { Send, Sparkles, Loader2, RefreshCw } from "lucide-react";

export const App: React.FC = () => {
  const [industries, setIndustries] = useState<IndustrySummary[]>([]);
  const [activeIndustry, setActiveIndustry] = useState<IndustryDetail | null>(null);
  const [activeIndustryId, setActiveIndustryId] = useState<string>("manufacturing");
  const [queryInput, setQueryInput] = useState<string>("");
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);
  const [session, setSession] = useState<AuthSession | null>(() => getAuthSession());
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load the workspace after the user has signed in.
  useEffect(() => {
    if (session) loadPlatformState();
  }, [session]);

  const handleLogin = async (username: string, password: string) => {
    try {
      setError(null);
      const authenticatedSession = await loginUser(username, password);
      setSession(authenticatedSession);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in. Please try again.");
      throw err;
    }
  };

  const handleLogout = () => {
    clearAuthSession();
    setSession(null);
    setActiveIndustry(null);
    setQueryResult(null);
    setSelectedCitation(null);
    setError(null);
  };

  const loadPlatformState = async () => {
    try {
      setError(null);
      const indList = await fetchAvailableIndustries();
      setIndustries(indList);

      const active = await fetchActiveIndustry();
      setActiveIndustry(active);
      setActiveIndustryId(active.id);

      // Pre-populate query input with default scenario if empty
      if (active.scenarios && active.scenarios.length > 0 && !queryInput) {
        setQueryInput(active.scenarios[0].question);
      }
    } catch (err: any) {
      console.error(err);
      setError("Unable to connect to backend server. Make sure FastAPI is running on port 8000.");
    }
  };

  const handleSelectIndustry = async (newId: string) => {
    if (newId === activeIndustryId) return;
    try {
      setIsLoading(true);
      await switchActiveIndustry(newId);
      setActiveIndustryId(newId);
      const updatedActive = await fetchActiveIndustry();
      setActiveIndustry(updatedActive);
      if (updatedActive.scenarios.length > 0) {
        setQueryInput(updatedActive.scenarios[0].question);
      }
      setQueryResult(null);
    } catch (err: any) {
      setError(`Failed to switch industry: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunQuery = async (questionToRun?: string) => {
    const q = questionToRun || queryInput;
    if (!q.trim()) return;

    try {
      setIsLoading(true);
      setError(null);
      const res = await executeQuery(q, activeIndustryId);
      setQueryResult(res);
    } catch (err: any) {
      setError(`Query failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (!session) return <LoginPage onLogin={handleLogin} error={error} />;

  return (
    <div className="app-shell">
      <Header
        industries={industries}
        activeIndustryId={activeIndustryId}
        onSelectIndustry={handleSelectIndustry}
        currentUser={session}
        onLogout={handleLogout}
        isLoading={isLoading}
      />

      <main className="main-content">
        {/* Error Notification */}
        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button className="btn-retry" onClick={loadPlatformState}>
              <RefreshCw size={14} /> Retry Connection
            </button>
          </div>
        )}

        {/* Hero & Query Bar */}
        <section className="query-section">
          <div className="hero-text">
            <h2>
              {activeIndustry?.metadata.name || "Enterprise Knowledge Intelligence"}
            </h2>
            <p>
              Ask complex cross-source business questions. The platform routes across databases,
              documents, and external intelligence with evidence-first verification.
            </p>
          </div>

          <div className="query-box">
            <input
              type="text"
              className="query-input"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRunQuery()}
              placeholder="Ask an enterprise question across SQL, documents, and external sources..."
              disabled={isLoading}
            />
            <button
              className="btn-submit"
              onClick={() => handleRunQuery()}
              disabled={isLoading || !queryInput.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Reasoning...</span>
                </>
              ) : (
                <>
                  <Send size={16} />
                  <span>Ask Intelligence</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* Pre-configured CXO Scenarios */}
        {activeIndustry?.scenarios && activeIndustry.scenarios.length > 0 && (
          <section className="scenarios-section">
            <div className="section-title-row">
              <Sparkles size={16} className="text-accent" />
              <h3>Suggested CXO Business Scenarios</h3>
              <span className="text-muted text-xs">
                (Click any scenario to execute multi-agent query)
              </span>
            </div>
            <div className="scenarios-grid">
              {activeIndustry.scenarios.map((sc) => (
                <ScenarioCard
                  key={sc.id}
                  scenario={sc}
                  onSelect={(q) => {
                    setQueryInput(q);
                    handleRunQuery(q);
                  }}
                  disabled={isLoading}
                />
              ))}
            </div>
          </section>
        )}

        {/* Results Section */}
        {queryResult && (
          <section className="results-section">
            {/* Multi-Agent Reasoning Trace */}
            <AgentTrace
              steps={queryResult.trace_steps}
              totalLatencyMs={queryResult.total_latency_ms}
            />

            {/* Answer View */}
            <AnswerView
              data={queryResult}
              onOpenCitation={(citation) => setSelectedCitation(citation)}
            />
          </section>
        )}
      </main>

      {/* Slide-out Evidence Inspection Drawer */}
      <EvidenceDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
};

export default App;
