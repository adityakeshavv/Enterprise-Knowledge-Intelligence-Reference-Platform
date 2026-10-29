import React, { useState, useEffect, useRef } from "react";
import { Sidebar, type NavTabId } from "./components/Sidebar";
import { HomeTab } from "./components/HomeTab";
import { QueryTab } from "./components/QueryTab";
import { TraceTab } from "./components/TraceTab";
import { KnowledgeTab } from "./components/KnowledgeTab";
import { IndustryTab } from "./components/IndustryTab";
import { AuditTab } from "./components/AuditTab";
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
import {
  Building2,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  ChevronRight,
  Menu,
  X
} from "lucide-react";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTabId>("home");
  const [industries, setIndustries] = useState<IndustrySummary[]>([]);
  const [activeIndustry, setActiveIndustry] = useState<IndustryDetail | null>(null);
  const [activeIndustryId, setActiveIndustryId] = useState<string>("manufacturing");
  const [queryInput, setQueryInput] = useState<string>("");
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);
  const [session, setSession] = useState<AuthSession | null>(() => getAuthSession());
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(getAuthSession()));
  const [error, setError] = useState<string | null>(null);
  const [errorContext, setErrorContext] = useState<"platform" | "industry" | "query" | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [pendingIndustryId, setPendingIndustryId] = useState<string | null>(null);
  const menuToggleRef = useRef<HTMLButtonElement>(null);
  const industryCancelRef = useRef<HTMLButtonElement>(null);
  const industryPickerRef = useRef<HTMLSelectElement>(null);

  // Load platform state after authentication
  useEffect(() => {
    if (session) {
      loadPlatformState();
    }
  }, [session]);

  useEffect(() => {
    const expireSession = () => {
      setSession(null);
      setError("Your session expired. Please sign in again.");
      setErrorContext(null);
      setQueryResult(null);
      setSelectedCitation(null);
    };
    window.addEventListener("nebula9:session-expired", expireSession);
    return () => window.removeEventListener("nebula9:session-expired", expireSession);
  }, []);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    const handleMobileMenuKeys = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMobileMenuOpen(false);
        menuToggleRef.current?.focus();
      }
      if (event.key === "Tab") {
        const links = document.querySelectorAll<HTMLElement>("#primary-navigation button");
        if (!links.length) return;
        const first = links[0];
        const last = links[links.length - 1];
        if (document.activeElement === menuToggleRef.current) {
          event.preventDefault();
          (event.shiftKey ? last : first).focus();
        } else if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          menuToggleRef.current?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          menuToggleRef.current?.focus();
        }
      }
    };
    window.addEventListener("keydown", handleMobileMenuKeys);
    return () => window.removeEventListener("keydown", handleMobileMenuKeys);
  }, [mobileMenuOpen]);

  useEffect(() => {
    if (!pendingIndustryId) return;
    const previousFocus = document.activeElement as HTMLElement | null;
    industryCancelRef.current?.focus();
    const handleDialogKeys = (event: KeyboardEvent) => {
      if (event.key === "Escape") setPendingIndustryId(null);
      if (event.key === "Tab") {
        const controls = document.querySelectorAll<HTMLElement>(".industry-confirm-dialog button");
        if (!controls.length) return;
        if (event.shiftKey && document.activeElement === controls[0]) { event.preventDefault(); controls[controls.length - 1].focus(); }
        else if (!event.shiftKey && document.activeElement === controls[controls.length - 1]) { event.preventDefault(); controls[0].focus(); }
      }
    };
    window.addEventListener("keydown", handleDialogKeys);
    return () => {
      window.removeEventListener("keydown", handleDialogKeys);
      (previousFocus && previousFocus !== document.body ? previousFocus : industryPickerRef.current)?.focus();
    };
  }, [pendingIndustryId]);

  const handleLogin = async (username: string, password: string) => {
    try {
      setError(null);
      setErrorContext(null);
      const authenticatedSession = await loginUser(username, password);
      setIsLoading(true);
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
    setErrorContext(null);
  };

  const loadPlatformState = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setErrorContext(null);
      const indList = await fetchAvailableIndustries();
      setIndustries(indList);

      const active = await fetchActiveIndustry();
      setActiveIndustry(active);
      setActiveIndustryId(active.id);

      if (active.scenarios && active.scenarios.length > 0 && !queryInput) {
        setQueryInput(active.scenarios[0].question);
      }
    } catch (err: any) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Unable to load workspace data. Check that the backend is available and try again.");
      setErrorContext("platform");
    } finally {
      setIsLoading(false);
    }
  };

  const applyIndustrySelection = async (newId: string) => {
    if (newId === activeIndustryId) return;
    try {
      setIsLoading(true);
      setError(null);
      setErrorContext(null);
      await switchActiveIndustry(newId);
      setActiveIndustryId(newId);
      const updatedActive = await fetchActiveIndustry();
      setActiveIndustry(updatedActive);
      if (updatedActive.scenarios.length > 0) {
        setQueryInput(updatedActive.scenarios[0].question);
      }
      setQueryResult(null);
    } catch (err: any) {
      if (getAuthSession()) {
        setError(`Failed to switch industry: ${err.message}`);
        setErrorContext("industry");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectIndustry = async (newId: string) => {
    if (newId === activeIndustryId) return;
    if (queryResult) {
      setPendingIndustryId(newId);
      return;
    }
    await applyIndustrySelection(newId);
  };

  const handleRunQuery = async (questionToRun?: string) => {
    const q = questionToRun || queryInput;
    if (!q.trim()) return;

    try {
      setIsLoading(true);
      setError(null);
      setErrorContext(null);
      const res = await executeQuery(q, activeIndustryId);
      setQueryResult(res);
    } catch (err: any) {
      if (getAuthSession()) {
        setError(`Query failed: ${err.message}`);
        setErrorContext("query");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!session) return <LoginPage onLogin={handleLogin} error={error} />;

  // Label lookup for top breadcrumb
  const tabTitles: Record<NavTabId, { title: string; subtitle: string }> = {
    home: { title: "Home Dashboard", subtitle: "Platform Overview & CXO Scenarios" },
    query: { title: "Ask Intelligence", subtitle: "Multi-Source Reasoning & Evidence Synthesis" },
    trace: { title: "Investigation Trace", subtitle: "Execution steps & evidence graph" },
    knowledge: { title: "Knowledge Sources", subtitle: "Representative source catalog" },
    industry: { title: "Industry Pack", subtitle: "Domain Ontologies, Terminology & Directives" },
    audit: { title: "Session & Governance", subtitle: "Signed-in account & latest query" },
  };

  return (
    <div className="app-layout">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      {/* Left Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          setMobileMenuOpen(false);
            if (window.matchMedia("(max-width: 900px)").matches) window.setTimeout(() => menuToggleRef.current?.focus(), 0);
        }}
        currentUser={session}
        onLogout={handleLogout}
        mobileMenuOpen={mobileMenuOpen}
        hasResult={Boolean(queryResult)}
        totalLatencyMs={queryResult?.total_latency_ms}
      />

      {/* Main Workspace Pane */}
      <div className="app-main-pane">
        {/* Top Sub-Header */}
        <header className={`top-subbar ${mobileMenuOpen ? "menu-open" : ""}`}>
          <div className="top-subbar-left">
            <button
              ref={menuToggleRef}
              className="mobile-menu-toggle"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
              aria-expanded={mobileMenuOpen}
              aria-controls="primary-navigation"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div className="breadcrumb-trail">
              <span className="breadcrumb-root">Nebula9</span>
              <ChevronRight size={14} className="breadcrumb-arrow" />
              <span className="breadcrumb-current">{tabTitles[activeTab].title}</span>
            </div>
            <span className="top-subbar-desc">
              {tabTitles[activeTab].subtitle}
            </span>
          </div>

          <div className="top-subbar-right">
            {/* Industry Switcher Dropdown */}
            <div className="subbar-industry-select-wrap">
              <Building2 size={16} className="text-muted" />
              <label htmlFor="industry-picker" className="sr-only">Select Industry</label>
              <select
                ref={industryPickerRef}
                id="industry-picker"
                className="subbar-industry-select"
                value={activeIndustryId}
                onChange={(e) => { setMobileMenuOpen(false); handleSelectIndustry(e.target.value); }}
                disabled={isLoading}
              >
                {industries.map((ind) => (
                  <option key={ind.id} value={ind.id}>
                    {ind.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Quick Action Button */}
            {activeTab !== "query" && (
              <button
                className="subbar-query-btn"
                onClick={() => { setActiveTab("query"); setMobileMenuOpen(false); }}
                title="Open Ask Intelligence"
              >
                <Sparkles size={14} />
                <span>Ask Question</span>
              </button>
            )}

            {/* User Clearance Pill */}
            <div className="subbar-user-badge">
              <ShieldCheck size={14} className="text-success" />
              <span>{session.role} account</span>
            </div>
          </div>
        </header>

        {mobileMenuOpen && <button className="mobile-nav-backdrop" aria-label="Close navigation" onClick={() => { setMobileMenuOpen(false); menuToggleRef.current?.focus(); }} />}

        {/* Global Connection / Query Error Banner */}
        {error && (
          <div className="error-banner global-error" role="alert">
            <span>{error}</span>
            {errorContext === "platform" && <button className="btn-retry" onClick={loadPlatformState}><RefreshCw size={14} /> Retry loading workspace</button>}
            <button className="error-dismiss" aria-label="Dismiss message" onClick={() => setError(null)}><X size={14} /></button>
          </div>
        )}

        {/* Dynamic Tab Content Area */}
        <main className="tab-content-area" id="main-content" aria-busy={isLoading}>
          {activeTab === "home" && (
            <HomeTab
              activeIndustry={activeIndustry}
              onNavigate={(tab) => setActiveTab(tab)}
              onSelectScenario={(q) => {
                setQueryInput(q);
                setActiveTab("query");
                handleRunQuery(q);
              }}
              isLoading={isLoading}
            />
          )}

          {activeTab === "query" && (
            <QueryTab
              queryInput={queryInput}
              onQueryInputChange={setQueryInput}
              onRunQuery={handleRunQuery}
              queryResult={queryResult}
              onOpenCitation={(c) => setSelectedCitation(c)}
              isLoading={isLoading}
              activeIndustry={activeIndustry}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === "trace" && (
            <TraceTab
              queryResult={queryResult}
              onOpenCitation={(c) => setSelectedCitation(c)}
              onNavigate={(tab) => setActiveTab(tab)}
              onRunDefaultScenario={() => {
                if (activeIndustry?.scenarios && activeIndustry.scenarios.length > 0) {
                  const defaultQ = activeIndustry.scenarios[0].question;
                  setQueryInput(defaultQ);
                  setActiveTab("query");
                }
              }}
            />
          )}

          {activeTab === "knowledge" && (
            <KnowledgeTab activeIndustry={activeIndustry} />
          )}

          {activeTab === "industry" && (
            <IndustryTab
              industries={industries}
              activeIndustry={activeIndustry}
              activeIndustryId={activeIndustryId}
              onSelectIndustry={handleSelectIndustry}
              isLoading={isLoading}
              canViewPrompts={session.role === "Admin"}
            />
          )}

          {activeTab === "audit" && (
            <AuditTab
              currentUser={session}
              queryResult={queryResult}
              activeIndustryId={activeIndustryId}
            />
          )}
        </main>
      </div>

      {/* Slide-out Evidence Inspection Drawer */}
      {pendingIndustryId && (
        <div className="scenario-modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setPendingIndustryId(null); }}>
          <section className="scenario-modal industry-confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="industry-change-title" aria-describedby="industry-change-description">
            <span className="scenario-category">Workspace scope</span>
            <h2 id="industry-change-title">Switch industry pack?</h2>
            <p className="scenario-modal-question" id="industry-change-description">Switch to {industries.find((industry) => industry.id === pendingIndustryId)?.name || pendingIndustryId}? This clears the current answer so the next investigation uses the new knowledge scope.</p>
            <div className="scenario-modal-actions">
              <button ref={industryCancelRef} type="button" className="btn-secondary-action" onClick={() => setPendingIndustryId(null)}>Stay here</button>
              <button type="button" className="btn-primary-action" disabled={isLoading} onClick={() => { const nextId = pendingIndustryId; setPendingIndustryId(null); void applyIndustrySelection(nextId); }}>Switch pack</button>
            </div>
          </section>
        </div>
      )}

      <EvidenceDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
};

export default App;
