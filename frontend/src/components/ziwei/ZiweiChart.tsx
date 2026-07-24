"use client";

import { useMemo } from "react";
import ChartBoard from "@/components/chart/ChartBoard";
import FourHuaTag from "./FourHuaTag";
import type { ChartCreateResponse, SiHuaType } from "@/types/ziwei";
import { adaptChartCreateResponse } from "@/lib/chartAdapter";
import { cn } from "@/lib/utils";

interface ZiweiChartProps {
  data: ChartCreateResponse;
  className?: string;
}

const HUA_ITEMS: Array<{ key: "lu" | "quan" | "ke" | "ji"; label: SiHuaType }> = [
  { key: "lu", label: "禄" },
  { key: "quan", label: "权" },
  { key: "ke", label: "科" },
  { key: "ji", label: "忌" },
];

/** 十二宫命盘 — 传统 4×4 专业布局（StandardChartSchema V2） */
export default function ZiweiChart({ data, className }: ZiweiChartProps) {
  const boardData = useMemo(() => adaptChartCreateResponse(data), [data]);
  const four = data.four_transform;

  return (
    <div className={cn("w-full", className)}>
      <div className="overflow-x-auto pb-2">
        <div className="min-w-[340px]">
          <ChartBoard data={boardData} />
        </div>
      </div>

      {four && (
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {HUA_ITEMS.map(({ key, label }) => {
            const item = four[key];
            if (!item) return null;
            return (
              <div
                key={key}
                className="rounded-xl border border-paper/10 bg-ink/40 px-3 py-2.5 text-center"
              >
                <FourHuaTag type={label} size="md" />
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
