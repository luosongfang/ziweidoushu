"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Palace } from "@/types/ziwei";
import StarBadge, { starCategoryToVariant } from "./StarBadge";

interface PalaceCardProps {
  palace: Palace;
  index: number;
  angle: number;
  radius: number;
  selected?: boolean;
  onSelect?: (palace: Palace) => void;
  compact?: boolean;
}

export default function PalaceCard({
  palace,
  index,
  angle,
  radius,
  selected,
  onSelect,
  compact = false,
}: PalaceCardProps) {
  const rad = (angle * Math.PI) / 180;
  const x = Math.cos(rad) * radius;
  const y = Math.sin(rad) * radius;

  const mainStars = palace.stars.filter((s) => s.category === "main" || !s.category);
  const otherStars = palace.stars.filter((s) => s.category && s.category !== "main" && s.category !== "daxian");

  return (
    <motion.button
      type="button"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.04, duration: 0.35 }}
      whileHover={{ scale: 1.08, zIndex: 20 }}
      onClick={() => onSelect?.(palace)}
      className={cn(
        "absolute left-1/2 top-1/2 text-left transition-shadow",
        compact ? "w-[88px]" : "w-[108px]",
      )}
      style={{
        transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
      }}
    >
      <div
        className={cn(
          "rounded-xl border p-2 backdrop-blur-md transition-all",
          palace.is_ming_gong
            ? "border-gold/50 bg-gold/[0.08] shadow-glow-gold"
            : palace.is_shen_gong
              ? "border-purple-glow/40 bg-purple-glow/[0.06]"
              : "border-white/10 bg-void-100/80",
          selected && "ring-2 ring-purple-glow/60",
        )}
      >
        <div className="mb-1 flex items-center justify-between gap-1">
          <span className={cn("text-xs font-semibold", palace.is_ming_gong ? "text-gold-light" : "text-white/90")}>
            {palace.name}
          </span>
          <span className="font-display text-sm font-bold text-gold/70">{palace.branch}</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {mainStars.length > 0 ? (
            mainStars.slice(0, compact ? 2 : 4).map((star) => (
              <StarBadge
                key={star.name}
                name={star.name}
                variant={starCategoryToVariant(star.category)}
                sihua={star.sihua}
              />
            ))
          ) : (
            <span className="text-[10px] text-white/25">无主星</span>
          )}
        </div>
        {!compact && otherStars.length > 0 && (
          <div className="mt-1 flex flex-wrap gap-1 border-t border-white/5 pt-1">
            {otherStars.slice(0, 3).map((star) => (
              <StarBadge
                key={star.name}
                name={star.name}
                variant={starCategoryToVariant(star.category)}
                sihua={star.sihua}
              />
            ))}
          </div>
        )}
      </div>
    </motion.button>
  );
}
