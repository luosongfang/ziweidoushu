"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import AnalysisCard from "@/components/AnalysisCard";
import KnowledgeSource from "@/components/KnowledgeSource";
import PrivacyNotice from "@/components/PrivacyNotice";
import { Button } from "@/components/ui/Button";
import { ANALYSIS_MODULES, SITE } from "@/lib/constants";
import { saveLocalAnalysisHistory } from "@/lib/analysisHistory";
import { useChart } from "@/context/ChartContext";
import { useAuth } from "@/contexts/AuthContext";
import { useMembership } from "@/context/MembershipContext";
import { analyzeKnowledge, ApiError } from "@/lib/api";
import type { KnowledgeAnalyzeResponse } from "@/types/analysis";
import type { ChartCreateResponse } from "@/types/ziwei";

function chartPayloadForAnalysis(chart: ChartCreateResponse): Record<string, unknown> {
  const palaces = chart.palaces ?? [];
  const byName: Record<string, unknown> = {};
  for (const p of palaces) {
    byName[p.name] = {
      stars: [
        ...p.main_stars.map((s) => s.name),
        ...p.lucky_stars.map((s) => s.name),
        ...p.sha_stars.map((s) => s.name),
        ...p.za_stars.map((s) => s.name),
      ],
      branch: p.branch,
    };
  }
  return {
    chart_id: chart.chart_id,
    name: chart.name,
    chart: { palaces, ming_gong: chart.meta?.mingGong, five_element: chart.meta?.wuxingJu },
    ...byName,
  };
}

function pickStrings(res: KnowledgeAnalyzeResponse | null): {
  traditional: string[];
  modern: string[];
  actions: string[];
} {
  if (!res) return { traditional: [], modern: [], actions: [] };
  const traditional: string[] = [];
  const modern: string[] = [];
  const actions = [...(res.suggestions || [])].slice(0, 5);

  const ta = res.traditional_analysis;
  if (typeof ta === "string") traditional.push(ta);
  else if (ta && typeof ta === "object") {
    Object.values(ta as Record<string, unknown>).forEach((v) => {
      if (typeof v === "string" && v.trim()) traditional.push(v);
    });
  }

  const da = res.decision_analysis;
  if (da && typeof da === "object") {
    const d = da as Record<string, unknown>;
    if (typeof d.current_state === "string") modern.push(d.current_state);
    if (Array.isArray(d.strengths)) {
      modern.push(...d.strengths.map(String).slice(0, 3));
    }
    if (Array.isArray(d.action_suggestions)) {
      actions.push(...d.action_suggestions.map(String).slice(0, 3));
    }
  }

  if (res.reflection_questions?.length) {
    modern.push("反思：" + res.reflection_questions.slice(0, 2).join("；"));
  }

  return {
    traditional: traditional.slice(0, 4),
    modern: modern.slice(0, 4),
    actions: Array.from(new Set(actions)).slice(0, 5),
  };
}

export default function AnalysisPage() {
  const { chart, isHydrated } = useChart();
  const { user, isGuest } = useAuth();
  const { planId, freeAnalysisUsed, markAnalysisUsed, isGuest: membershipGuest } = useMembership();
  const [active, setActive] = useState<string>(ANALYSIS_MODULES[0].id);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cache, setCache] = useState<Record<string, KnowledgeAnalyzeResponse>>({});

  const module = ANALYSIS_MODULES.find((m) => m.id === active) || ANALYSIS_MODULES[0];
  const result = cache[active] || null;
  const blocks = useMemo(() => pickStrings(result), [result]);
  const sourcesLocked = planId === "free";

  useEffect(() => {
    if (!isHydrated || !chart || cache[active]) return;
    let cancelled = false;

    (async () => {
      if (planId === "free" && freeAnalysisUsed && Object.keys(cache).length > 0) {
        setError("免费专业解读已使用。登录并升级会员可继续查看更多模块。");
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await analyzeKnowledge({
          question: module.question,
          chart_id: chart.chart_id,
          chart_data: chartPayloadForAnalysis(chart),
          engine_version: "5.1",
          user_id: user?.id ?? null,
          persist_memory: false,
          persist_growth_memory: false,
        });
        if (cancelled) return;
        setCache((c) => ({ ...c, [active]: res }));
        saveLocalAnalysisHistory(user?.id ?? null, {
          question: module.question,
          question_type: module.id,
          topic: module.label,
          suggestions: res.suggestions ?? [],
        });
        if (membershipGuest && planId === "free") markAnalysisUsed();
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "分析失败");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [active, chart, isHydrated, cache, module.question, module.id, module.label, planId, freeAnalysisUsed, markAnalysisUsed, membershipGuest, user?.id]);

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <p className="section-label">深度分析</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">六大人生模块</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-paper/50">{SITE.notice}</p>
          <PrivacyNotice className="mt-2" />

          {isGuest && (
            <p className="mt-3 text-sm text-paper/45">
              游客可体验基础排盘与一次免费分析。
              <Link href="/login" className="ml-1 text-gold/80 hover:underline">
                登录
              </Link>
              后可保存命盘与成长记录。
            </p>
          )}

          {!chart && isHydrated && (
            <div className="mt-8 surface-panel p-6">
              <p className="text-paper/70">请先创建个人星盘，再进行专业解读。</p>
              <Button href="/chart" variant="gold" className="mt-4">
                创建星盘
              </Button>
            </div>
          )}

          {chart && (
            <>
              <div className="mt-8 flex gap-2 overflow-x-auto pb-2">
                {ANALYSIS_MODULES.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setActive(m.id)}
                    className={`shrink-0 rounded-full px-4 py-1.5 text-sm transition ${
                      active === m.id
                        ? "bg-gold text-ink"
                        : "border border-paper/15 text-paper/60 hover:border-gold/30"
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>

              <p className="mt-4 text-xs text-paper/35">
                每个模块：传统依据 → 现代解释 → 行动建议
              </p>

              {error && (
                <p className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
                  {error}
                </p>
              )}

              <div className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
                <AnalysisCard
                  title={module.label}
                  traditional={blocks.traditional}
                  modern={blocks.modern}
                  actions={blocks.actions}
                  loading={loading}
                />
                <div className="space-y-4">
                  <KnowledgeSource sources={result?.sources} locked={sourcesLocked} />
                  <div className="flex flex-wrap gap-3">
                    <Button href="/advisor" variant="gold">
                      继续向导师提问
                    </Button>
                    <Link href="/member" className="text-sm text-gold/80 hover:underline">
                      升级查看完整引用 →
                    </Link>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
