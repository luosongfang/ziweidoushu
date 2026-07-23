"use client";

import { useRouter } from "next/navigation";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import BirthForm from "@/components/ziwei/BirthForm";
import { useChart } from "@/context/ChartContext";
import { SITE } from "@/lib/constants";
import type { ChartCreateResponse } from "@/types/ziwei";

export default function ChartPage() {
  const router = useRouter();
  const { setChart } = useChart();

  const handleSuccess = (data: ChartCreateResponse) => {
    setChart(data);
    router.push("/chart/result");
  };

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-16 pt-24 sm:px-6">
        <div className="mx-auto max-w-3xl text-center">
          <p className="section-label">个人星盘</p>
          <h1 className="mt-3 font-display text-3xl font-bold text-paper sm:text-4xl">
            创建你的个人星盘
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-paper/50 sm:text-base">
            输入出生信息，生成属于你的传统文化分析档案。
          </p>
        </div>
        <div className="mt-10">
          <BirthForm onSuccess={handleSuccess} />
        </div>
        <p className="mx-auto mt-6 max-w-lg text-center text-xs text-paper/35">
          {SITE.notice} 出生信息仅用于生成个人分析。
        </p>
      </main>
      <Footer />
    </>
  );
}
