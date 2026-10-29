import { useEffect, useRef } from "react";
import { Activity, UsersRound, Workflow } from "lucide-react";
import { BrandGlyph } from "../../components/ui/brand-glyph";

export function InnovationShowcase() {
  const stageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;

    const finePointer = window.matchMedia("(pointer: fine)");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (!finePointer.matches || reducedMotion.matches) return;

    const surface = stage.closest(".auth-showcase");
    if (!(surface instanceof HTMLElement)) return;

    let frame = 0;
    let shiftX = 0;
    let shiftY = 0;

    const handlePointerMove = (event: PointerEvent) => {
      const rect = surface.getBoundingClientRect();
      shiftX = Math.max(
        -0.5,
        Math.min(0.5, (event.clientX - rect.left) / rect.width - 0.5),
      );
      shiftY = Math.max(
        -0.5,
        Math.min(0.5, (event.clientY - rect.top) / rect.height - 0.5),
      );

      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        stage.style.setProperty("--shift-x", shiftX.toFixed(3));
        stage.style.setProperty("--shift-y", shiftY.toFixed(3));
      });
    };

    const resetParallax = () => {
      if (frame) {
        window.cancelAnimationFrame(frame);
        frame = 0;
      }
      stage.style.setProperty("--shift-x", "0");
      stage.style.setProperty("--shift-y", "0");
    };

    surface.addEventListener("pointermove", handlePointerMove);
    surface.addEventListener("pointerleave", resetParallax);

    return () => {
      surface.removeEventListener("pointermove", handlePointerMove);
      surface.removeEventListener("pointerleave", resetParallax);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <div className="core-stage" ref={stageRef} aria-hidden="true">
      <div className="core-glow core-glow--blue" />
      <div className="core-glow core-glow--cyan" />

      <div className="core-depth core-depth--far">
        <svg className="core-rings" viewBox="0 0 560 560" fill="none">
          <defs>
            <linearGradient
              id="hubos-ring-stroke"
              x1="80"
              y1="140"
              x2="500"
              y2="460"
              gradientUnits="userSpaceOnUse"
            >
              <stop stopColor="#38bdf8" stopOpacity="0.5" />
              <stop offset="0.48" stopColor="#60a5fa" stopOpacity="0.16" />
              <stop offset="1" stopColor="#818cf8" stopOpacity="0.46" />
            </linearGradient>
            <radialGradient id="hubos-core-wash">
              <stop stopColor="#38bdf8" stopOpacity="0.16" />
              <stop offset="1" stopColor="#38bdf8" stopOpacity="0" />
            </radialGradient>
          </defs>

          <circle cx="280" cy="280" r="182" fill="url(#hubos-core-wash)" />

          <g className="core-ring core-ring--outer">
            <ellipse
              cx="280"
              cy="280"
              rx="252"
              ry="104"
              transform="rotate(-16 280 280)"
              stroke="url(#hubos-ring-stroke)"
              strokeWidth="1"
              strokeDasharray="2 10"
              strokeLinecap="round"
            />
          </g>
          <g className="core-ring core-ring--mid">
            <ellipse
              cx="280"
              cy="280"
              rx="206"
              ry="82"
              transform="rotate(26 280 280)"
              stroke="url(#hubos-ring-stroke)"
              strokeWidth="1"
              opacity="0.8"
            />
          </g>
          <g className="core-ring core-ring--inner">
            <ellipse
              cx="280"
              cy="280"
              rx="158"
              ry="60"
              transform="rotate(-4 280 280)"
              stroke="url(#hubos-ring-stroke)"
              strokeWidth="1"
              strokeDasharray="1 8"
              strokeLinecap="round"
            />
          </g>

          <g className="core-sparkles" fill="#93c5fd">
            <circle cx="152" cy="118" r="1.6" />
            <circle cx="428" cy="302" r="1.9" />
            <circle cx="336" cy="472" r="1.4" />
            <circle cx="208" cy="336" r="1.6" />
            <circle cx="470" cy="122" r="1.2" />
          </g>
        </svg>
      </div>

      <div className="core-depth core-depth--near">
        <svg className="core-links" viewBox="0 0 560 560" fill="none">
          <defs>
            <linearGradient
              id="hubos-link-stroke"
              x1="280"
              y1="280"
              x2="462"
              y2="198"
              gradientUnits="userSpaceOnUse"
            >
              <stop stopColor="#7dd3fc" stopOpacity="0.55" />
              <stop offset="1" stopColor="#60a5fa" stopOpacity="0.1" />
            </linearGradient>
          </defs>

          <g
            stroke="url(#hubos-link-stroke)"
            strokeWidth="1"
            strokeLinecap="round"
          >
            <path d="M280 280 C 228 240, 176 208, 118 176" />
            <path d="M280 280 C 340 244, 408 218, 462 198" />
            <path d="M280 280 C 248 330, 214 388, 180 438" />
          </g>

          <g className="core-link-dots" fill="#7dd3fc">
            <circle cx="118" cy="176" r="2.6" />
            <circle cx="462" cy="198" r="2.6" />
            <circle cx="180" cy="438" r="2.6" />
          </g>
        </svg>

        <div className="core-orb">
          <span className="core-orb__halo" />
          <span className="core-orb__frame">
            <span className="core-orb__icon">
              <BrandGlyph size={30} />
            </span>
            <span className="core-orb__name">HubOS</span>
            <span className="core-orb__caption">Innovation core</span>
          </span>
          <span className="core-orb__orbit" />
        </div>

        <div className="core-node core-node--projects">
          <Workflow size={18} strokeWidth={1.7} />
        </div>
        <div className="core-node core-node--teams">
          <UsersRound size={18} strokeWidth={1.7} />
        </div>
        <div className="core-node core-node--signals">
          <Activity size={18} strokeWidth={1.7} />
        </div>
      </div>
    </div>
  );
}
