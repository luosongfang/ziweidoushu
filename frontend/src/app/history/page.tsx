"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import PrivacyNotice from "@/components/PrivacyNotice";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { getAnalysisHistory, type HistoryRecord } from "@/services/growthService";
import { loadLocalAnalysisHistory } from "@/lib/analysisHistory";

export default function HistoryPage() {
  const { isAuthenticated, isGuest, isLoading } = useAuth();
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isLoading) return;
    (async () => {
      setLoading(true);
      if (isAuthenticated) {
        const remote = await getAnalysisHistory();
        setRecords(remote);
      } else {
        setRecords(loadLocalAnalysisHistory());
      }
      setLoading(false);
    })();
  }, [isAuthenticated, isLoading]);

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <p className="section-label">成长记录</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">分析历史</h1>
          <PrivacyNotice className="mt-3" />

          {isGuest && !isLoading && (
            <div className="mt-6 surface-panel p-5 text-sm text-paper/60">
              登录后可同步云端分析历史与成长档案。
              <Button href="/login" variant="gold" size="sm" className="ml-3">
                去登录
              </Button>
            </div>
          )}

          {loading ? (
            <p className="mt-8 text-sm text-paper/45">加载中…</p>
          ) : records.length === 0 ? (
            <div className="mt-8 surface-panel p-8 text-center">
              <p className="text-paper/55">暂无分析记录</p>
              <Button href="/analysis" variant="gold" className="mt-4">
                开始第一次分析
              </Button>
            </div>
          ) : (
            <div className="mt-8 space-y-4">
              {records.map((item) => (
                <article key={item.id} className="surface-panel p-5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="rounded-full border border-gold/30 px-2.5 py-0.5 text-xs text-gold">
                      {item.topic || item.analysis_type || "分析"}
                    </span>
                    <time className="text-xs text-paper/35">
                      {item.created_at ? new Date(item.created_at).toLocaleString("zh-CN") : "—"}
                    </time>
                  </div>
                  <h2 className="mt-3 font-medium text-paper">{item.question}</h2>
                  {item.suggestions.length > 0 && (
                    <ul className="mt-3 space-y-1.5">
                      {item.suggestions.slice(0, 3).map((s) => (
                        <li key={s.slice(0, 40)} className="text-sm text-paper/65">
                          · {s}
                        </li>
                      ))}
                    </ul>
                  )}
                </article>
              ))}
            </div>
          )}

          <div className="mt-8 text-center">
            <Link href="/profile" className="text-sm text-gold/75 hover:underline">
              返回成长档案 →
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
