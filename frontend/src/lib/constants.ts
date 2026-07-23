export const SITE = {
  name: "Ziwei AI",
  nameZh: "紫微 AI",
  tagline: "探索传统智慧，发现更好的自己",
  subtitle:
    "基于紫微斗数传统知识体系，结合 AI 技术，帮助你进行人生规划与自我成长。",
  positioning: "传统文化学习 + 人生规划 AI 导师",
  notice:
    "本产品提供传统文化视角与自我认知参考，不作绝对预测，不替代专业咨询。",
} as const;

export const NAV_LINKS = [
  { label: "首页", href: "/" },
  { label: "排盘", href: "/chart" },
  { label: "AI 人生导师", href: "/advisor" },
  { label: "成长档案", href: "/profile" },
  { label: "会员中心", href: "/member" },
] as const;

export const LIFE_DOMAINS = [
  { key: "career", label: "事业", hint: "方向与节奏" },
  { key: "wealth", label: "财富", hint: "资源与结构" },
  { key: "relationship", label: "关系", hint: "相处与边界" },
  { key: "growth", label: "学习成长", hint: "能力与习惯" },
  { key: "family", label: "家庭", hint: "支持与责任" },
  { key: "choice", label: "人生选择", hint: "决策辅助" },
] as const;

export const ANALYSIS_MODULES = [
  { id: "personality", label: "性格优势", question: "请从传统文化视角分析我的性格优势与成长空间" },
  { id: "career", label: "事业方向", question: "请分析适合我的事业方向与现阶段可行动作" },
  { id: "wealth", label: "财富模式", question: "请分析我的财富结构特点与稳健理财建议" },
  { id: "relationship", label: "人际关系", question: "请分析我的人际相处模式与关系经营建议" },
  { id: "stage", label: "当前阶段", question: "请结合当前人生阶段给出规划参考" },
  { id: "growth", label: "成长建议", question: "请给出可执行的自我成长建议与反思问题" },
] as const;

export const MEMBERSHIP_PLANS = [
  {
    id: "basic",
    name: "普通会员",
    price: "29.9",
    period: "月",
    features: ["每月 10 次专家级解盘", "事业 / 财富 / 关系 / 阶段分析", "查看部分知识来源"],
    recommended: false,
  },
  {
    id: "vip",
    name: "VIP 会员",
    price: "299",
    period: "年",
    features: [
      "不限次数解盘",
      "开启 AI 人生导师",
      "赠送 300 积分 / 月",
      "连续上下文记忆 · 成长档案",
    ],
    recommended: true,
    pointsNote: "每次 AI 交流消耗 2 积分",
  },
  {
    id: "svip",
    name: "SVIP 会员",
    price: "699",
    period: "年",
    features: ["不限解盘", "不限 AI 交流", "高级模型优先", "完整知识引用 · 人生成长报告"],
    recommended: false,
  },
] as const;

export const FREE_BENEFITS = [
  "注册即可一次完整排盘",
  "首次赠送一次专业解盘",
] as const;

export const FREE_LIMITS = [
  "无法查看完整引用体系",
  "无法连续 AI 咨询",
] as const;

/** 安全表达提示 — 前端展示用 */
export const SAFE_PHRASE_HINTS = [
  "传统理论分析认为……",
  "可以作为自我探索参考……",
] as const;
