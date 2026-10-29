import { useEffect } from "react";
import { ArrowLeft, KeyRound } from "lucide-react";
import { Link } from "react-router-dom";
import { BrandMark } from "../../components/ui/brand-mark";
import { AuthShell } from "./auth-shell";

export function ForgotPasswordPage() {
  useEffect(() => {
    document.title = "Password recovery · HubOS";
  }, []);

  return (
    <AuthShell showThemeToggle={false}>
      <div className="auth-form-block">
        <Link
          to="/"
          className="auth-brand-link focus-ring"
          aria-label="HubOS home"
        >
          <BrandMark size="sm" />
        </Link>

        <div className="auth-form-head">
          <h1>Reset your password</h1>
          <p>Password recovery is not available yet.</p>
        </div>

        <div className="auth-notice">
          <span className="auth-notice__icon" aria-hidden="true">
            <KeyRound size={18} strokeWidth={1.7} />
          </span>
          <div>
            <p className="auth-notice__title">
              A placeholder screen, not a working recovery service
            </p>
            <p className="auth-notice__text">
              Once HubOS exposes a password recovery endpoint, this screen will
              send a secure reset link to your email address. For now, ask your
              hub administrator to restore your access.
            </p>
          </div>
        </div>

        <Link to="/login" className="auth-submit">
          <ArrowLeft size={17} aria-hidden="true" />
          Back to sign in
        </Link>
      </div>
    </AuthShell>
  );
}
