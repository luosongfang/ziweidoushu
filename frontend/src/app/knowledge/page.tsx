"use client";

import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";

const CATEGORIES = [
  {
    id: "stars",
    title: "十四主星",
    desc: "了解主星特质、亮度与组合思路，建立星曜知识框架。",
    items: ["紫微", "天府", "天机", "太阳", "武曲", "天同", "廉贞", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"],
  },
  {
    id: "palaces",
    title: "十二宫",
    desc: "命宫、官禄、财帛等宫位含义，理解人生不同面向的结构。",
    items: ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "奴仆", "官禄", "田宅", "福德", "父母"],
  },
  {
    id: "sihua",
    title: "四化",
    desc: "禄权科忌的动态变化，学习资源与节奏的管理视角。",
    items: ["化禄", "化权", "化科", "化忌", "生年四化", "飞化概念"],
  },
  {
    id: "sanhe",
    title: "三合",
    desc: "三方四正与格局思路，理解整体结构而非单点断语。",
    items: ["三方四正", "紫府同宫", "杀破狼", "机月同梁"],
  },
  {
    id: "cases",
    title: "经典案例",
    desc: "通过结构化案例学习如何阅读命盘，不作宿命式解读。",
    items: ["事业方向案例", "关系经营案例", "人生阶段案例"],
  },
] as const;

export default function KnowledgePage() {
  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <p className="section-label">知识学院</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-paper">紫微传统知识学习中心</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-paper/50">
            内容来自 Knowledge Core 知识体系，以学习为目的，帮助理解传统结构，不直接展示断语或预测结论。
          </p>

          <div className="mt-10 space-y-6">
            {CATEGORIES.map((cat) => (
              <section key={cat.id} className="surface-panel p-6">
                <h2 className="font-display text-xl font-semibold text-paper">{cat.title}</h2>
                <p className="mt-2 text-sm text-paper/55">{cat.desc}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {cat.items.map((item) => (
                    <span
                      key={item}
                      className="rounded-full border border-gold/20 bg-gold/5 px-3 py-1 text-xs text-gold/80"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </section>
            ))}
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Button href="/chart" variant="gold">
              结合命盘实践
            </Button>
            <Button href="/report" variant="outline">
              查看人生报告
            </Button>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
