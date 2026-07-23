"use client";

import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import MembershipCard from "@/components/MembershipCard";
import { Button } from "@/components/ui/Button";
import { FREE_BENEFITS, FREE_LIMITS, MEMBERSHIP_PLANS } from "@/lib/constants";
import { useMembership, type PlanId } from "@/context/MembershipContext";

export default function MemberPage() {
  const { planId, points, setPlan } = useMembership();

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-6xl">
          <p className="section-label">会员中心</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">选择适合你的成长方案</h1>
          <p className="mt-2 text-sm text-paper/50">
            支付能力预留中，当前可本地预览切换权益（不会产生真实扣款）。
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <div className="surface-panel p-5">
              <h2 className="font-display text-lg text-paper">免费用户</h2>
              <ul className="mt-3 space-y-2 text-sm text-paper/65">
                {FREE_BENEFITS.map((b) => (
                  <li key={b}>✓ {b}</li>
                ))}
              </ul>
              <p className="mt-4 text-xs text-paper/40">限制</p>
              <ul className="mt-1 space-y-1 text-sm text-paper/45">
                {FREE_LIMITS.map((b) => (
                  <li key={b}>· {b}</li>
                ))}
              </ul>
              <Button
                className="mt-5"
                variant={planId === "free" ? "gold" : "outline"}
                onClick={() => setPlan("free")}
              >
                {planId === "free" ? "当前为免费方案" : "切换为免费预览"}
              </Button>
            </div>
            <div className="surface-panel p-5">
              <h2 className="font-display text-lg text-paper">当前状态</h2>
              <p className="mt-3 text-sm text-paper/60">
                方案：<span className="text-gold">{planId.toUpperCase()}</span>
              </p>
              <p className="mt-1 text-sm text-paper/60">积分余额：{points}</p>
              <p className="mt-4 text-xs leading-relaxed text-paper/40">
                数据库已预留 user_membership / user_points / membership_orders。后端支付确认接口待接入。
              </p>
            </div>
          </div>

          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {MEMBERSHIP_PLANS.map((plan) => (
              <MembershipCard
                key={plan.id}
                plan={plan}
                current={planId === plan.id}
                onSelect={(id) => setPlan(id as PlanId)}
              />
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
