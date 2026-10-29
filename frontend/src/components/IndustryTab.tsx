import React, { useState } from "react";
import type { IndustryDetail, IndustrySummary } from "../types";
import {
  Building2,
  BookOpen,
  Search,
  CheckCircle2,
  FileCode2,
  Cpu
} from "lucide-react";

interface IndustryTabProps {
  industries: IndustrySummary[];
  activeIndustry: IndustryDetail | null;
  activeIndustryId: string;
  onSelectIndustry: (id: string) => void;
  isLoading: boolean;
  canViewPrompts: boolean;
}

export const IndustryTab: React.FC<IndustryTabProps> = ({
  industries,
  activeIndustry,
  activeIndustryId,
  onSelectIndustry,
  isLoading,
  canViewPrompts,
}) => {
  const [searchTerm, setSearchTerm] = useState("");

  const terminology = activeIndustry?.terminology || {};
  const termsList = Object.entries(terminology).map(([key, val]) => ({
    term: key,
    fullName: val.full_name,
    definition: val.definition,
  }));

  const filteredTerms = termsList.filter(
    (t) =>
      t.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.definition.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="tab-page industry-tab">
      {/* Industry Overview Header */}
      <section className="industry-header-card">
        <div className="industry-header-content">
          <div className="icon-badge accent-purple">
            <Building2 size={22} />
          </div>
          <div>
            <h3>Industry Pack: {activeIndustry?.metadata.name || "Enterprise Domain"}</h3>
            <p>
              Modular configuration layer defining domain ontologies, specific entity extractors,
              acronym dictionaries, and specialized prompt templates without modifying core multi-agent code.
            </p>
          </div>
        </div>

        {/* Industry Switcher Buttons */}
        <div className="industry-switch-grid">
          {industries.map((ind) => {
            const isSelected = ind.id === activeIndustryId;
            return (
              <button
                key={ind.id}
                className={`ind-switch-card ${isSelected ? "selected" : ""}`}
                onClick={() => onSelectIndustry(ind.id)}
                disabled={isLoading || isSelected}
              >
                <div className="ind-switch-top">
                  <span className="ind-name">{ind.name}</span>
                  {isSelected && <CheckCircle2 size={16} className="text-success" />}
                </div>
                <span className="ind-desc">{ind.description}</span>
                <div className="ind-meta">
                  <span className="ind-scenarios">{ind.scenario_count} Scenarios</span>
                  <span className="ind-version">{ind.version}</span>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Domain Terminology Dictionary */}
      <section className="terminology-section">
        <div className="section-header-row">
          <div className="section-header-title">
            <BookOpen size={18} className="text-accent" />
            <h3>Domain Terminology & Acronym Dictionary</h3>
          </div>
          <div className="terms-search-box">
            <Search size={15} className="text-muted" />
            <input
              aria-label="Search industry terminology"
              type="text"
              placeholder="Search domain terms (e.g. OEE, MTBF)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="terms-grid">
          {filteredTerms.map((item) => (
            <div key={item.term} className="term-card">
              <div className="term-badge-row">
                <span className="term-acronym">{item.term}</span>
                <span className="term-fullname">{item.fullName}</span>
              </div>
              <p className="term-definition">{item.definition}</p>
            </div>
          ))}
          {filteredTerms.length === 0 && (
            <div className="empty-terms">
              <p>No matching domain terminology found for "{searchTerm}".</p>
            </div>
          )}
        </div>
      </section>

      {/* Prompts & Agent Configuration */}
      {canViewPrompts && activeIndustry?.prompts && Object.keys(activeIndustry.prompts).length > 0 && (
        <section className="industry-prompts-section">
          <div className="section-header-row">
            <div className="section-header-title">
              <FileCode2 size={18} className="text-accent" />
              <h3>Configured Agent Directives & Prompts</h3>
            </div>
          </div>
          <div className="prompts-list">
            {Object.entries(activeIndustry.prompts).map(([promptKey, promptText]) => (
              <div key={promptKey} className="prompt-item-box">
                <div className="prompt-item-header">
                  <Cpu size={14} className="text-accent" />
                  <strong>{promptKey.toUpperCase()}</strong>
                </div>
                <pre className="prompt-item-code">{promptText}</pre>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
