"use client";

import { useMemo, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";
import type { ChartCreateResponse, Palace } from "@/types/ziwei";
import { cn } from "@/lib/utils";
import PalaceCard from "./PalaceCard";
import StarBadge, { starCategoryToVariant } from "./StarBadge";
import FourHuaTag from "./FourHuaTag";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ZiweiChartProps {
  data: ChartCreateResponse;
  className?: string;
}

/** 十二宫圆盘 — 命宫置顶，逆时针排列 */
const PALACE_ORDER = [
  "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
  "迁移", "交友", "官禄", "田宅", "福德", "父母",
];

export default function ZiweiChart({ data, className }: ZiweiChartProps) {
  const [selected, setSelected] = useState<Palace | null>(null);
  const [radius, setRadius] = useState(168);
  const { chart } = data;

  useEffect(() => {
    const update = () => setRadius(window.innerWidth < 640 ? 118 : 168);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const orderedPalaces = useMemo(() => {
    const map = new Map(chart.palaces.map((p) => [p.name, p]));
    return PALACE_ORDER.map((name) => map.get(name)).filter(Boolean) as Palace[];
  }, [chart.palaces]);

  return (
    <div className={cn("relative w-full", className)}>
      {/* 桌面：圆盘模式 */}
      <div className="relative mx-auto hidden aspect-square max-w-[520px] sm:block">
        <div className="absolute inset-0 rounded-full border border-purple-glow/20 bg-gradient-radial from-purple-deep/20 to-transparent" />
        <div className="absolute inset-8 rounded-full border border-gold/10 border-dashed" />
        <div className="absolute inset-16 rounded-full border border-white/5" />

        {/* 中心信息 */}
        <div className="absolute left-1/2 top-1/2 z-10 w-[140px] -translate-x-1/2 -translate-y-1/2">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-2xl border border-gold/30 bg-void-100/90 p-4 text-center backdrop-blur-xl shadow-glow-gold"
          >
            <Sparkles className="mx-auto mb-2 h-5 w-5 text-gold" />
            <div className="text-[10px] text-white/40">命宫 · 身宫 · 五行</div>
            <div className="mt-2 grid grid-cols-3 gap-1 text-xs">
              <div>
                <div className="text-white/30">命宫</div>
                <div className="font-semibold text-gold-light">{chart.ming_gong}</div>
              </div>
              <div>
                <div className="text-white/30">身宫</div>
                <div className="font-semibold text-purple-mist">{chart.shen_gong}</div>
              </div>
              <div>
                <div className="text-white/30">五行</div>
                <div className="font-semibold text-white/80">{chart.five_element.replace("局", "")}</div>
              </div>
            </div>
          </motion.div>
        </div>

        {orderedPalaces.map((palace, i) => (
          <PalaceCard
            key={palace.name}
            palace={palace}
            index={i}
            angle={-90 + i * 30}
            radius={radius}
            selected={selected?.name === palace.name}
            onSelect={setSelected}
          />
        ))}
      </div>

      {/* 手机：缩放网格模式 */}
      <div className="sm:hidden">
        <div className="mb-4 rounded-2xl border border-gold/20 bg-gold/5 p-4 text-center">
          <div className="text-xs text-white/40">命宫 {chart.ming_gong} · 身宫 {chart.shen_gong} · {chart.five_element}</div>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {orderedPalaces.map((palace, i) => (
            <motion.button
              key={palace.name}
              type="button"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              onClick={() => setSelected(palace)}
              className={cn(
                "rounded-xl border p-2 text-left",
                palace.is_ming_gong ? "border-gold/40 bg-gold/10" : "border-white/10 bg-white/5",
              )}
            >
              <div className="flex justify-between text-xs font-semibold">
                <span>{palace.name}</span>
                <span className="text-gold/70">{palace.branch}</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {palace.stars
                  .filter((s) => s.category === "main")
                  .slice(0, 2)
                  .map((s) => (
                    <StarBadge key={s.name} name={s.name} variant="main" sihua={s.sihua} />
                  ))}
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* 宫位详情面板 */}
      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            className="mt-6"
          >
            <Card>
              <CardHeader>
                <CardTitle>
                  {selected.name} · {selected.branch} · {selected.ganzhi}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {selected.stars
                    .filter((s) => s.category !== "daxian")
                    .map((star) => (
                      <StarBadge
                        key={star.name}
                        name={star.name}
                        variant={starCategoryToVariant(star.category)}
                        sihua={star.sihua}
                      />
                    ))}
                </div>
                {selected.transformations.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selected.transformations.map((t) => (
                      <span key={t.star} className="text-xs text-white/50">
                        {t.star} <FourHuaTag type={t.type} />
                      </span>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 四化摘要 */}
      {chart.four_hua && (
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {(["hua_lu", "hua_quan", "hua_ke", "hua_ji"] as const).map((key) => {
            const item = chart.four_hua![key];
            return (
              <div key={key} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-center text-xs">
                <FourHuaTag type={item.type as "禄" | "权" | "科" | "忌"} size="md" />
                <div className="mt-1 text-white/70">
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
