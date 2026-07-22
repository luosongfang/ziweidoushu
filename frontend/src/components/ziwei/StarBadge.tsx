import { cn } from "@/lib/utils";
import FourHuaTag from "./FourHuaTag";
import type { SiHuaType } from "@/types/ziwei";

export type StarVariant = "main" | "lucky" | "evil" | "aux";

const VARIANT_STYLE: Record<StarVariant, string> = {
  main: "text-gold-light border-gold/30 bg-gold/10",
  lucky: "text-emerald-300 border-emerald-400/30 bg-emerald-400/10",
  evil: "text-rose-300 border-rose-400/30 bg-rose-400/10",
  aux: "text-purple-mist border-purple-glow/20 bg-purple-glow/10",
};

interface StarBadgeProps {
  name: string;
  variant?: StarVariant;
  sihua?: SiHuaType;
  className?: string;
}

export default function StarBadge({
  name,
  variant = "main",
  sihua,
  className,
}: StarBadgeProps) {
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px]", VARIANT_STYLE[variant], className)}>
      {name}
      {sihua && <FourHuaTag type={sihua} />}
    </span>
  );
}

export function starCategoryToVariant(category?: string): StarVariant {
  if (category === "main") return "main";
  if (category === "sha") return "evil";
  if (category === "aux" || category === "za") return "lucky";
  return "aux";
}
