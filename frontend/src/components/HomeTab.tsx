import React from "react";
import type { IndustryDetail } from "../types";
import { ScenarioCard } from "./ScenarioCard";
import type { NavTabId } from "./Sidebar";
import {
  Sparkles,
  Cpu,
  Database,
  ShieldCheck,
  ArrowRight,
  Zap,
  FileCheck2,
  Layers,
  Loader2
} from "lucide-react";

interface HomeTabProps {
  activeIndustry: IndustryDetail | null;
  onNavigate: (tab: NavTabId) => void;
  onSelectScenario: (question: string) => void;
  isLoading: boolean;
}

export const HomeTab: React.FC<HomeTabProps> = ({
  activeIndustry,
  onNavigate,
  onSelectScenario,
  isLoading,
}) => {
  const industryName = activeIndustry?.metadata.name || "Enterprise Knowledge Intelligence";
  const scenarios = activeIndustry?.scenarios || [];

  if (isLoading && !activeIndustry) {
    return <div className="workspace-loading" role="status"><Loader2 size={20} className="animate-spin" /><span>Loading your workspace…</span></div>;
  }

  return (
    <div className="tab-page home-tab">
      {/* Hero Banner */}
      <section className="home-hero-card">
        <div className="home-hero-content">
          <div className="hero-pill-badge">
            <Zap size={14} className="text-warning" />
            <span>Enterprise knowledge, in one workspace</span>
          </div>
          <h2 className="home-hero-title">{industryName}</h2>
          <p className="home-hero-desc">
            Ask questions across the knowledge sources configured for this workspace, then review answers alongside their citations and investigation traces.
          </p>
          <div className="home-hero-actions">
            <button
              className="btn-primary-action"
              onClick={() => onNavigate("query")}
            >
              <Sparkles size={16} />
              <span>Ask Intelligence</span>
              <ArrowRight size={15} />
            </button>
            <button
              className="btn-secondary-action"
              onClick={() => onNavigate("knowledge")}
            >
              <Database size={16} />
              <span>Explore Knowledge Base</span>
            </button>
          </div>
        </div>

        {/* Quick Capabilities Highlights */}
        <div className="hero-stats-grid">
          <div className="hero-stat-box">
            <div className="stat-icon-wrap accent-blue">
              <Cpu size={20} />
            </div>
            <div className="stat-details">
              <span className="stat-value">{scenarios.length}</span>
              <span className="stat-label">Available scenarios</span>
              <span className="stat-sub">For this industry pack</span>
            </div>
          </div>

          <div className="hero-stat-box">
            <div className="stat-icon-wrap accent-purple">
              <FileCheck2 size={20} />
            </div>
            <div className="stat-details">
              <span className="stat-value">{activeIndustry?.metadata.version || "—"}</span>
              <span className="stat-label">Pack version</span>
              <span className="stat-sub">Selected workspace</span>
            </div>
          </div>

          <div className="hero-stat-box">
            <div className="stat-icon-wrap accent-green">
              <ShieldCheck size={20} />
            </div>
            <div className="stat-details">
              <span className="stat-value">Citations</span>
              <span className="stat-label">Review answer sources</span>
              <span className="stat-sub">Open source details inline</span>
            </div>
          </div>

          <div className="hero-stat-box">
            <div className="stat-icon-wrap accent-amber">
              <Layers size={20} />
            </div>
            <div className="stat-details">
              <span className="stat-value">{activeIndustry?.terminology ? Object.keys(activeIndustry.terminology).length : 0}</span>
              <span className="stat-label">Domain terms</span>
              <span className="stat-sub">Configured terminology</span>
            </div>
          </div>
        </div>
      </section>

      {/* Suggested CXO Scenarios Section */}
      <section className="home-scenarios-section">
        <div className="section-header-row">
          <div className="section-header-title">
            <Sparkles size={18} className="text-accent" />
            <h3>Start with a suggested question</h3>
          </div>
          <span className="section-header-hint">
            Choose a scenario to review its question before submitting it.
          </span>
        </div>

        {scenarios.length > 0 ? (
          <div className="scenarios-grid">
            {scenarios.map((sc) => (
              <ScenarioCard
                key={sc.id}
                scenario={sc}
                onSelect={(q) => onSelectScenario(q)}
                disabled={isLoading}
              />
            ))}
          </div>
        ) : (
          <div className="empty-scenarios-box">
            <p>No pre-configured scenarios loaded for this industry pack.</p>
          </div>
        )}
      </section>

      {/* Navigation Quick Jump Cards */}
      <section className="home-navigation-cards">
        <div className="section-header-row">
          <div className="section-header-title">
            <Layers size={18} className="text-accent" />
            <h3>Explore your workspace</h3>
          </div>
        </div>

        <div className="nav-cards-grid">
          <div className="nav-card" role="button" tabIndex={0} onClick={() => onNavigate("query")} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onNavigate("query"); } }}>
            <div className="nav-card-header">
              <div className="nav-card-icon accent-blue">
                <Sparkles size={20} />
              </div>
              <ArrowRight size={16} className="nav-card-arrow" />
            </div>
            <h4>Ask Intelligence</h4>
            <p>Ask a question and review the response with its available evidence.</p>
          </div>

          <div className="nav-card" role="button" tabIndex={0} onClick={() => onNavigate("trace")} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onNavigate("trace"); } }}>
            <div className="nav-card-header">
              <div className="nav-card-icon accent-purple">
                <Cpu size={20} />
              </div>
              <ArrowRight size={16} className="nav-card-arrow" />
            </div>
            <h4>Agent Reasoning & Graph</h4>
            <p>Inspect the execution steps and explore how evidence is connected.</p>
          </div>

          <div className="nav-card" role="button" tabIndex={0} onClick={() => onNavigate("knowledge")} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onNavigate("knowledge"); } }}>
            <div className="nav-card-header">
              <div className="nav-card-icon accent-green">
                <Database size={20} />
              </div>
              <ArrowRight size={16} className="nav-card-arrow" />
            </div>
            <h4>Knowledge Base</h4>
            <p>Browse representative documents for this industry pack.</p>
          </div>

          <div className="nav-card" role="button" tabIndex={0} onClick={() => onNavigate("audit")} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onNavigate("audit"); } }}>
            <div className="nav-card-header">
              <div className="nav-card-icon accent-amber">
                <ShieldCheck size={20} />
              </div>
              <ArrowRight size={16} className="nav-card-arrow" />
            </div>
            <h4>Governance & Security</h4>
            <p>Review your signed-in account and latest query in this browser session.</p>
          </div>
        </div>
      </section>
    </div>
  );
};
