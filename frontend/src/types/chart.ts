/** 四化类型 */
export type SiHuaType = "禄" | "权" | "科" | "忌";

/** 星曜亮度 */
export type Brightness =
  | "庙"
  | "旺"
  | "得"
  | "利"
  | "平"
  | "不"
  | "陷"
  | "";

/** 地支 */
export type EarthlyBranch =
  | "子"
  | "丑"
  | "寅"
  | "卯"
  | "辰"
  | "巳"
  | "午"
  | "未"
  | "申"
  | "酉"
  | "戌"
  | "亥";

/** 宫位名称 */
export type PalaceName =
  | "命宫"
  | "兄弟"
  | "夫妻"
  | "子女"
  | "财帛"
  | "疾厄"
  | "迁移"
  | "交友"
  | "官禄"
  | "田宅"
  | "福德"
  | "父母";

/** 单颗星曜 */
export interface Star {
  name: string;
  brightness?: Brightness;
  sihua?: SiHuaType;
  /** 是否为主星 */
  isMain?: boolean;
}

/** 大限信息 */
export interface DaXian {
  startAge: number;
  endAge: number;
}

/** 单个宫位 */
export interface Palace {
  name: PalaceName;
  branch: EarthlyBranch;
  ganzhi?: string;
  mainStars: Star[];
  auxStars: Star[];
  shaStars?: Star[];
  daxian: DaXian;
  /** 是否为命宫 */
  isMingGong?: boolean;
  /** 是否为身宫 */
  isShenGong?: boolean;
}

/** 命盘元信息 */
export interface ChartMeta {
  name: string;
  gender: "male" | "female";
  birthDate: string;
  birthTime: string;
  calendar: "solar" | "lunar";
  lunarDate: string;
  yearStemBranch: string;
  monthStemBranch: string;
  dayStemBranch: string;
  hourStemBranch: string;
  wuxingJu: string;
  mingZhu: string;
  shenZhu: string;
  mingGong: EarthlyBranch;
  shenGong: EarthlyBranch;
}

/** 完整命盘 */
export interface ChartData {
  meta: ChartMeta;
  palaces: Palace[];
}

/** 四宫格布局坐标 */
export interface GridPosition {
  row: number;
  col: number;
}

/** 带布局位置的宫位 */
export interface PositionedPalace extends Palace {
  grid: GridPosition;
}
