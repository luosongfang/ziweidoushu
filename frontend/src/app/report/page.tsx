"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import AnalysisCard from "@/components/AnalysisCard";
import KnowledgeSource from "@/components/KnowledgeSource";
import PrivacyNotice from "@/components/PrivacyNotice";
import { Button } from "@/components/ui/Button";
import { SITE } from "@/lib/constants";
import { useChart } from "@/context/ChartContext";
import { useAuth } from "@/contexts/AuthContext";
import { useMembership } from "@/context/MembershipContext";
import { createReport, type ReportDetail } from "@/services/reportService";

const CARDS = [
  { key: "identity", title: "自我认知", section: "identity" as const },
  { key: "career", title: "事业方向", section: "career" as const },
  { key: "wealth", title: "财富规划", section: "wealth" as const, lockedFree: true },
  { key: "relationship", title: "关系成长", section: "relationship" as const, lockedFree: true },
  { key: "life_cycle", title: "人生阶段", section: "life_cycle" as const, lockedFree: true },
  { key: "actions", title: "行动建议", section: "personality" as const },
];

export default function ReportPage() {
  const { chart, isHydrated } = useChart();
  const { isAuthenticated } = useAuth();
  const { planId } = useMembership();
  const isFree = planId === "free";
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isHydrated || !chart?.chart_id || !isAuthenticated) return;
    const chartId = chart.chart_id;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      const data = await createReport(chartId, "life_profile");
      if (cancelled) return;
      if (!data) {
        setError("报告生成失败，请稍后重试");
      } else {
        setReport(data);
      }
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [chart?.chart_id, isHydrated, isAuthenticated]);

  const sections = report?.report_sections;

  function cardContent(key: string) {
    if (!sections) return { traditional: [], modern: [], actions: [] };
    if (key === "identity") {
      const id = sections.identity;
      const p = sections.personality;
      return {
        traditional: [id?.traditional_basis].filter(Boolean) as string[],
        modern: [id?.modern_interpretation, id?.chart_summary].filter(Boolean) as string[],
        actions: (p?.growth_direction ?? []).slice(0, 3),
      };
    }
    if (key === "actions") {
      return {
        traditional: [],
        modern: [sections.advisor_message].filter(Boolean) as string[],
        actions: (sections.personality?.growth_direction ?? []).slice(0, 5),
      };
    }
    const block = sections[key as keyof typeof sections];
    if (!block || typeof block !== "object") return { traditional: [], modern: [], actions: [] };
    const b = block as Record<string, unknown>;
    return {
      traditional: [String(b.traditional_view || b.resource_pattern || b.interaction_style || "")].filter(
        Boolean,
      ),
      modern: [String(b.current_stage || b.focus || b.risk_awareness || "")].filter(Boolean),
      actions: [
        ...(Array.isArray(b.development_advice) ? (b.development_advice as string[]) : []),
        ...(Array.isArray(b.growth_advice) ? [String(b.growth_advice)] : []),
        String(b.advice || ""),
      ].filter(Boolean),
    };
  }

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <p className="section-label">人生报告</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">你的个人成长档案</h1>
          <p className="mt-2 max-w-2xl text-sm text-paper/50">{SITE.notice}</p>
          <PrivacyNotice className="mt-2" />

          {!chart && isHydrated && (
            <div className="mt-8 surface-panel p-6">
              <p className="text-paper/70">请先完成排盘，再生成人生报告。</p>
              <Button href="/chart" variant="gold" className="mt-4">
                立即排盘
              </Button>
            </div>
          )}

          {!isAuthenticated && chart && (
            <div className="mt-8 surface-panel p-6">
              <p className="text-paper/70">登录后可生成并保存完整人生报告。</p>
              <Button href="/login" variant="gold" className="mt-4">
                登录
              </Button>
            </div>
          )}

          {loading && (
            <p className="mt-8 text-center text-sm text-paper/50">
              正在结合 Knowledge Core 生成人生报告，请稍候…
            </p>
          )}

          {error && (
            <p className="mt-6 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
              {error}
            </p>
          )}

          {report && sections && (
            <>
              <p className="mt-6 text-sm text-paper/60">{report.summary}</p>
              <div className="mt-8 grid gap-6 lg:grid-cols-2">
                {CARDS.map((card) => {
                  const locked = isFree && card.lockedFree;
                  const blocks = cardContent(card.key === "actions" ? "actions" : card.section);
                  return (
                    <div key={card.key} className={locked ? "relative opacity-60" : ""}>
                      {locked && (
                        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-ink/70">
                          <Link href="/member" className="text-sm text-gold hover:underline">
                            升级解锁
                          </Link>
                        </div>
                      )}
                      <AnalysisCard
                        title={card.title}
                        traditional={blocks.traditional}
                        modern={blocks.modern}
                        actions={blocks.actions}
                      />
                    </div>
                  );
                })}
              </div>
              <div className="mt-8">
                <KnowledgeSource
                  sources={(report.knowledge_trace?.sources as []) || []}
                  locked={isFree}
                />
              </div>
              <div className="mt-6 flex flex-wrap gap-3">
                <Button href="/advisor" variant="gold">
                  继续 AI 导师陪伴
                </Button>
                <Button href="/growth" variant="outline">
                  成长中心
                </Button>
              </div>
            </>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
