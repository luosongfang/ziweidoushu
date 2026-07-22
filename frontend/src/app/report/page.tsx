"use client";

import { useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Brain, Loader2, Sparkles } from "lucide-react";
import StarryBackground from "@/components/background/StarryBackground";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useChart } from "@/context/ChartContext";
import { buildReportSections } from "@/lib/reportGenerator";

export default function ReportPage() {
  const router = useRouter();
  const { chart, isHydrated } = useChart();

  const sections = useMemo(
    () => (chart ? buildReportSections(chart) : []),
    [chart],
  );

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

  return (
    <>
      <StarryBackground />
      <main className="min-h-screen px-4 pb-20 pt-8 sm:px-6 sm:pt-12">
        <div className="mx-auto max-w-3xl">
          <div className="mb-8 text-center">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-purple-glow/30 bg-purple-glow/10 px-4 py-1.5 text-xs text-purple-mist">
              <Brain className="h-3.5 w-3.5" />
              AI 人生分析报告
            </div>
            <h1 className="font-display text-3xl font-bold text-white">
              {chart.name} 的命盘解读
            </h1>
            <p className="mt-2 text-sm text-white/50">
              基于 Phase 2 排盘引擎真实数据 · 规则驱动分析 · 非随机生成
            </p>
          </div>

          <div className="space-y-4">
            {sections.map((section, i) => (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
              >
                <Card className="border-white/10 hover:border-purple-glow/30 transition-colors">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Sparkles className="h-4 w-4 text-gold" />
                      {section.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed text-white/70">{section.content}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Button href="/chart/result" variant="outline">
              返回命盘
            </Button>
            <Button href="/chart" variant="gold">
              重新排盘
            </Button>
          </div>

          <p className="mt-8 text-center text-xs text-white/30">
            以上解读基于三合紫微规则引擎，仅供文化研究与自我参考，不构成决策建议。
          </p>
        </div>
      </main>
    </>
  );
}
