import { BrandGlyph } from "./brand-glyph";

type BrandMarkProps = {
  onDark?: boolean;
  size?: "sm" | "md";
};

export function BrandMark({ onDark = false, size = "md" }: BrandMarkProps) {
  const classes = ["brand-lockup"];
  if (size === "sm") classes.push("brand-lockup--sm");
  if (onDark) classes.push("brand-lockup--on-dark");

  return (
    <span className={classes.join(" ")}>
      <span className="brand-lockup__tile" aria-hidden="true">
        <BrandGlyph size={size === "sm" ? 21 : 23} />
      </span>
      <span className="brand-lockup__text">
        <span className="brand-lockup__name">HubOS</span>
        <span className="brand-lockup__tagline">K-Innovation Hub</span>
      </span>
    </span>
  );
}
