import type { EarthlyBranch, GridPosition, PalaceName } from "@/types/chart";

/**
 * 传统天盘地支定位（4×4 外圈，中心 2×2 为信息区）
 *
 * ┌────┬────┬────┬────┐
 * │ 巳 │ 午 │ 未 │ 申 │
 * ├────┼────┴────┼────┤
 * │ 辰 │  中心   │ 酉 │
 * ├────┤         ├────┤
 * │ 卯 │         │ 戌 │
 * ├────┼────┬────┼────┤
 * │ 寅 │ 丑 │ 子 │ 亥 │
 * └────┴────┴────┴────┘
 */
export const BRANCH_GRID: Record<EarthlyBranch, GridPosition> = {
  巳: { row: 0, col: 0 },
  午: { row: 0, col: 1 },
  未: { row: 0, col: 2 },
  申: { row: 0, col: 3 },
  辰: { row: 1, col: 0 },
  酉: { row: 1, col: 3 },
  卯: { row: 2, col: 0 },
  戌: { row: 2, col: 3 },
  寅: { row: 3, col: 0 },
  丑: { row: 3, col: 1 },
  子: { row: 3, col: 2 },
  亥: { row: 3, col: 3 },
};

/**
 * @deprecated 按宫名定位；排盘 UI 应使用 BRANCH_GRID
 */
export const PALACE_GRID: Record<PalaceName, GridPosition> = {
  兄弟: { row: 0, col: 0 },
  命宫: { row: 0, col: 1 },
  父母: { row: 0, col: 2 },
  福德: { row: 0, col: 3 },
  官禄: { row: 1, col: 0 },
  田宅: { row: 1, col: 3 },
  交友: { row: 2, col: 0 },
  夫妻: { row: 2, col: 3 },
  迁移: { row: 3, col: 0 },
  疾厄: { row: 3, col: 1 },
  财帛: { row: 3, col: 2 },
  子女: { row: 3, col: 3 },
};

/** 地支顺序（逆时针） */
export const BRANCHES = [
  "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥",
] as const;

/** 四化颜色映射 */
export const SIHUA_COLORS: Record<string, string> = {
  禄: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
  权: "text-purple-300 bg-purple-400/10 border-purple-400/30",
  科: "text-sky-300 bg-sky-400/10 border-sky-400/30",
  忌: "text-rose-400 bg-rose-400/10 border-rose-400/30",
};

/** 亮度显示映射 */
export const BRIGHTNESS_STYLE: Record<string, string> = {
  庙: "text-gold-light",
  旺: "text-gold",
  得: "text-white/90",
  利: "text-white/80",
  平: "text-white/60",
  不: "text-white/40",
  陷: "text-white/30",
};
