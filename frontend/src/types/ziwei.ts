/** Phase 2/3 紫微命盘 API 类型 — 对齐 POST /api/chart/create */

export type Gender = "male" | "female";
export type CalendarType = "solar" | "lunar";
export type SiHuaType = "禄" | "权" | "科" | "忌";

export interface ChartCreateRequest {
  name: string;
  gender: Gender;
  solar_date: string;
  time: string;
  location?: string;
  persist?: boolean;
}

export interface PalaceStar {
  name: string;
  category?: "main" | "aux" | "sha" | "za" | "daxian" | string;
  sihua?: SiHuaType;
}

export interface PalaceTransformation {
  star: string;
  type: SiHuaType;
}

/** 单宫结构 */
export interface Palace {
  name: string;
  position: number;
  branch: string;
  ganzhi?: string;
  stars: PalaceStar[];
  transformations: PalaceTransformation[];
  is_ming_gong?: boolean;
  is_shen_gong?: boolean;
}

/** 命盘核心结构 */
export interface ZiweiChart {
  ming_gong: string;
  shen_gong: string;
  five_element: string;
  ming_zhu?: string;
  shen_zhu?: string;
  palaces: Palace[];
  four_hua?: FourHuaSummary;
  main_stars?: Array<{ name: string; palace?: string; branch?: string }>;
  daxian_direction?: string;
  daxian_ranges?: Array<{ palace: string; start_age: number; end_age: number }>;
  liu_nian?: { year?: number; branch?: string; palace?: string };
}

export interface FourHuaSummary {
  year_gan: string;
  hua_lu: { star: string; palace: string; type: string };
  hua_quan: { star: string; palace: string; type: string };
  hua_ke: { star: string; palace: string; type: string };
  hua_ji: { star: string; palace: string; type: string };
}

export interface BirthInfo {
  solar: string;
  lunar: string;
  lunar_detail: {
    lunar_year: number;
    lunar_month: number;
    lunar_day: number;
    is_leap: boolean;
  };
  year_gan: string;
  year_zhi: string;
  ganzhi: {
    year_gan: string;
    year_zhi: string;
    month_gan: string;
    month_zhi: string;
    day_gan: string;
    day_zhi: string;
    hour_gan: string;
    hour_zhi: string;
  };
  shichen: string;
}

export interface ChartCreateResponse {
  name: string;
  gender: Gender;
  birth: BirthInfo;
  chart: ZiweiChart & {
    five_element_detail?: Record<string, unknown>;
    ziwei?: Record<string, unknown>;
    tianfu?: Record<string, unknown>;
    lucky_stars?: Array<{ name: string; palace: string }>;
    evil_stars?: Array<{ name: string; palace: string }>;
  };
  engine_version: string;
  rules_version: string;
  chart_id?: string | null;
}

export interface BirthFormData {
  name: string;
  gender: Gender;
  calendarType: CalendarType;
  date: string;
  time: string;
  location: string;
}
