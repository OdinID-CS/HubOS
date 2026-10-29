import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { BrandMark } from "../../components/ui/brand-mark";
import { ThemeToggle } from "../../components/ui/theme-toggle";
import { InnovationShowcase } from "./innovation-showcase";
import "./auth.css";

type AuthShellProps = {
  children: ReactNode;
  showThemeToggle?: boolean;
};

export function AuthShell({
  children,
  showThemeToggle = true,
}: AuthShellProps) {
  return (
    <div className="auth-page">
      <aside className="auth-showcase">
        <div className="auth-showcase__ambient" aria-hidden="true" />

        <header className="auth-showcase__header">
          <Link
            to="/"
            className="auth-brand-link focus-ring"
            aria-label="HubOS home"
          >
            <BrandMark onDark />
          </Link>
        </header>

        <div className="auth-showcase__visual">
          <InnovationShowcase />
        </div>

        <div className="auth-showcase__copy">
          <p className="showcase-kicker">
            <span>Innovation</span>
            <span aria-hidden="true">•</span>
            <span>Collaboration</span>
            <span aria-hidden="true">•</span>
            <span>Impact</span>
          </p>
          <p className="showcase-headline">
            Great ideas deserve a place to <span>become reality.</span>
          </p>
          <p className="showcase-description">
            Connect your team, manage your projects, and turn innovation into
            measurable impact.
          </p>
        </div>
      </aside>

      <main className="auth-panel">
        {showThemeToggle ? (
          <div className="auth-panel__bar">
            <ThemeToggle />
          </div>
        ) : null}

        <div className="auth-panel__body">{children}</div>

        <footer className="auth-panel__footer">
          <span>HubOS · Innovation Hub Management Platform</span>
          <Link to="/" className="auth-link">
            Back to home
          </Link>
        </footer>
      </main>
    </div>
  );
}
