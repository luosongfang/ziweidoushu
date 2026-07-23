"use client";

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { getGrowthProfile } from "@/services/reportService";

export default function GrowthPage() {
  const { isAuthenticated, isGuest } = useAuth();
  const [data, setData] = useState<Awaited<ReturnType<typeof getGrowthProfile>>>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    void (async () => {
      setData(await getGrowthProfile());
      setLoading(false);
    })();
  }, [isAuthenticated]);

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl space-y-6">
          <div>
            <p className="section-label">成长中心</p>
            <h1 className="mt-2 font-display text-3xl font-bold text-paper">我的成长轨迹</h1>
            <p className="mt-2 text-sm text-paper/50">
              汇总历史分析、关注领域与长期目标，帮助你看清成长方向。
            </p>
          </div>

          {isGuest && (
            <div className="surface-panel p-6">
              <p className="text-paper/70">登录后查看完整成长轨迹与导师建议。</p>
              <Button href="/login" variant="gold" className="mt-4">
                登录
              </Button>
            </div>
          )}

          {isAuthenticated && loading && (
            <p className="text-sm text-paper/45">加载成长档案…</p>
          )}

          {isAuthenticated && data && (
            <>
              {data.continuity_message && (
                <section className="surface-panel border-gold/20 p-6">
                  <p className="text-sm leading-relaxed text-paper/75">{data.continuity_message}</p>
                </section>
              )}

              <section className="surface-panel p-6">
                <h2 className="font-display text-lg text-paper">关注领域变化</h2>
                <div className="mt-4 flex flex-wrap gap-2">
                  {(data.focus_topics.length ? data.focus_topics : ["自我认知", "事业探索"]).map((t) => (
                    <span
                      key={t}
                      className="rounded-full border border-paper/15 px-3 py-1 text-xs text-paper/60"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </section>

              <section className="surface-panel p-6">
                <h2 className="font-display text-lg text-paper">人生目标</h2>
                <ul className="mt-4 space-y-3">
                  {data.goals.map((g) => (
                    <li
                      key={String(g.id)}
                      className="rounded-xl border border-paper/10 bg-ink/40 px-4 py-3 text-sm text-paper/75"
                    >
                      <span className="text-xs text-gold/70">{String(g.goal_type)}</span>
                      <p className="mt-1">{String(g.goal_content)}</p>
                    </li>
                  ))}
                </ul>
              </section>

              <section className="surface-panel p-6">
                <h2 className="font-display text-lg text-paper">历史分析记录</h2>
                <ul className="mt-4 space-y-2">
                  {data.history.slice(0, 8).map((h) => (
                    <li
                      key={String(h.id)}
                      className="rounded-lg border border-paper/10 px-3 py-2 text-sm text-paper/65"
                    >
                      {String(h.question || h.summary || "分析记录")}
                    </li>
                  ))}
                  {data.history.length === 0 && (
                    <li className="text-sm text-paper/40">暂无记录，完成一次分析后会出现在这里。</li>
                  )}
                </ul>
              </section>

              <section className="surface-panel p-6">
                <h2 className="font-display text-lg text-paper">导师建议</h2>
                <ul className="mt-4 space-y-2">
                  {(data.advisor_suggestions.length
                    ? data.advisor_suggestions
                    : ["从一个小目标开始，每周复盘一次。"]
                  ).map((s) => (
                    <li key={s} className="text-sm text-paper/70">
                      · {s}
                    </li>
                  ))}
                </ul>
                <Button href="/advisor" variant="gold" className="mt-4">
                  向 AI 导师提问
                </Button>
              </section>
            </>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
