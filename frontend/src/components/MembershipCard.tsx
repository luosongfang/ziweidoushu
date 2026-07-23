import { Button } from "@/components/ui/Button";
import { MEMBERSHIP_PLANS } from "@/lib/constants";

type Plan = (typeof MEMBERSHIP_PLANS)[number];

interface MembershipCardProps {
  plan: Plan;
  current?: boolean;
  onSelect?: (planId: string) => void;
}

export default function MembershipCard({ plan, current, onSelect }: MembershipCardProps) {
  return (
    <div
      className={`relative flex h-full flex-col rounded-2xl border p-6 ${
        plan.recommended
          ? "border-gold/50 bg-gradient-to-b from-gold/10 to-ink-soft/90 shadow-gold"
          : "border-paper/10 bg-ink-soft/70"
      }`}
    >
      {plan.recommended && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gold px-3 py-0.5 text-[11px] font-semibold text-ink">
          推荐
        </span>
      )}
      <h3 className="font-display text-xl font-semibold text-paper">{plan.name}</h3>
      <div className="mt-3 flex items-baseline gap-1">
        <span className="font-display text-3xl font-bold text-gold-light">¥{plan.price}</span>
        <span className="text-sm text-paper/45">/{plan.period}</span>
      </div>
      <ul className="mt-5 flex-1 space-y-2.5">
        {plan.features.map((f) => (
          <li key={f} className="flex gap-2 text-sm text-paper/70">
            <span className="text-gold">✓</span>
            <span>{f}</span>
          </li>
        ))}
      </ul>
      {"pointsNote" in plan && plan.pointsNote && (
        <p className="mt-4 text-xs text-paper/40">{plan.pointsNote}</p>
      )}
      <Button
        className="mt-6 w-full"
        variant={plan.recommended ? "gold" : "outline"}
        disabled={current}
        onClick={() => onSelect?.(plan.id)}
      >
        {current ? "当前方案" : "选择方案（预留）"}
      </Button>
      <p className="mt-2 text-center text-[11px] text-paper/30">支付未接入 · 仅预览权益</p>
    </div>
  );
}
