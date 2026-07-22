"use client";

import StarryBackground from "@/components/background/StarryBackground";
import ChartPageHeader from "@/components/chart/ChartPageHeader";
import ChartBoard from "@/components/chart/ChartBoard";
import Button from "@/components/ui/Button";
import type { ChartData } from "@/types/chart";

interface ChartViewProps {
  data: ChartData;
  source?: "engine" | "mock";
}

export default function ChartView({ data, source = "engine" }: ChartViewProps) {
  return (
    <>
      <StarryBackground />
      <ChartPageHeader />

      <main className="mx-auto max-w-5xl px-3 py-6 sm:px-6 sm:py-8">
        <div className="mb-4 flex flex-col gap-3 sm:mb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs tracking-widest text-purple-mist uppercase">Ziwei Chart</p>
            <h2 className="font-display text-xl font-bold text-white sm:text-2xl">
              十二宫命盘
            </h2>
            <p className="mt-1 text-xs text-white/40 sm:text-sm">
              {data.meta.name} · {data.meta.wuxingJu} · 命宫 {data.meta.mingGong}
            </p>
          </div>
          <Button href="#" variant="gold" size="sm">
            AI 解读命盘
          </Button>
        </div>

        <div className="overflow-x-auto pb-2">
          <div className="min-w-[340px]">
            <ChartBoard data={data} />
          </div>
        </div>

        <p className="mt-4 text-center text-[10px] text-white/25 sm:text-xs">
          {source === "engine"
            ? "由紫微AI 排盘引擎实时计算 · 三合派 V1.0"
            : "演示命盘 · 引擎暂不可用"}
        </p>
      </main>
    </>
  );
}
