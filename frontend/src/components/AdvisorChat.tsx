"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { useMembership } from "@/context/MembershipContext";
import { analyzeKnowledge, ApiError } from "@/lib/api";
import { useChart } from "@/context/ChartContext";
import { SITE } from "@/lib/constants";

interface Message {
  id: string;
  role: "assistant" | "user";
  content: string;
}

const SUGGESTIONS = [
  "现在适合换行业吗？",
  "创业需要注意什么？",
  "如何提升自己？",
];

const COST = 2;

export default function AdvisorChat() {
  const { chart } = useChart();
  const { points, planId, spendPoints, hydrated } = useMembership();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "你好，我是 AI 人生导师。我可以结合你的命盘与知识库，提供传统文化视角下的人生规划参考。不作绝对预测，也不替代专业咨询。",
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
          content: "AI 人生导师对 VIP / SVIP 开放。你可以先在会员中心预览权益，或使用解盘页体验一次分析。",
        },
      ]);
      return;
    }

    if (!unlimited) {
      const ok = spendPoints(COST);
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
          content: "请先完成排盘，以便结合命盘给出更贴合的规划参考。",
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
        typeof res.safety_notice === "string"
          ? res.safety_notice
          : SITE.notice;
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
          <h1 className="font-display text-lg font-semibold text-paper">AI 人生导师</h1>
          <p className="text-xs text-paper/40">长期陪伴 · 决策辅助 · 非宿命预测</p>
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
        {loading && <div className="text-sm text-paper/40">导师思考中…</div>}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-paper/10 px-4 py-3 sm:px-5">
        <div className="mb-2 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              className="rounded-full border border-paper/15 px-3 py-1 text-xs text-paper/60 hover:border-gold/40 hover:text-gold"
              onClick={() => send(s)}
            >
              {s}
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
