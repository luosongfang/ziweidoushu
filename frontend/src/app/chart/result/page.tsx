"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ChartCard from "@/components/ChartCard";
import ZiweiChart from "@/components/ziwei/ZiweiChart";
import { Button } from "@/components/ui/Button";
import { useChart } from "@/context/ChartContext";

const TABS = [
  { id: "map", label: "命盘图" },
  { id: "stage", label: "当前阶段" },
  { id: "modern", label: "现代解读提示" },
] as const;

export default function ChartResultPage() {
  const router = useRouter();
  const { chart, isHydrated } = useChart();
  const [tab, setTab] = useState<(typeof TABS)[number]["id"]>("map");

  useEffect(() => {
    if (isHydrated && !chart) router.replace("/chart");
  }, [chart, isHydrated, router]);

  if (!isHydrated || !chart) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ink">
        <Loader2 className="h-8 w-8 animate-spin text-gold" />
      </div>
    );
  }

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl space-y-6">
          <ChartCard chart={chart} />

          <div className="flex flex-wrap gap-2">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={`rounded-full px-4 py-1.5 text-sm transition ${
                  tab === t.id
                    ? "bg-gold text-ink"
                    : "border border-paper/15 text-paper/60 hover:border-gold/40"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "map" && (
            <div className="surface-panel p-3 sm:p-5">
              <ZiweiChart data={chart} />
            </div>
          )}
          {tab === "stage" && (
            <div className="surface-panel p-6 text-sm leading-relaxed text-paper/70">
              当前阶段信息可在「AI 解盘」中结合大限与知识库进一步展开。此处仅展示命盘结构，不作运势断言。
              <div className="mt-4">
                <Button href="/analysis" variant="gold">
                  开始 AI 分析解读
                </Button>
              </div>
            </div>
          )}
          {tab === "modern" && (
            <div className="surface-panel p-6 text-sm leading-relaxed text-paper/70">
              现代解读将紫微术语转化为可执行的自我认知语言：优势、节奏、风险边界与成长动作。完整模块见分析页。
              <div className="mt-4">
                <Button href="/analysis" variant="outline">
                  进入六大分析模块
                </Button>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
