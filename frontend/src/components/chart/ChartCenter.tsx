import type { ChartMeta } from "@/types/chart";

interface ChartCenterProps {
  meta: ChartMeta;
}

export default function ChartCenter({ meta }: ChartCenterProps) {
  const genderLabel = meta.gender === "male" ? "男" : "女";

  return (
    <div className="flex h-full flex-col items-center justify-center rounded-xl border border-white/10 bg-void-100/80 p-3 backdrop-blur-sm sm:p-4">
      {/* 标题 */}
      <div className="mb-2 text-center">
        <h2 className="font-display text-sm font-bold text-gradient-gold sm:text-base">
          {meta.name}
        </h2>
        <p className="mt-0.5 text-[10px] text-white/40 sm:text-xs">
          {meta.wuxingJu} · {genderLabel}
        </p>
      </div>

      {/* 出生信息 */}
      <div className="w-full space-y-1 border-t border-white/[0.06] pt-2 text-center">
        <InfoRow label="公历" value={meta.birthDate} />
        <InfoRow label="农历" value={meta.lunarDate} />
        <InfoRow label="时辰" value={meta.birthTime} />
      </div>

      {/* 四柱 */}
      <div className="mt-2 grid w-full grid-cols-4 gap-1 border-t border-white/[0.06] pt-2">
        {[
          { label: "年", value: meta.yearStemBranch },
          { label: "月", value: meta.monthStemBranch },
          { label: "日", value: meta.dayStemBranch },
          { label: "时", value: meta.hourStemBranch },
        ].map((item) => (
          <div key={item.label} className="text-center">
            <div className="text-[9px] text-white/30">{item.label}</div>
            <div className="font-display text-[11px] font-medium text-gold/80 sm:text-xs">
              {item.value}
            </div>
          </div>
        ))}
      </div>

      {/* 命主身主 */}
      <div className="mt-2 flex w-full gap-2 border-t border-white/[0.06] pt-2">
        <div className="flex-1 rounded-lg border border-gold/20 bg-gold/5 py-1.5 text-center">
          <div className="text-[9px] text-white/30">命宫</div>
          <div className="text-xs font-medium text-gold-light">{meta.mingGong}</div>
        </div>
        <div className="flex-1 rounded-lg border border-purple-glow/20 bg-purple-glow/5 py-1.5 text-center">
          <div className="text-[9px] text-white/30">身宫</div>
          <div className="text-xs font-medium text-purple-mist">{meta.shenGong}</div>
        </div>
        <div className="flex-1 rounded-lg border border-white/10 bg-white/[0.03] py-1.5 text-center">
          <div className="text-[9px] text-white/30">命主</div>
          <div className="text-xs font-medium text-white/70">{meta.mingZhu}</div>
        </div>
        <div className="flex-1 rounded-lg border border-white/10 bg-white/[0.03] py-1.5 text-center">
          <div className="text-[9px] text-white/30">身主</div>
          <div className="text-xs font-medium text-white/70">{meta.shenZhu}</div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-2 text-[10px] sm:text-[11px]">
      <span className="shrink-0 text-white/30">{label}</span>
      <span className="truncate text-white/60">{value}</span>
    </div>
  );
}
