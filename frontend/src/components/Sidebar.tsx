import React from "react";
import type { AuthSession } from "../services/api";
import {
  LayoutDashboard,
  Sparkles,
  Cpu,
  Database,
  Building2,
  ShieldCheck,
  LogOut,
  ChevronRight
} from "lucide-react";
import logo from "../assets/nebula9-logo.png";

export type NavTabId = "home" | "query" | "trace" | "knowledge" | "industry" | "audit";

interface SidebarProps {
  activeTab: NavTabId;
  onSelectTab: (tab: NavTabId) => void;
  currentUser: AuthSession;
  onLogout: () => void;
  hasResult: boolean;
  totalLatencyMs?: number;
  mobileMenuOpen: boolean;
}

interface NavItem {
  id: NavTabId;
  label: string;
  sublabel: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  currentUser,
  onLogout,
  hasResult,
  totalLatencyMs,
  mobileMenuOpen,
}) => {
  const navItems: NavItem[] = [
    {
      id: "home",
      label: "Home Dashboard",
      sublabel: "Overview & Scenarios",
      icon: LayoutDashboard,
    },
    {
      id: "query",
      label: "Ask Intelligence",
      sublabel: "Multi-Source Reasoning",
      icon: Sparkles,
      badge: hasResult ? "Result Ready" : undefined,
    },
    {
      id: "trace",
      label: "Agent Pipeline Trace",
      sublabel: "Execution & Evidence",
      icon: Cpu,
      badge: totalLatencyMs ? `${(totalLatencyMs / 1000).toFixed(1)}s` : undefined,
    },
    {
      id: "knowledge",
      label: "Knowledge Base",
      sublabel: "Documents & SQL Sources",
      icon: Database,
    },
    {
      id: "industry",
      label: "Industry Pack",
      sublabel: "Taxonomy & Terminology",
      icon: Building2,
    },
    {
      id: "audit",
      label: "Governance & Audit",
      sublabel: "RBAC & Security Gate",
      icon: ShieldCheck,
    },
  ];

  return (
    <aside className={`app-sidebar ${mobileMenuOpen ? "mobile-open" : ""}`} aria-label="Main Navigation" id="primary-navigation">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-logo-wrap">
          <img src={logo} alt="Nebula9" className="brand-logo-img" />
        </div>
        <div className="brand-text">
          <h1 className="brand-name">Nebula9</h1>
          <span className="brand-tag">Knowledge Intelligence</span>
        </div>
      </div>

      {/* Navigation Label */}
      <div className="sidebar-section-heading">
        <span>WORKSPACES & TOOLS</span>
      </div>

      {/* Vertical Navigation Tabs */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-nav-tab ${isActive ? "active" : ""}`}
              onClick={() => onSelectTab(item.id)}
              aria-current={isActive ? "page" : undefined}
            >
              <div className="tab-icon-wrap">
                <Icon size={18} className={isActive ? "icon-active" : "icon-idle"} />
              </div>
              <div className="tab-label-wrap">
                <div className="tab-title-row">
                  <span className="tab-label">{item.label}</span>
                  {item.badge && (
                    <span className={`tab-badge ${isActive ? "badge-active" : ""}`}>
                      {item.badge}
                    </span>
                  )}
                </div>
                <span className="tab-sublabel">{item.sublabel}</span>
              </div>
              {isActive && <ChevronRight size={14} className="active-arrow" />}
            </button>
          );
        })}
      </nav>

      {/* Workspace guidance */}
      <div className="sidebar-status-card">
        <div className="status-indicator-row">
          <Building2 size={14} className="text-accent" />
          <span className="status-text">Workspace scope</span>
        </div>
        <div className="status-details">
          <span>Use the industry selector above to change the active knowledge pack.</span>
        </div>
      </div>

      {/* User Session & Logout */}
      <div className="sidebar-footer">
        <div className="user-profile-card">
          <div className="user-avatar-badge">
            <ShieldCheck size={16} />
          </div>
          <div className="user-details">
            <span className="user-name">{currentUser.full_name}</span>
            <span className="user-role">{currentUser.role} Account</span>
          </div>
        </div>
        <button
          className="sidebar-logout-btn"
          onClick={onLogout}
          title="Sign out of platform"
        >
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
