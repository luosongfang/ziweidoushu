"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import PrivacyNotice from "@/components/PrivacyNotice";
import { Button } from "@/components/ui/Button";
import { useChart } from "@/context/ChartContext";
import { useAuth } from "@/contexts/AuthContext";
import { useMembership } from "@/context/MembershipContext";
import { getUserCharts, loadSavedChart, type SavedChartSummary } from "@/services/chartService";
import { getGrowthContext } from "@/services/growthService";

export default function ProfilePage() {
  const { chart, setChart, isHydrated } = useChart();
  const { user, isAuthenticated, isGuest, signOut } = useAuth();
  const { planId, planLabel, points } = useMembership();
  const [savedCharts, setSavedCharts] = useState<SavedChartSummary[]>([]);
  const [focusTopics, setFocusTopics] = useState<string[]>([]);
  const [loadingCharts, setLoadingCharts] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    (async () => {
      setLoadingCharts(true);
      try {
        const [charts, growth] = await Promise.all([getUserCharts(), getGrowthContext()]);
        setSavedCharts(charts);
        setFocusTopics(growth?.focus_topics ?? growth?.growth_goals ?? []);
      } catch {
        setSavedCharts([]);
      } finally {
        setLoadingCharts(false);
      }
    })();
  }, [isAuthenticated]);

  const handleLoadChart = async (chartId: string) => {
    const data = await loadSavedChart(chartId);
    if (data) setChart(data);
  };

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl space-y-6">
          <div className="surface-panel flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-ink font-display text-xl text-gold">
                {user?.nickname?.slice(0, 1) || "访"}
              </div>
              <div>
                <p className="section-label">成长档案</p>
                <h1 className="font-display text-2xl font-semibold text-paper">
                  {isGuest ? "游客体验" : "个人成长中心"}
                </h1>
                <p className="mt-1 text-sm text-paper/50">
                  {isGuest
                    ? "登录后可保存命盘与分析历史"
                    : `${user?.email || ""} · ${planLabel} · 积分 ${points}`}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {isGuest ? (
                <Button href="/login" variant="gold">
                  登录 / 注册
                </Button>
              ) : (
                <>
                  <Button href="/member" variant="gold">
                    会员中心
                  </Button>
                  <Button variant="outline" onClick={() => void signOut()}>
                    退出
                  </Button>
                </>
              )}
            </div>
          </div>

          <PrivacyNotice />

          {/* 我的命盘 */}
          <section className="surface-panel p-6">
            <h2 className="font-display text-lg font-semibold text-paper">我的命盘</h2>
            {isHydrated && chart ? (
              <div className="mt-4 rounded-xl border border-paper/10 bg-ink/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-medium text-paper">{chart.name || "当前命盘"}</p>
                    <p className="mt-1 text-sm text-paper/50">
                      命宫 {chart.meta.mingGong} · {chart.meta.wuxingJu} · {typeof chart.birth.shichen === "string" ? chart.birth.shichen : chart.birth.shichen.name}
                    </p>
                  </div>
                  <Button href="/chart/result" variant="outline" size="sm">
                    查看档案
                  </Button>
                </div>
              </div>
            ) : (
              <p className="mt-4 text-sm text-paper/50">尚未生成命盘</p>
            )}

            {isAuthenticated && (
              <div className="mt-5">
                <p className="text-xs font-medium text-paper/40">历史命盘</p>
                {loadingCharts ? (
                  <p className="mt-2 text-sm text-paper/40">加载中…</p>
                ) : savedCharts.length === 0 ? (
                  <p className="mt-2 text-sm text-paper/45">暂无云端存档</p>
                ) : (
                  <ul className="mt-3 space-y-2">
                    {savedCharts.map((c) => (
                      <li
                        key={c.id}
                        className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-paper/10 px-3 py-2"
                      >
                        <div>
                          <span className="text-sm text-paper/80">
                            {c.name}
                            {c.is_default && (
                              <span className="ml-2 text-xs text-gold">默认</span>
                            )}
                          </span>
                          <p className="text-xs text-paper/40">
                            {c.ming_gong} · {c.five_element}
                          </p>
                        </div>
                        <button
                          type="button"
                          className="text-xs text-gold hover:underline"
                          onClick={() => void handleLoadChart(c.id)}
                        >
                          载入
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            <Button href="/chart" variant="outline" size="sm" className="mt-4">
              {chart ? "重新排盘" : "创建命盘"}
            </Button>
          </section>

          {/* 成长记录 */}
          <section className="surface-panel p-6">
            <h2 className="font-display text-lg font-semibold text-paper">我的成长记录</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <Link
                href="/history"
                className="rounded-xl border border-paper/10 bg-ink/30 p-4 transition hover:border-gold/30"
              >
                <p className="text-sm font-medium text-paper">历史分析</p>
                <p className="mt-1 text-xs text-paper/45">查看过往解读与建议</p>
              </Link>
              <Link
                href="/analysis"
                className="rounded-xl border border-paper/10 bg-ink/30 p-4 transition hover:border-gold/30"
              >
                <p className="text-sm font-medium text-paper">关注方向</p>
                <p className="mt-1 text-xs text-paper/45">
                  {focusTopics.length > 0 ? focusTopics.slice(0, 2).join(" · ") : "探索六大模块"}
                </p>
              </Link>
              <Link
                href="/advisor"
                className="rounded-xl border border-paper/10 bg-ink/30 p-4 transition hover:border-gold/30"
              >
                <p className="text-sm font-medium text-paper">决策记录</p>
                <p className="mt-1 text-xs text-paper/45">AI 导师对话与复盘</p>
              </Link>
            </div>
          </section>

          {/* 会员 */}
          <section className="surface-panel p-6">
            <h2 className="font-display text-lg font-semibold text-paper">我的会员</h2>
            <div className="mt-4 flex flex-wrap gap-6">
              <div>
                <p className="text-xs text-paper/40">当前等级</p>
                <p className="mt-1 font-display text-xl text-gold">{planLabel}</p>
              </div>
              <div>
                <p className="text-xs text-paper/40">积分余额</p>
                <p className="mt-1 font-display text-xl text-paper">{points}</p>
              </div>
            </div>
            {isGuest && (
              <p className="mt-4 text-sm text-paper/50">
                游客可体验基础排盘与一次免费分析。登录后解锁命盘保存与成长档案。
              </p>
            )}
          </section>
        </div>
      </main>
      <Footer />
    </>
  );
}
