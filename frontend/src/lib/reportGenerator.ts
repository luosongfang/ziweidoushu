"use client";

import type { ChartCreateResponse } from "@/types/ziwei";

export interface ReportSection {
  id: string;
  title: string;
  content: string;
}

function findPalace(data: ChartCreateResponse, name: string) {
  return data.chart.palaces.find((p) => p.name === name);
}

function starList(palaceName: string, data: ChartCreateResponse): string {
  const palace = findPalace(data, palaceName);
  if (!palace) return "暂无主星数据";
  const mains = palace.stars.filter((s) => s.category === "main").map((s) => s.name);
  return mains.length ? mains.join("、") : "无主星";
}

/** 基于命盘真实数据生成报告摘要（非随机 mock） */
export function buildReportSections(data: ChartCreateResponse): ReportSection[] {
  const { chart, birth, name } = data;
  const gz = birth.ganzhi;
  const four = chart.four_hua;

  return [
    {
      id: "personality",
      title: "人格分析",
      content: `${name} 命宫在${chart.ming_gong}，身宫在${chart.shen_gong}，五行${chart.five_element}。命宫主星：${starList("命宫", data)}。命主${chart.ming_zhu ?? ""}、身主${chart.shen_zhu ?? ""}，整体性格底色由命宫与身宫共同塑造，呈现${chart.five_element}的能量特质。`,
    },
    {
      id: "talent",
      title: "天赋能力",
      content: `官禄宫主星：${starList("官禄", data)}；福德宫主星：${starList("福德", data)}。${four ? `生年${four.year_gan}年化科在${four.hua_ke.star}（${four.hua_ke.palace}），才学名声方面有先天优势。` : ""}建议发挥主星组合优势，在专注领域深耕。`,
    },
    {
      id: "career",
      title: "事业方向",
      content: `官禄宫：${starList("官禄", data)}。四化${four ? `化禄在${four.hua_lu.star}（${four.hua_lu.palace}）、化权在${four.hua_quan.star}（${four.hua_quan.palace}）` : "数据待补充"}。适合在能发挥领导力与专业能力的领域发展，关注大限经过官禄、迁移宫时的机遇。`,
    },
    {
      id: "wealth",
      title: "财富趋势",
      content: `财帛宫主星：${starList("财帛", data)}；田宅宫主星：${starList("田宅", data)}。${chart.five_element} 局财运节奏与理财风格相关，宜稳健规划，在大限走财帛、田宅时重点布局。`,
    },
    {
      id: "relationship",
      title: "感情关系",
      content: `夫妻宫主星：${starList("夫妻", data)}。${four ? `化忌在${four.hua_ji.star}（${four.hua_ji.palace}），感情与情绪面需多加觉察与沟通。` : ""}福德宫${starList("福德", data)}影响内在情感需求与相处模式。`,
    },
    {
      id: "health",
      title: "健康趋势",
      content: `疾厄宫主星：${starList("疾厄", data)}。建议关注${chart.five_element}对应脏腑系统的节律，保持规律作息；大限走疾厄宫时加强体检与压力管理。`,
    },
    {
      id: "decade",
      title: "未来十年趋势",
      content: `当前大限方向：${chart.daxian_direction === "forward" ? "顺行" : "逆行"}。${chart.daxian_ranges?.slice(0, 3).map((d) => `${d.start_age}-${d.end_age}岁走${d.palace}`).join("；") ?? "大限数据加载中"}。${chart.liu_nian?.palace ? `流年太岁在${chart.liu_nian.palace}，宜结合四化动态做年度规划。` : ""}`,
    },
  ];
}
