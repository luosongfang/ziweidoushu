"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { ANALYSIS_LOADING_STEPS } from "@/lib/constants";

interface AnalysisLoadingProps {
  minDuration?: number;
  /** 外部任务完成（如 API 返回） */
  ready?: boolean;
  onComplete?: () => void;
}

export default function AnalysisLoading({
  minDuration = 3000,
  ready = false,
  onComplete,
}: AnalysisLoadingProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const [startedAt] = useState(() => Date.now());
  const [minElapsed, setMinElapsed] = useState(false);

  useEffect(() => {
    const stepMs = minDuration / ANALYSIS_LOADING_STEPS.length;
    const stepTimer = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, ANALYSIS_LOADING_STEPS.length - 1));
    }, stepMs);

    const minTimer = setTimeout(() => setMinElapsed(true), minDuration);

    return () => {
      clearInterval(stepTimer);
      clearTimeout(minTimer);
    };
  }, [minDuration]);

  useEffect(() => {
    if (minElapsed && ready) {
      onComplete?.();
    }
  }, [minElapsed, ready, onComplete]);

  const progressDone = minElapsed && ready;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/90 px-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-paper/10 bg-ink-soft/95 p-8 shadow-panel">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-gold/30 bg-gold/10">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-gold/30 border-t-gold" />
        </div>
        <h2 className="mt-6 text-center font-display text-xl font-semibold text-paper">
          正在建立你的个人分析模型…
        </h2>
        <ul className="mt-8 space-y-3">
          {ANALYSIS_LOADING_STEPS.map((step, i) => {
            const completed = progressDone || i < stepIndex;
            const current = !progressDone && i === stepIndex;
            return (
              <li
                key={step}
                className={`flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition ${
                  current ? "bg-gold/10 text-paper" : completed ? "text-paper/70" : "text-paper/35"
                }`}
              >
                <span
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                    completed
                      ? "border-emerald-400/40 bg-emerald-400/15 text-emerald-300"
                      : current
                        ? "border-gold/40 text-gold"
                        : "border-paper/15"
                  }`}
                >
                  {completed ? <Check className="h-3 w-3" /> : current ? "·" : ""}
                </span>
                {step}
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
