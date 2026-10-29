import type { CSSProperties } from "react";
import markUrl from "../../assets/hubos-mark.png";

const maskStyle: CSSProperties = {
  WebkitMaskImage: `url("${markUrl}")`,
  maskImage: `url("${markUrl}")`,
  WebkitMaskSize: "contain",
  maskSize: "contain",
  WebkitMaskRepeat: "no-repeat",
  maskRepeat: "no-repeat",
  WebkitMaskPosition: "center",
  maskPosition: "center",
};

type BrandGlyphProps = {
  size?: number;
};

export function BrandGlyph({ size = 22 }: BrandGlyphProps) {
  return (
    <span
      aria-hidden="true"
      className="block shrink-0 bg-current"
      style={{ ...maskStyle, width: size, height: size }}
    />
  );
}
