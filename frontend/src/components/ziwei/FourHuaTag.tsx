import type { SiHuaType } from "@/types/ziwei";
import { cn } from "@/lib/utils";

const SIHUA_STYLE: Record<SiHuaType, string> = {
  禄: "border-emerald-400/40 bg-emerald-400/10 text-emerald-300",
  权: "border-purple-400/40 bg-purple-400/10 text-purple-200",
  科: "border-sky-400/40 bg-sky-400/10 text-sky-200",
  忌: "border-rose-400/40 bg-rose-400/10 text-rose-300",
};

interface FourHuaTagProps {
  type: SiHuaType;
  className?: string;
  size?: "sm" | "md";
}

export default function FourHuaTag({ type, className, size = "sm" }: FourHuaTagProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded border font-medium",
        SIHUA_STYLE[type],
        size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs",
        className,
      )}
    >
      化{type}
    </span>
  );
}
