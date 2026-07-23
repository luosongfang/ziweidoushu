export const SITE = {
  name: "ZiweiX AI",
  nameZh: "紫微AI",
  tagline: "传统智慧 × AI人生导师",
  heroTitle: "探索传统紫微智慧，找到更清晰的人生方向。",
  heroDescription:
    "基于传统紫微斗数知识体系，结合 AI 分析技术，帮助你认识优势、理解人生阶段、辅助重要选择。",
  subtitle:
    "基于传统紫微斗数知识体系，结合 AI 分析技术，帮助你认识优势、理解人生阶段、辅助重要选择。",
  positioning: "传统智慧学习 + AI人生导师",
  notice:
    "AI 提供传统文化分析与成长建议，帮助你进行自我探索。不作绝对预测，不替代专业咨询。",
} as const;

export const NAV_LINKS = [
  { label: "首页", href: "/" },
  { label: "排盘", href: "/chart" },
  { label: "报告", href: "/report" },
  { label: "分析", href: "/analysis" },
  { label: "导师", href: "/advisor" },
  { label: "我的", href: "/profile" },
] as const;

export const MOBILE_NAV = [
  { label: "首页", href: "/", icon: "home" },
  { label: "排盘", href: "/chart", icon: "chart" },
  { label: "分析", href: "/analysis", icon: "analysis" },
  { label: "导师", href: "/advisor", icon: "advisor" },
  { label: "我的", href: "/profile", icon: "profile" },
] as const;

export const TRUST_CARDS = [
  {
    title: "传统知识体系",
    items: ["16册经典资料", "理论来源可追溯"],
  },
  {
    title: "AI 分析引擎",
    items: ["多维理论结合", "结构化分析"],
  },
  {
    title: "人生成长导师",
    items: ["不是预测未来", "而是帮助理解自己"],
  },
] as const;

export const FREE_EXPERIENCE_BENEFITS = [
  "基础排盘",
  "一次专业解读",
  "查看人生阶段分析",
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
  {
    id: "personality",
    label: "自我认知",
    question: "请从传统文化视角分析我的性格优势、思维模式与成长空间",
  },
  {
    id: "career",
    label: "事业探索",
    question: "请分析适合我的事业方向与现阶段可行动作",
  },
  {
    id: "wealth",
    label: "财富规划",
    question: "请分析我的资源结构特点与稳健规划建议",
  },
  {
    id: "relationship",
    label: "关系经营",
    question: "请分析我的人际相处模式与关系经营建议",
  },
  {
    id: "stage",
    label: "人生阶段",
    question: "请结合当前人生阶段给出关注方向与规划参考",
  },
  {
    id: "growth",
    label: "成长方向",
    question: "请给出可执行的自我成长建议与反思问题",
  },
] as const;

export const PLAN_LABELS: Record<string, string> = {
  free: "免费用户",
  basic: "普通会员",
  vip: "VIP 会员",
  svip: "SVIP 会员",
};

export const MEMBERSHIP_PLANS = [
  {
    id: "basic",
    name: "Basic",
    nameZh: "普通会员",
    price: "29.9",
    period: "月",
    features: ["每月 10 次深度分析", "完整分析报告", "成长档案"],
    recommended: false,
  },
  {
    id: "vip",
    name: "VIP",
    nameZh: "VIP 会员",
    price: "299",
    period: "月",
    features: ["不限报告", "300 积分 / 月", "AI 导师聊天", "连续上下文 · 成长档案"],
    recommended: true,
    pointsNote: "每次 AI 交流消耗 2 积分",
  },
  {
    id: "svip",
    name: "SVIP",
    nameZh: "SVIP 年度",
    price: "699",
    period: "年",
    features: ["不限分析", "不限 AI 导师", "高级模型优先", "完整知识引用 · 成长报告"],
    recommended: false,
  },
] as const;

export const FREE_BENEFITS = [
  "免费体验",
  "一次完整基础分析",
  "基础排盘与阶段参考",
] as const;

export const FREE_LIMITS = [
  "完整分析报告需升级",
  "AI 导师连续对话需 VIP 及以上",
] as const;

export const ADVISOR_QUICK_QUESTIONS = [
  "事业方向",
  "创业选择",
  "个人优势",
  "人生阶段",
  "关系经营",
  "成长规划",
] as const;

export const ANALYSIS_LOADING_STEPS = [
  "排盘计算",
  "星曜结构分析",
  "理论匹配",
  "人生阶段分析",
  "生成成长建议",
] as const;

/** 安全表达提示 — 前端展示用 */
export const SAFE_PHRASE_HINTS = [
  "传统理论分析认为……",
  "可以作为自我探索参考……",
] as const;
