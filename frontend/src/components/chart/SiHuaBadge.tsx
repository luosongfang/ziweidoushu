import type { SiHuaType } from "@/types/chart";
import { SIHUA_COLORS } from "@/lib/chartLayout";

interface SiHuaBadgeProps {
  type: SiHuaType;
  compact?: boolean;
}

export default function SiHuaBadge({ type, compact = false }: SiHuaBadgeProps) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded border font-medium ${SIHUA_COLORS[type]} ${
        compact ? "h-3.5 min-w-[14px] px-0.5 text-[9px]" : "h-4 min-w-[16px] px-1 text-[10px]"
      }`}
    >
      {type}
    </span>
  );
}
