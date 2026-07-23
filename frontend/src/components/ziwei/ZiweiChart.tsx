"use client";

import { useMemo } from "react";
import ChartBoard from "@/components/chart/ChartBoard";
import FourHuaTag from "./FourHuaTag";
import type { ChartCreateResponse } from "@/types/ziwei";
import { adaptChartCreateResponse } from "@/lib/chartAdapter";
import { cn } from "@/lib/utils";

interface ZiweiChartProps {
  data: ChartCreateResponse;
  className?: string;
}

/** 十二宫命盘 — 传统 4×4 专业布局（与 Product UI V1.0 一致） */
export default function ZiweiChart({ data, className }: ZiweiChartProps) {
  const boardData = useMemo(() => adaptChartCreateResponse(data), [data]);
  const { chart } = data;

  return (
    <div className={cn("w-full", className)}>
      <div className="overflow-x-auto pb-2">
        <div className="min-w-[340px]">
          <ChartBoard data={boardData} />
        </div>
      </div>

      {chart.four_hua && (
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {(["hua_lu", "hua_quan", "hua_ke", "hua_ji"] as const).map((key) => {
            const item = chart.four_hua![key];
            return (
              <div
                key={key}
                className="rounded-xl border border-paper/10 bg-ink/40 px-3 py-2.5 text-center"
              >
                <FourHuaTag type={item.type as "禄" | "权" | "科" | "忌"} size="md" />
                <div className="mt-1.5 text-xs text-paper/70">
                  {item.star} → {item.palace}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
