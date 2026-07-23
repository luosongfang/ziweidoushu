"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { useMembership } from "@/context/MembershipContext";
import { analyzeKnowledge, ApiError } from "@/lib/api";
import { useChart } from "@/context/ChartContext";
import { ADVISOR_QUICK_QUESTIONS, SITE } from "@/lib/constants";
import { useAuth } from "@/contexts/AuthContext";
import type { GrowthContext } from "@/services/growthService";
import { consumePoints } from "@/services/memberService";

interface Message {
  id: string;
  role: "assistant" | "user";
  content: string;
}

const QUESTION_MAP: Record<string, string> = {
  事业方向: "请结合我的命盘，分析当前适合关注的事业方向与行动建议",
  创业选择: "如果考虑创业，从传统文化视角有哪些需要留意的要点？",
  个人优势: "请帮我梳理个人优势与可强化的能力方向",
  人生阶段: "请结合当前人生阶段，给出关注方向与规划参考",
  关系经营: "请分析我的人际相处模式与关系经营建议",
  成长规划: "请给出可执行的自我成长规划与反思问题",
};

const COST = 2;

interface AdvisorChatProps {
  growthContext?: GrowthContext | null;
}

export default function AdvisorChat({ growthContext }: AdvisorChatProps) {
  const { chart } = useChart();
  const { user, isAuthenticated } = useAuth();
  const { points, planId, spendPoints, hydrated, syncFromServer } = useMembership();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const welcome = growthContext?.continuity_message
    ? `欢迎回来。${growthContext.continuity_message} 我可以结合你的星盘与成长记录，提供传统文化视角下的建议。`
    : "你好，我是 ZiweiX AI Mentor。我可以结合你的星盘与知识库，提供传统文化视角下的成长建议。不作绝对预测，帮助你进行自我探索。";

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: welcome,
    },
  ]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const canChat = planId === "vip" || planId === "svip";
  const unlimited = planId === "svip";

  const send = async (text: string) => {
    const question = text.trim();
    if (!question || loading) return;

    if (!canChat) {
      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "AI 导师对 VIP / SVIP 开放。你可以先在会员中心了解权益，或使用分析页体验一次免费解读。",
        },
      ]);
      return;
    }

    if (!unlimited) {
      let ok = false;
      if (isAuthenticated) {
        const result = await consumePoints(COST);
        ok = result.success;
        if (ok) void syncFromServer();
      } else {
        ok = spendPoints(COST);
      }
      if (!ok) {
        setMessages((m) => [
          ...m,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: `积分不足（每次交流消耗 ${COST} 积分）。当前积分：${points}。`,
          },
        ]);
        return;
      }
    }

    if (!chart) {
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "user", content: question },
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "请先创建个人星盘，以便结合分析结构给出更贴合的建议。",
        },
      ]);
      setInput("");
      return;
    }

    setMessages((m) => [...m, { id: crypto.randomUUID(), role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await analyzeKnowledge({
        question,
        chart_id: chart.chart_id,
        chart_data: chart as unknown as Record<string, unknown>,
        engine_version: "5.1",
        user_id: user?.id ?? null,
        persist_memory: Boolean(user?.id),
      });

      const parts: string[] = [];
      const da = res.decision_analysis;
      if (da && typeof da === "object") {
        const cur = (da as { current_state?: string }).current_state;
        if (cur) parts.push(String(cur));
      }
      if (res.suggestions?.length) {
        parts.push("行动建议：\n" + res.suggestions.slice(0, 4).map((s) => `· ${s}`).join("\n"));
      }
      if (res.reflection_questions?.length) {
        parts.push(
          "反思问题：\n" +
            res.reflection_questions.slice(0, 3).map((q) => `· ${q}`).join("\n"),
        );
      }
      const notice =
        typeof res.safety_notice === "string" ? res.safety_notice : SITE.notice;
      parts.push(notice);

      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: parts.join("\n\n") || "已生成参考建议，可继续追问具体场景。",
        },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: err instanceof ApiError ? err.message : "暂时无法回复，请稍后再试。",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[min(72vh,720px)] flex-col overflow-hidden rounded-2xl border border-paper/10 bg-ink-soft/80 shadow-panel">
      <div className="flex items-center justify-between border-b border-paper/10 px-4 py-3 sm:px-5">
        <div>
          <h2 className="font-display text-lg font-semibold text-paper">ZiweiX AI Mentor</h2>
          <p className="text-xs text-paper/40">成长陪伴 · 自我探索 · 非宿命论断</p>
        </div>
        <div className="rounded-full border border-gold/30 px-3 py-1 text-xs text-gold">
          {hydrated ? `积分 ${points}` : "…"}
          {!unlimited && canChat ? ` · 每次 ${COST}` : ""}
        </div>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4 sm:px-5">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`max-w-[90%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              m.role === "user"
                ? "ml-auto bg-gold/15 text-paper"
                : "bg-ink/60 text-paper/85"
            }`}
          >
            {m.content}
          </div>
        ))}
        {loading && <div className="text-sm text-paper/40">分析中…</div>}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-paper/10 px-4 py-3 sm:px-5">
        <div className="mb-2 flex flex-wrap gap-2">
          {ADVISOR_QUICK_QUESTIONS.map((label) => (
            <button
              key={label}
              type="button"
              className="rounded-full border border-paper/15 px-3 py-1 text-xs text-paper/60 hover:border-gold/40 hover:text-gold"
              onClick={() => send(QUESTION_MAP[label] ?? label)}
            >
              {label}
            </button>
          ))}
        </div>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            void send(input);
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="提出你的人生问题…"
            className="h-11 flex-1 rounded-xl border border-paper/15 bg-ink/50 px-4 text-sm text-paper outline-none placeholder:text-paper/30 focus:border-gold/40"
          />
          <Button type="submit" variant="gold" disabled={loading}>
            发送
          </Button>
        </form>
      </div>
    </div>
  );
}
