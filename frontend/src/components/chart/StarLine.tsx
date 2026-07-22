import type { Star } from "@/types/chart";
import { BRIGHTNESS_STYLE } from "@/lib/chartLayout";
import SiHuaBadge from "./SiHuaBadge";

interface StarLineProps {
  star: Star;
  variant?: "main" | "aux";
}

export default function StarLine({ star, variant = "main" }: StarLineProps) {
  const brightnessClass =
    star.brightness && BRIGHTNESS_STYLE[star.brightness]
      ? BRIGHTNESS_STYLE[star.brightness]
      : variant === "main"
        ? "text-white/80"
        : "text-white/45";

  return (
    <span className="inline-flex items-center gap-0.5 leading-tight">
      <span
        className={`whitespace-nowrap ${brightnessClass} ${
          variant === "main" ? "text-[11px] font-medium sm:text-xs" : "text-[10px] sm:text-[11px]"
        }`}
      >
        {star.name}
        {star.brightness && (
          <span className="ml-0.5 text-[9px] opacity-60">{star.brightness}</span>
        )}
      </span>
      {star.sihua && <SiHuaBadge type={star.sihua} compact />}
    </span>
  );
}
