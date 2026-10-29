import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import {
  ArrowRight,
  ShieldCheck,
  UsersRound,
  Workflow,
} from "lucide-react";
import { BrandGlyph } from "../components/ui/brand-glyph";
import { ForgotPasswordPage } from "../features/auth/forgot-password-page";
import { SignInPage } from "../features/auth/sign-in-page";
import humanRobotImage from "../assets/human-robot-collaboration.png";

const capabilities = [
  {
    number: "01",
    icon: Workflow,
    title: "Project portfolio",
    description:
      "Bring initiatives, milestones, and delivery signals into one clear view.",
  },
  {
    number: "02",
    icon: UsersRound,
    title: "Team collaboration",
    description:
      "Keep ownership visible and help multidisciplinary teams move in sync.",
  },
  {
    number: "03",
    icon: ShieldCheck,
    title: "Executive oversight",
    description:
      "Make confident decisions with transparent reviews and hub-wide context.",
  },
];

function HomePage() {
  return (
    <main className="min-h-screen px-5 py-5 text-foreground sm:px-8 sm:py-7">
      <header className="glass-panel mx-auto flex max-w-7xl items-center justify-between rounded-2xl px-4 py-3 sm:px-5">
        <a
          href="/"
          aria-label="HubOS home"
          className="focus-ring flex items-center gap-3 rounded-xl"
        >
          <span className="grid size-10 place-items-center rounded-xl border border-primary/25 bg-primary/10 text-primary">
            <BrandGlyph size={24} />
          </span>
          <span>
            <span className="block text-base font-semibold tracking-tight">
              HubOS
            </span>
            <span className="brand-caption block text-[11px] tracking-wide text-muted">
              K-Innovation Hub
            </span>
          </span>
        </a>

        <nav aria-label="Main navigation" className="flex items-center gap-3">
          <Link
            to="/login"
            className="focus-ring inline-flex rounded-lg px-2 py-2 text-xs text-muted transition hover:text-foreground sm:px-3 sm:text-sm"
          >
            Sign in
          </Link>
          <a
            href="#overview"
            className="focus-ring hidden items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-background shadow-lg shadow-primary/15 transition hover:bg-primary-hover sm:inline-flex"
          >
            Explore HubOS
            
          </a>
        </nav>
      </header>

      <section
        id="overview"
        className="mx-auto grid max-w-7xl items-center gap-14 pb-20 pt-16 sm:pb-28 sm:pt-24 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16"
      >
        <div>
          <h1 className="max-w-3xl text-4xl font-semibold leading-[1.12] tracking-tight sm:text-6xl lg:text-[4.25rem]">
            Turn ambitious ideas into{" "}
            <span className="text-primary">measurable impact.</span>
          </h1>

          <p className="mt-6 max-w-2xl text-base leading-7 text-muted sm:text-lg sm:leading-8">
            A connected workspace to manage innovation projects, align teams,
            track resources, and move decisions forward with confidence.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-4">
            <a
              href="#capabilities"
              className="focus-ring inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-3 font-semibold text-background shadow-lg shadow-primary/20 transition hover:bg-primary-hover"
            >
              Explore the workspace
              <ArrowRight aria-hidden="true" size={17} />
            </a>
            <a
              href="#capabilities"
              className="focus-ring rounded-xl px-4 py-3 text-sm font-medium text-muted transition hover:text-foreground"
            >
              Discover the platform
            </a>
          </div>

          <div className="mt-10 flex items-center gap-3 text-sm text-muted">
            <span className="flex -space-x-2" aria-hidden="true">
              <span className="grid size-8 place-items-center rounded-full border-2 border-background bg-primary/20 text-xs font-semibold text-primary">
                E
              </span>
              <span className="grid size-8 place-items-center rounded-full border-2 border-background bg-accent/15 text-xs font-semibold text-accent">
                P
              </span>
              <span className="grid size-8 place-items-center rounded-full border-2 border-background bg-success/15 text-xs font-semibold text-success">
                T
              </span>
            </span>
            <span>Designed for teams building what’s next</span>
          </div>
        </div>

        <div className="relative">
          <div
            aria-hidden="true"
            className="absolute inset-[8%] rounded-full bg-primary/10 blur-3xl"
          />
          <div
            aria-hidden="true"
            className="absolute left-1/2 top-1/2 size-28 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent/25 blur-3xl"
          />
          <img
            src={humanRobotImage}
            alt="A human hand and a robotic hand reaching toward each other, fingertips almost touching."
            width={447}
            height={381}
            decoding="async"
            className="relative mx-auto w-full max-w-[600px]"
            style={{
              maskImage:
                "linear-gradient(to right, transparent, #000 14%, #000 86%, transparent), linear-gradient(to bottom, transparent, #000 12%, #000 88%, transparent)",
              WebkitMaskImage:
                "linear-gradient(to right, transparent, #000 14%, #000 86%, transparent), linear-gradient(to bottom, transparent, #000 12%, #000 88%, transparent)",
              maskComposite: "intersect",
              WebkitMaskComposite: "source-in",
            }}
          />
        </div>
      </section>

      <section
        id="capabilities"
        className="mx-auto max-w-7xl scroll-mt-8 pb-20 sm:pb-28"
      >
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-accent">
              Built for meaningful progress
            </p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
              Everything moving in one direction.
            </h2>
          </div>
          <p className="max-w-md text-sm leading-6 text-muted">
            Connect the people, priorities, and decisions behind your next
            breakthrough.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {capabilities.map(({ number, icon: Icon, title, description }) => (
            <article
              key={number}
              className="glass-card rounded-2xl p-6 sm:p-7"
            >
              <div className="flex items-center justify-between">
                <span className="grid size-11 place-items-center rounded-xl border border-primary/20 bg-primary/10 text-primary">
                  <Icon aria-hidden="true" size={21} />
                </span>
                <span className="text-xs font-medium tracking-wide text-muted">
                  {number}
                </span>
              </div>
              <h3 className="mt-7 text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">
                {description}
              </p>
            </article>
          ))}
        </div>
      </section>

      <footer className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 border-t border-border py-6 text-xs text-muted">
        <span>HubOS · Innovation Hub Management Platform</span>
        <span>Clarity for the work that moves us forward.</span>
      </footer>
    </main>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<SignInPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
