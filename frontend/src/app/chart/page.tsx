"use client";

import { useRouter } from "next/navigation";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import BirthForm from "@/components/ziwei/BirthForm";
import { useChart } from "@/context/ChartContext";
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
          <p className="section-label">基础排盘</p>
          <h1 className="mt-3 font-display text-3xl font-bold text-paper sm:text-4xl">
            生成我的命盘
          </h1>
          <p className="mt-3 text-sm text-paper/50 sm:text-base">
            填写出生信息，生成十二宫结构、十四主星与四化。结果用于自我认知与人生规划参考。
          </p>
        </div>
        <div className="mt-10">
          <BirthForm onSuccess={handleSuccess} />
        </div>
      </main>
      <Footer />
    </>
  );
}
