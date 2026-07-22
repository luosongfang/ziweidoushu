"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, FileText, Loader2 } from "lucide-react";
import StarryBackground from "@/components/background/StarryBackground";
import ZiweiChart from "@/components/ziwei/ZiweiChart";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/card";
import { useChart } from "@/context/ChartContext";

export default function ChartResultPage() {
  const router = useRouter();
  const { chart, isHydrated } = useChart();

  useEffect(() => {
    if (isHydrated && !chart) {
      router.replace("/chart");
    }
  }, [chart, isHydrated, router]);

  if (!isHydrated || !chart) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-void">
        <Loader2 className="h-8 w-8 animate-spin text-purple-mist" />
      </div>
    );
  }

  const { birth } = chart;

  return (
    <>
      <StarryBackground />
      <main className="min-h-screen px-4 pb-20 pt-8 sm:px-6 sm:pt-12">
        <div className="mx-auto max-w-5xl">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <Button href="/chart" variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4" />
              重新排盘
            </Button>
            <Link href="/report">
              <Button variant="gold" size="lg">
                <FileText className="h-4 w-4" />
                生成 AI 分析报告
              </Button>
            </Link>
          </div>

          {/* 用户信息摘要 */}
          <Card className="mb-8 border-gold/20 bg-gradient-to-br from-purple-deep/20 to-transparent">
            <CardContent className="p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h1 className="font-display text-2xl font-bold text-white">{chart.name}</h1>
                  <p className="mt-1 text-sm text-white/50">
                    {chart.gender === "male" ? "男" : "女"} · {birth.shichen}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                  <InfoChip label="农历" value={birth.lunar} />
                  <InfoChip label="四柱" value={`${birth.ganzhi.year_gan}${birth.ganzhi.year_zhi} ${birth.ganzhi.month_gan}${birth.ganzhi.month_zhi}`} />
                  <InfoChip label="命宫" value={chart.chart.ming_gong} highlight />
                  <InfoChip label="五行局" value={chart.chart.five_element} />
                </div>
              </div>
              {chart.persisted === false && (
                <p className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
                  命盘未写入数据库。请检查 backend/.env 中的 DATABASE_URL 是否已配置 Supabase 密码。
                </p>
              )}
              {chart.persisted && chart.chart_id && (
                <p className="mt-4 text-xs text-white/40">
                  已保存至 Supabase · chart_id: {chart.chart_id.slice(0, 8)}…
                </p>
              )}
            </CardContent>
          </Card>

          <ZiweiChart data={chart} />
        </div>
      </main>
    </>
  );
}

function InfoChip({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2">
      <div className="text-[10px] text-white/40">{label}</div>
      <div className={`mt-0.5 text-xs font-medium ${highlight ? "text-gold-light" : "text-white/80"}`}>
        {value}
      </div>
    </div>
  );
}
