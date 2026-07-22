export const SITE = {
  name: "紫微AI",
  nameEn: "Ziwei AI",
  tagline: "以千年星象智慧，洞见人生轨迹",
  description: "基于紫微斗数十二宫命盘，结合 AI 大语言模型的人生分析平台",
} as const;

export const NAV_LINKS = [
  { label: "产品介绍", href: "#features" },
  { label: "AI 规划", href: "#ai-planning" },
  { label: "关于", href: "#about" },
] as const;

export const FEATURES = [
  {
    icon: "palace",
    title: "十二宫命盘",
    description:
      "精准排盘，呈现命宫、财帛、官禄等十二宫位，还原传统紫微斗数完整结构。",
  },
  {
    icon: "star",
    title: "十四主星解析",
    description:
      "紫微、天机、太阳、武曲等主星落宫解读，揭示性格底色与天赋潜能。",
  },
  {
    icon: "sihua",
    title: "四化飞星",
    description:
      "禄、权、科、忌四化飞星动态追踪，洞察运势流转与人生关键节点。",
  },
  {
    icon: "timeline",
    title: "大限流年",
    description:
      "十年大运与流年运势联动分析，把握事业、感情、财富的时间节奏。",
  },
] as const;

export const AI_PLANNING_ITEMS = [
  {
    title: "性格深度画像",
    description: "AI 综合命盘主星与宫位，生成多维度性格雷达图与核心特质报告。",
  },
  {
    title: "事业财富规划",
    description: "结合官禄宫、财帛宫与大限走势，提供个性化职业发展建议。",
  },
  {
    title: "情感关系洞察",
    description: "分析夫妻宫、福德宫配置，解读感情模式与相处之道。",
  },
  {
    title: "流年运势预警",
    description: "AI 实时解读流年四化，提前洞察机遇与挑战，辅助决策。",
  },
] as const;
