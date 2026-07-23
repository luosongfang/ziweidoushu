import type { Palace } from "@/types/chart";
import StarLine from "./StarLine";

interface PalaceCellProps {
  palace: Palace;
  isActive?: boolean;
}

export default function PalaceCell({ palace, isActive = false }: PalaceCellProps) {
  const hasMainStars = palace.mainStars.length > 0;
  const shaStars = palace.shaStars ?? [];

  return (
    <div
      className={`relative flex h-full min-h-[96px] flex-col rounded-lg border transition-all duration-200 sm:min-h-[118px] ${
        palace.isMingGong
          ? "border-gold/50 bg-gold/[0.06] shadow-glow-gold"
          : palace.isShenGong
            ? "border-purple-glow/40 bg-purple-glow/[0.04]"
            : isActive
              ? "border-purple-glow/30 bg-purple-glow/[0.06]"
              : "border-white/[0.08] bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.04]"
      }`}
    >
      <div className="flex items-center justify-between border-b border-white/[0.06] px-1.5 py-1 sm:px-2 sm:py-1.5">
        <div className="flex min-w-0 flex-1 items-center gap-1">
          <span
            className={`truncate text-[11px] font-semibold sm:text-xs ${
              palace.isMingGong ? "text-gold-light" : "text-white/80"
            }`}
          >
            {palace.name}
          </span>
          {palace.isMingGong && (
            <span className="shrink-0 rounded bg-gold/20 px-1 text-[8px] text-gold sm:text-[9px]">命</span>
          )}
          {palace.isShenGong && (
            <span className="shrink-0 rounded bg-purple-glow/20 px-1 text-[8px] text-purple-mist sm:text-[9px]">
              身
            </span>
          )}
        </div>
        <div className="shrink-0 text-right leading-none">
          <span className="font-display text-sm font-bold text-gold/70 sm:text-base">{palace.branch}</span>
          {palace.ganzhi && (
            <div className="text-[9px] text-white/35 sm:text-[10px]">{palace.ganzhi}</div>
          )}
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-1 px-1.5 py-1 sm:gap-1.5 sm:px-2 sm:py-1.5">
        <div className="flex flex-wrap gap-x-1.5 gap-y-0.5">
          {hasMainStars ? (
            palace.mainStars.map((star) => (
              <StarLine key={star.name} star={star} variant="main" />
            ))
          ) : (
            <span className="text-[10px] text-white/20">无主星</span>
          )}
        </div>

        {palace.auxStars.length > 0 && (
          <div className="flex flex-wrap gap-x-1.5 gap-y-0.5 border-t border-white/[0.04] pt-1">
            {palace.auxStars.map((star) => (
              <StarLine key={star.name} star={star} variant="aux" />
            ))}
          </div>
        )}

        {shaStars.length > 0 && (
          <div className="flex flex-wrap gap-x-1.5 gap-y-0.5 border-t border-rose-400/10 pt-1">
            {shaStars.map((star) => (
              <StarLine key={star.name} star={star} variant="aux" />
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-white/[0.06] px-1.5 py-0.5 sm:px-2 sm:py-1">
        <span className="text-[9px] text-white/30 sm:text-[10px]">
          大限 {palace.daxian.startAge}–{palace.daxian.endAge}
        </span>
      </div>
    </div>
  );
}
