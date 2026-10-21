import React from "react";
import type { IndustrySummary } from "../types";
import type { AuthSession } from "../services/api";
import { Building2, LogOut, ShieldCheck } from "lucide-react";
import logo from "../assets/nebula9-logo.png";

interface HeaderProps {
  industries: IndustrySummary[];
  activeIndustryId: string;
  onSelectIndustry: (id: string) => void;
  currentUser: AuthSession;
  onLogout: () => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  industries,
  activeIndustryId,
  onSelectIndustry,
  currentUser,
  onLogout,
  isLoading,
}) => (
  <header className="header-container">
    <div className="header-brand">
      <div className="logo-badge"><img src={logo} alt="" /></div>
      <div>
        <h1 className="brand-title">Nebula9 Knowledge Intelligence</h1>
        <p className="brand-subtitle">Enterprise intelligence workspace</p>
      </div>
    </div>

    <div className="header-actions">
      <label className="action-group">
        <Building2 size={16} className="text-muted" />
        <span className="action-label">Industry</span>
        <select
          className="industry-select"
          value={activeIndustryId}
          onChange={(event) => onSelectIndustry(event.target.value)}
          disabled={isLoading}
          aria-label="Select industry"
        >
          {industries.map((industry) => <option key={industry.id} value={industry.id}>{industry.name}</option>)}
        </select>
      </label>

      <div className="user-session">
        <span className="user-session-avatar"><ShieldCheck size={15} /></span>
        <span className="user-session-copy"><strong>{currentUser.full_name}</strong><small>{currentUser.role} account</small></span>
        <button className="logout-button" onClick={onLogout} title="Sign out" aria-label="Sign out">
          <LogOut size={16} /><span>Sign out</span>
        </button>
      </div>
    </div>
  </header>
);
