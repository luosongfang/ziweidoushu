"use client";

import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
import StarryBackground from "@/components/background/StarryBackground";
import Header from "@/components/layout/Header";
import BirthForm from "@/components/ziwei/BirthForm";
import { useChart } from "@/context/ChartContext";
import type { ChartCreateResponse } from "@/types/ziwei";

export default function ChartInputPage() {
  const router = useRouter();
  const { setChart } = useChart();

  const handleSuccess = (data: ChartCreateResponse) => {
    setChart(data);
    router.push("/chart/result");
  };

  return (
    <>
      <StarryBackground />
      <Header />
      <main className="min-h-screen px-4 pb-16 pt-24 sm:px-6">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-purple-glow/30 bg-purple-glow/10 px-4 py-1.5 text-xs text-purple-mist">
            <Sparkles className="h-3.5 w-3.5" />
            Phase 2 Engine · 实时排盘
          </div>
          <h1 className="font-display text-3xl font-bold text-white sm:text-4xl">
            生成你的<span className="text-gradient-gold">紫微命盘</span>
          </h1>
          <p className="mt-3 text-sm text-white/50 sm:text-base">
            填写出生信息，连接 FastAPI 排盘引擎，获取十二宫完整星曜布局
          </p>
        </div>
        <div className="mt-10">
          <BirthForm onSuccess={handleSuccess} />
        </div>
      </main>
    </>
  );
}
