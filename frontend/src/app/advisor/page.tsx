"use client";

import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import AdvisorChat from "@/components/AdvisorChat";
import { Button } from "@/components/ui/Button";
import { useMembership } from "@/context/MembershipContext";

export default function AdvisorPage() {
  const { planId } = useMembership();
  const unlocked = planId === "vip" || planId === "svip";

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-16 pt-24 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <p className="section-label">长期陪伴</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">AI 人生导师</h1>
          <p className="mt-2 text-sm text-paper/50">
            结合命盘、咨询上下文与知识库，提供人生规划参考。每次交流消耗 2 积分（SVIP 不限）。
          </p>
          {!unlocked && (
            <div className="mt-4 rounded-xl border border-gold/25 bg-gold/5 px-4 py-3 text-sm text-paper/70">
              当前为体验预览。开通 VIP 后可连续对话并保存成长档案。
              <Button href="/member" variant="outline" size="sm" className="ml-3">
                查看会员
              </Button>
            </div>
          )}
          <div className="mt-6">
            <AdvisorChat />
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
