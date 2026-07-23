"use client";

import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ChartCard from "@/components/ChartCard";
import { Button } from "@/components/ui/Button";
import { useChart } from "@/context/ChartContext";
import { useMembership } from "@/context/MembershipContext";

const MENU = [
  { label: "我的命盘", href: "/chart/result" },
  { label: "人生档案", href: "/profile" },
  { label: "分析历史", href: "/analysis" },
  { label: "成长笔记", href: "/profile" },
  { label: "我的积分", href: "/member" },
  { label: "事业关注", href: "/analysis" },
  { label: "决策记录", href: "/advisor" },
  { label: "收藏", href: "/profile" },
  { label: "设置", href: "/member" },
  { label: "邀请好友", href: "/member" },
] as const;

export default function ProfilePage() {
  const { chart, isHydrated } = useChart();
  const { planId, points, userId } = useMembership();

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl space-y-6">
          <div className="surface-panel flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-ink font-display text-xl text-gold">
                我
              </div>
              <div>
                <h1 className="font-display text-2xl font-semibold text-paper">成长档案</h1>
                <p className="mt-1 text-sm text-paper/50">
                  {planId.toUpperCase()} · 积分 {points} · ID {userId.slice(0, 8)}
                </p>
              </div>
            </div>
            <Button href="/member" variant="gold">
              会员中心
            </Button>
          </div>

          {isHydrated && chart ? (
            <ChartCard chart={chart} compact />
          ) : (
            <div className="surface-panel p-6 text-sm text-paper/60">
              尚未保存命盘。
              <Button href="/chart" variant="outline" size="sm" className="ml-3">
                去排盘
              </Button>
            </div>
          )}

          <div>
            <p className="section-label">快捷入口</p>
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-5">
              {MENU.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="rounded-xl border border-paper/10 bg-ink-soft/60 px-3 py-4 text-center text-sm text-paper/75 transition hover:border-gold/35 hover:text-gold"
                >
                  {item.label}
                </a>
              ))}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <ArchiveBlock title="历史咨询" body="导师对话记录将展示在此（本地预览阶段）。" />
            <ArchiveBlock title="成长方向" body="结合解盘模块沉淀的关注主题与行动项。" />
            <ArchiveBlock title="决策记录" body="重要选择的复盘与反馈，连接决策闭环。" />
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

function ArchiveBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="surface-panel p-5">
      <h3 className="font-display text-lg text-paper">{title}</h3>
      <p className="mt-2 text-sm text-paper/50">{body}</p>
    </div>
  );
}
