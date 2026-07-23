"use client";

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import AdvisorChat from "@/components/AdvisorChat";
import PrivacyNotice from "@/components/PrivacyNotice";
import { Button } from "@/components/ui/Button";
import { SITE } from "@/lib/constants";
import { useAuth } from "@/contexts/AuthContext";
import { useMembership } from "@/context/MembershipContext";
import { getGrowthContext, type GrowthContext } from "@/services/growthService";

export default function AdvisorPage() {
  const { isAuthenticated } = useAuth();
  const { planId } = useMembership();
  const unlocked = planId === "vip" || planId === "svip";
  const [growth, setGrowth] = useState<GrowthContext | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    void getGrowthContext().then(setGrowth);
  }, [isAuthenticated]);

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-16 pt-24 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <p className="section-label">ZiweiX AI Mentor</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">你的专属人生分析助手</h1>
          <p className="mt-3 rounded-xl border border-paper/10 bg-ink-soft/50 px-4 py-3 text-sm leading-relaxed text-paper/55">
            {SITE.notice}
          </p>
          <PrivacyNotice className="mt-2" />

          {isAuthenticated && growth?.continuity_message && (
            <div className="mt-4 rounded-xl border border-gold/20 bg-gold/5 px-4 py-3 text-sm leading-relaxed text-paper/75">
              欢迎回来，根据你的历史探索，我们继续关注你的成长方向：{growth.continuity_message}
            </div>
          )}

          {!unlocked && (
            <div className="mt-4 rounded-xl border border-gold/25 bg-gold/5 px-4 py-3 text-sm text-paper/70">
              当前为体验预览。开通 VIP 后可连续对话并保存成长档案。
              <Button href="/member" variant="outline" size="sm" className="ml-3">
                查看会员
              </Button>
            </div>
          )}
          <div className="mt-6">
            <AdvisorChat growthContext={growth} />
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
