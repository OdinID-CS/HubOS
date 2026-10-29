import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AlertCircle,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  Mail,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { BrandMark } from "../../components/ui/brand-mark";
import { AuthShell } from "./auth-shell";
import { AuthServiceError, isAuthConfigured, signIn } from "./auth-service";
import { signInSchema, type SignInValues } from "./sign-in-schema";

const REMEMBERED_EMAIL_KEY = "hubos-remembered-email";

function readRememberedEmail(): string {
  try {
    return window.localStorage.getItem(REMEMBERED_EMAIL_KEY) ?? "";
  } catch {
    return "";
  }
}

function persistRememberedEmail(email: string | null) {
  try {
    if (email) {
      window.localStorage.setItem(REMEMBERED_EMAIL_KEY, email);
    } else {
      window.localStorage.removeItem(REMEMBERED_EMAIL_KEY);
    }
  } catch {
    // Storage can be unavailable (private mode); remembering the email is optional.
  }
}

export function SignInPage() {
  const navigate = useNavigate();
  const [initialEmail] = useState(readRememberedEmail);
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInValues>({
    resolver: zodResolver(signInSchema),
    mode: "onTouched",
    defaultValues: {
      email: initialEmail,
      password: "",
      rememberMe: initialEmail.length > 0,
    },
  });

  useEffect(() => {
    document.title = "Sign in · HubOS";
  }, []);

  const onSubmit = handleSubmit(async (values) => {
    setFormError(null);

    try {
      await signIn({ email: values.email, password: values.password });
      persistRememberedEmail(values.rememberMe ? values.email : null);
      navigate("/", { replace: true });
    } catch (error) {
      setFormError(
        error instanceof AuthServiceError
          ? error.message
          : "Something went wrong while signing in. Please try again.",
      );
    }
  });

  return (
    <AuthShell>
      <div className="auth-form-block">
        <Link
          to="/"
          className="auth-brand-link focus-ring"
          aria-label="HubOS home"
        >
          <BrandMark size="sm" />
        </Link>

        <div className="auth-form-head">
          <h1>Welcome back</h1>
          <p>Sign in to continue to your workspace.</p>
        </div>

        <form
          className="auth-form"
          noValidate
          onSubmit={onSubmit}
          onChange={() => {
            if (formError) setFormError(null);
          }}
        >
          {formError ? (
            <div className="auth-alert" role="alert">
              <AlertCircle size={16} aria-hidden="true" />
              <span>
                {formError}
                {!isAuthConfigured && import.meta.env.DEV ? (
                  <span className="auth-alert__meta">
                    Connect the backend endpoint through{" "}
                    <code>VITE_AUTH_API_URL</code> to enable sign-in.
                  </span>
                ) : null}
              </span>
            </div>
          ) : null}

          <div className="auth-field">
            <label className="auth-field__label" htmlFor="signin-email">
              Email address
            </label>
            <div className="auth-input">
              <Mail className="auth-input__icon" size={17} aria-hidden="true" />
              <input
                id="signin-email"
                type="email"
                inputMode="email"
                autoComplete="email"
                placeholder="you@example.com"
                aria-invalid={errors.email ? true : undefined}
                aria-describedby={
                  errors.email ? "signin-email-error" : undefined
                }
                {...register("email")}
              />
            </div>
            {errors.email ? (
              <p
                className="auth-field__error"
                id="signin-email-error"
                role="alert"
              >
                <AlertCircle size={13} aria-hidden="true" />
                {errors.email.message}
              </p>
            ) : null}
          </div>

          <div className="auth-field">
            <label className="auth-field__label" htmlFor="signin-password">
              Password
            </label>
            <div className="auth-input auth-input--password">
              <LockKeyhole
                className="auth-input__icon"
                size={17}
                aria-hidden="true"
              />
              <input
                id="signin-password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                aria-invalid={errors.password ? true : undefined}
                aria-describedby={
                  errors.password ? "signin-password-error" : undefined
                }
                {...register("password")}
              />
              <button
                type="button"
                className="auth-input__toggle"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((visible) => !visible)}
              >
                {showPassword ? (
                  <EyeOff size={17} aria-hidden="true" />
                ) : (
                  <Eye size={17} aria-hidden="true" />
                )}
              </button>
            </div>
            {errors.password ? (
              <p
                className="auth-field__error"
                id="signin-password-error"
                role="alert"
              >
                <AlertCircle size={13} aria-hidden="true" />
                {errors.password.message}
              </p>
            ) : null}
          </div>

          <div className="auth-options">
            <label className="auth-checkbox" htmlFor="signin-remember">
              <input
                id="signin-remember"
                type="checkbox"
                {...register("rememberMe")}
              />
              <span className="auth-checkbox__box" aria-hidden="true">
                <Check size={12} strokeWidth={3} />
              </span>
              <span>Remember me</span>
            </label>
            <Link to="/forgot-password" className="auth-link">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
            aria-busy={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <LoaderCircle className="animate-spin" size={17} aria-hidden="true" />
                Signing in…
              </>
            ) : (
              <>
                Sign in
                <ArrowRight size={17} aria-hidden="true" />
              </>
            )}
          </button>
        </form>

        <p className="auth-support">
          Need help signing in? Contact your hub administrator.
        </p>
      </div>
    </AuthShell>
  );
}
