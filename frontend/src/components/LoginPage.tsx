import React, { useState } from "react";
import { ArrowRight, Eye, EyeOff, Fingerprint, LockKeyhole, ShieldCheck, Sparkles, UserRound } from "lucide-react";
import logo from "../assets/nebula9-logo.png";

interface LoginPageProps {
  onLogin: (username: string, password: string) => Promise<void>;
  error: string | null;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin, error }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onLogin(username.trim(), password);
    } catch {
      // The parent keeps the API error in view; avoid an unhandled event rejection.
    } finally {
      setIsSubmitting(false);
    }
  };

  const setAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <main className="login-screen">
      <section className="login-showcase" aria-label="Nebula9 platform overview">
        <div className="showcase-orb showcase-orb-one" />
        <div className="showcase-orb showcase-orb-two" />
        <div className="showcase-content">
          <div className="login-brand">
            <span className="login-logo-frame"><img src={logo} alt="Nebula9 logo" /></span>
            <span className="login-brand-name">Nebula9<span>®</span></span>
          </div>

          <div className="showcase-copy">
            <span className="eyebrow"><Sparkles size={14} /> ENTERPRISE KNOWLEDGE INTELLIGENCE</span>
            <h1>Make better decisions with knowledge you can trust.</h1>
            <p>Bring your operational data and documents together in one clear, evidence-led workspace.</p>
          </div>

          <div className="showcase-proof">
            <div className="proof-icon"><Fingerprint size={18} /></div>
            <div><strong>Designed for confident decisions</strong><span>Clear answers. Traceable evidence. One view.</span></div>
            <ShieldCheck className="proof-shield" size={19} />
          </div>
          <div className="showcase-footer"><span>© 2026 Nebula9</span><span>Secure workspace access</span></div>
        </div>
      </section>

      <section className="login-panel" aria-label="Sign in">
        <div className="login-form-wrap">
          <div className="mobile-login-brand"><img src={logo} alt="" /><span>Nebula9</span></div>
          <div className="login-heading">
            <span className="login-kicker">WELCOME BACK</span>
            <h2>Sign in to your workspace</h2>
            <p>Enter your account details to continue.</p>
          </div>

          <form className="login-form" onSubmit={submit} aria-busy={isSubmitting}>
            <label htmlFor="username">Username</label>
            <div className="login-input-wrap">
              <UserRound size={17} aria-hidden="true" />
              <input id="username" name="username" autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Enter your username" required autoFocus />
            </div>

            <div className="password-label-row"><label htmlFor="password">Password</label></div>
            <div className="login-input-wrap">
              <LockKeyhole size={17} aria-hidden="true" />
              <input id="password" name="password" autoComplete="current-password" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required />
              <button className="password-toggle" type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Hide password" : "Show password"}>
                {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </div>

            {error && <div className="login-error" role="alert">{error}</div>}

            <button className="login-submit" type="submit" disabled={isSubmitting || !username.trim() || !password}>
              <span>{isSubmitting ? "Signing in…" : "Sign in securely"}</span>
              {isSubmitting ? <span className="login-spinner" /> : <ArrowRight size={17} />}
            </button>
          </form>

          <div className="demo-access-card">
            <div className="demo-access-top"><span className="demo-dot" /> <strong>Role-Based Demo Personas (RBAC)</strong><span className="demo-only">ENTERPRISE</span></div>
            <p>Select a persona to test granular permissions and audit logging:</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "8px" }}>
              <button type="button" onClick={() => setAccount("cxo_exec", "Executive2026!")}>CXO Exec</button>
              <button type="button" onClick={() => setAccount("auditor_dan", "Auditor2026!")}>Auditor</button>
              <button type="button" onClick={() => setAccount("qa_analyst", "Quality2026!")}>Quality Lead</button>
              <button type="button" onClick={() => setAccount("operator_line3", "Operator2026!")}>Line Operator</button>
            </div>
          </div>

          <p className="login-help">Need an account? <span>Contact your workspace administrator.</span></p>
        </div>
        <div className="login-panel-bottom"><LockKeyhole size={13} /> Your sign-in is protected by secure token-based access.</div>
      </section>
    </main>
  );
};
