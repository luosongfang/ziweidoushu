import Link from "next/link";
import { Button } from "@/components/ui/Button";
import type { ChartCreateResponse } from "@/types/ziwei";

interface ChartCardProps {
  chart: ChartCreateResponse;
  compact?: boolean;
}

/** 命盘摘要卡片 — 用于结果页与档案页 */
export default function ChartCard({ chart, compact = false }: ChartCardProps) {
  const { birth, meta } = chart;
  const shichen = typeof birth.shichen === "string" ? birth.shichen : birth.shichen.name;
  return (
    <div className="surface-panel p-5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="section-label">命盘摘要</p>
          <h2 className="mt-2 font-display text-2xl font-semibold text-paper">
            {chart.name || "访客命盘"}
          </h2>
          <p className="mt-1 text-sm text-paper/50">
            {chart.gender === "male" ? "男" : "女"} · {shichen} · {birth.solar}
          </p>
        </div>
        <div className={`grid gap-2 text-sm ${compact ? "grid-cols-2" : "grid-cols-2 sm:grid-cols-4"}`}>
          <Meta label="农历" value={birth.lunar} />
          <Meta label="命宫" value={meta.mingGong} accent />
          <Meta label="五行局" value={meta.wuxingJu} />
          <Meta
            label="四柱"
            value={`${birth.ganzhi.year_gan}${birth.ganzhi.year_zhi}`}
          />
        </div>
      </div>
      {!compact && (
        <div className="mt-5 flex flex-wrap gap-3">
          <Button href="/analysis" variant="gold" size="md">
            开始 AI 分析解读
          </Button>
          <Button href="/chart" variant="outline" size="md">
            重新排盘
          </Button>
          <Link href="/advisor" className="text-sm text-gold/80 underline-offset-4 hover:underline">
            向人生导师提问 →
          </Link>
        </div>
      )}
    </div>
  );
}

function Meta({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-xl border border-paper/10 bg-ink/50 px-3 py-2">
      <div className="text-[11px] text-paper/40">{label}</div>
      <div className={`mt-0.5 font-medium ${accent ? "text-gold-light" : "text-paper/85"}`}>
        {value}
      </div>
    </div>
  );
}
