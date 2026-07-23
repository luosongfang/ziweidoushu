import type { ChartCreateResponse } from "@/types/ziwei";

export interface ChartInsights {
  mainStructure: string[];
  strengths: {
    thinking: string;
    action: string;
    resources: string;
  };
  lifeStage: {
    title: string;
    focus: string[];
  };
  growth: string[];
}

const STAR_TRAITS: Record<string, { thinking?: string; action?: string; resources?: string }> = {
  紫微: { thinking: "重视整体格局与长期方向", action: "倾向主导与统筹", resources: "善于整合人脉与平台" },
  天机: { thinking: "思维灵活、善于分析", action: "适应变化、快速调整", resources: "信息与策略是核心资源" },
  太阳: { thinking: "关注价值表达与影响力", action: "主动 outward、愿意承担", resources: "口碑与公众形象" },
  武曲: { thinking: "务实、结果导向", action: "执行力强、重视效率", resources: "技能与现金流管理" },
  天同: { thinking: "重视和谐与感受", action: "温和推进、避免硬碰", resources: "人际支持与情绪稳定" },
  廉贞: { thinking: "原则感强、边界清晰", action: "专注目标、有韧性", resources: "专业深度与规则意识" },
  天府: { thinking: "稳健保守、注重积累", action: "循序渐进、风险可控", resources: "储备与稳定基础" },
  太阴: { thinking: "细腻敏感、内省力强", action: "幕后策划、长期经营", resources: "内在积累与审美品味" },
  贪狼: { thinking: "多元兴趣、探索欲强", action: "善于开拓与社交", resources: "机会嗅觉与跨界连接" },
  巨门: { thinking: "表达与分析并重", action: "通过沟通推动进展", resources: "专业话语权" },
  天相: { thinking: "协调平衡、服务导向", action: "辅助型领导、重视流程", resources: "制度与团队支持" },
  天梁: { thinking: "责任感强、关注长期", action: "守护型、愿意扶持他人", resources: "经验与信任资本" },
  七杀: { thinking: "独立果断、竞争意识", action: "敢于突破、快节奏", resources: "魄力与行动力" },
  破军: { thinking: "创新变革、不喜守成", action: "破旧立新、敢试敢错", resources: "变革窗口与勇气" },
};

const DEFAULT_STRENGTHS = {
  thinking: "善于从传统结构中提取自我认知线索",
  action: "可根据阶段调整节奏，循序渐进",
  resources: "重视学习与复盘，持续积累个人优势",
};

export function buildChartInsights(chart: ChartCreateResponse): ChartInsights {
  const { meta, palaces, four_transform: fourHua, daxian } = chart;
  const ming = palaces.find((p) => p.is_ming_gong);
  const shen = palaces.find((p) => p.is_shen_gong);
  const mainStars = ming?.main_stars.map((s) => s.name) ?? [];

  const mainStructure = [
    `命宫位于 ${meta.mingGong}${ming?.ganzhi ? `（${ming.ganzhi}）` : ""}`,
    shen ? `身宫位于 ${meta.shenGong}` : "",
    `五行局：${meta.wuxingJu}`,
    mainStars.length > 0 ? `命宫主星：${mainStars.join("、")}` : "命宫无主星，需结合对宫与辅星综合理解",
    meta.mingZhu ? `命主：${meta.mingZhu}` : "",
    meta.shenZhu ? `身主：${meta.shenZhu}` : "",
  ].filter(Boolean);

  let strengths = { ...DEFAULT_STRENGTHS };
  for (const star of mainStars) {
    const trait = STAR_TRAITS[star];
    if (trait) {
      strengths = {
        thinking: trait.thinking ?? strengths.thinking,
        action: trait.action ?? strengths.action,
        resources: trait.resources ?? strengths.resources,
      };
      break;
    }
  }

  const daxianRange = daxian.ranges?.[0];
  const lifeStage = {
    title: daxianRange ? `当前大限 ${daxianRange.startAge}–${daxianRange.endAge} 岁（${daxianRange.palace}）` : "人生阶段概览",
    focus: daxianRange
      ? [
          `此阶段可关注「${daxianRange.palace}」相关主题`,
          "适合梳理优势与边界，设定阶段性目标",
          "重大决策建议结合现实条件与长期规划",
        ]
      : ["理解当前关注方向", "建立可执行的短期目标", "保持自我复盘与调整"],
  };

  const growth: string[] = [];
  if (fourHua) {
    growth.push(`化禄在 ${fourHua.lu.star}（${fourHua.lu.palace}）— 可主动发挥的优势方向`);
    growth.push(`化权在 ${fourHua.quan.star}（${fourHua.quan.palace}）— 适合承担责任的领域`);
    growth.push(`化科在 ${fourHua.ke.star}（${fourHua.ke.palace}）— 学习与表达加分项`);
    growth.push(`化忌在 ${fourHua.ji.star}（${fourHua.ji.palace}）— 需要留意的盲点，非负面定论`);
  } else {
    growth.push("从命宫主星结构出发，识别 1–2 个可强化优势");
    growth.push("结合当前阶段，设定可衡量的短期行动");
    growth.push("定期复盘，调整节奏与优先级");
  }

  return { mainStructure, strengths, lifeStage, growth };
}
