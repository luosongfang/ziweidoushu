"use client";

import { useEffect, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Lock } from "lucide-react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import PrivacyNotice from "@/components/PrivacyNotice";
import ZiweiChart from "@/components/ziwei/ZiweiChart";
import { Button } from "@/components/ui/Button";
import { useChart } from "@/context/ChartContext";
import { useAuth } from "@/contexts/AuthContext";
import { useMembership } from "@/context/MembershipContext";
import { buildChartInsights } from "@/lib/chartInsights";
import { saveLocalAnalysisHistory } from "@/lib/analysisHistory";
import { saveAnalysisSnapshot, saveChart } from "@/services/chartService";
import { SITE } from "@/lib/constants";

function Section({
  title,
  children,
  locked,
}: {
  title: string;
  children: React.ReactNode;
  locked?: boolean;
}) {
  return (
    <section className="surface-panel overflow-hidden p-5 sm:p-6">
      <h2 className="font-display text-lg font-semibold text-paper sm:text-xl">{title}</h2>
      <div className={`mt-4 ${locked ? "relative" : ""}`}>
        {locked && (
          <div className="pointer-events-none absolute inset-0 z-10 rounded-xl bg-gradient-to-b from-transparent via-ink/60 to-ink/95" />
        )}
        {children}
      </div>
    </section>
  );
}

export default function ChartResultPage() {
  const router = useRouter();
  const { chart, isHydrated, setChart } = useChart();
  const { isAuthenticated, isGuest, user } = useAuth();
  const { planId } = useMembership();
  const isFree = planId === "free";
  const persistedRef = useRef(false);

  const insights = useMemo(() => (chart ? buildChartInsights(chart) : null), [chart]);

  useEffect(() => {
    if (isHydrated && !chart) router.replace("/chart");
  }, [chart, isHydrated, router]);

  useEffect(() => {
    if (!chart || !insights || persistedRef.current) return;
    persistedRef.current = true;

    const summary = [
      insights.strengths.thinking,
      insights.lifeStage.title,
      ...insights.growth.slice(0, 2),
    ]
      .filter(Boolean)
      .join("；");

    if (isAuthenticated) {
      void (async () => {
        try {
          const saved = await saveChart(chart);
          const next = { ...chart, chart_id: saved.id, persisted: true };
          setChart(next);
          await saveAnalysisSnapshot(next, insights);
        } catch {
          /* 云端保存失败不影响本地预览 */
        }
      })();
    } else {
      saveLocalAnalysisHistory(null, {
        question: "命盘概览分析",
        analysis_type: "overview",
        topic: "概览",
        suggestions: summary ? [summary] : [],
      });
    }
  }, [chart, insights, isAuthenticated, setChart]);

  if (!isHydrated || !chart || !insights) {
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
          <div>
            <p className="section-label">分析档案</p>
            <h1 className="mt-2 font-display text-2xl font-bold text-paper sm:text-3xl">
              你的 ZiweiX AI 分析档案
            </h1>
            <p className="mt-2 text-sm text-paper/50">
              {chart.name || "访客"} · {chart.gender === "male" ? "男" : "女"} ·{" "}
              {typeof chart.birth.shichen === "string"
                ? chart.birth.shichen
                : chart.birth.shichen?.name ?? ""}
            </p>
            <PrivacyNotice className="mt-2" />
            {isGuest && (
              <p className="mt-2 text-xs text-paper/40">
                当前为游客预览，分析仅保存在本机。
                <Button href="/login" variant="outline" size="sm" className="ml-2">
                  登录保存
                </Button>
              </p>
            )}
          </div>

          {/* Part 1: 基础星盘 */}
          <Section title="一、基础星盘">
            <div className="mb-4 grid gap-2 text-sm sm:grid-cols-2">
              {insights.mainStructure.map((line) => (
                <div key={line} className="rounded-lg border border-paper/10 bg-ink/40 px-3 py-2 text-paper/75">
                  {line}
                </div>
              ))}
            </div>
            <div className="rounded-xl border border-paper/10 bg-ink/30 p-3 sm:p-5">
              <ZiweiChart data={chart} />
            </div>
          </Section>

          {/* Part 2: 优势倾向 */}
          <Section title="二、你的优势倾向">
            <div className="grid gap-3 sm:grid-cols-3">
              <TraitCard label="思维方式" value={insights.strengths.thinking} />
              <TraitCard label="行动模式" value={insights.strengths.action} />
              <TraitCard label="资源特点" value={insights.strengths.resources} />
            </div>
            <p className="mt-4 text-xs text-paper/35">{SITE.notice}</p>
          </Section>

          {/* Part 3: 人生阶段 */}
          <Section title="三、人生阶段">
            <p className="text-sm font-medium text-gold/80">{insights.lifeStage.title}</p>
            <ul className="mt-3 space-y-2">
              {insights.lifeStage.focus.map((item) => (
                <li key={item} className="flex gap-2 text-sm text-paper/70">
                  <span className="text-gold">·</span>
                  {item}
                </li>
              ))}
            </ul>
          </Section>

          {/* Part 4 & 5: 成长建议 + 升级（免费用户部分锁定） */}
          <Section title="四、成长建议" locked={isFree}>
            <ul className="space-y-2">
              {insights.growth.map((item, i) => (
                <li
                  key={item}
                  className={`rounded-lg border border-paper/10 px-3 py-2 text-sm text-paper/75 ${
                    isFree && i >= 2 ? "blur-[2px] select-none" : ""
                  }`}
                >
                  {item}
                </li>
              ))}
            </ul>
          </Section>

          <section className="surface-panel border-gold/25 bg-gradient-to-br from-gold/10 to-ink-soft/90 p-6 sm:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  {isFree && <Lock className="h-4 w-4 text-gold" />}
                  <h2 className="font-display text-xl font-semibold text-paper">
                    {isFree ? "生成完整人生报告" : "查看完整人生报告"}
                  </h2>
                </div>
                <p className="mt-2 max-w-lg text-sm text-paper/55">
                  {isFree
                    ? "免费用户可查看基础报告；深度事业、财富、关系与人生阶段模块需升级会员解锁。"
                    : "基于 Knowledge Core V5.6 生成六维成长档案，含知识来源与导师建议。"}
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button href="/report" variant="gold">
                  {isFree ? "生成基础报告" : "生成完整人生报告"}
                </Button>
                {isFree ? (
                  <>
                    <Button href="/member" variant="outline">
                      升级会员
                    </Button>
                    <Button href="/analysis" variant="outline">
                      预览免费解读
                    </Button>
                  </>
                ) : (
                  <>
                    <Button href="/analysis" variant="outline">
                      六大模块分析
                    </Button>
                    <Button href="/advisor" variant="outline">
                      AI 导师
                    </Button>
                  </>
                )}
              </div>
            </div>
          </section>
        </div>
      </main>
      <Footer />
    </>
  );
}

function TraitCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-paper/10 bg-ink/40 p-4">
      <div className="text-xs font-medium text-gold/70">{label}</div>
      <p className="mt-2 text-sm leading-relaxed text-paper/75">{value}</p>
    </div>
  );
}
