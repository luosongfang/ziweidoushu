/** StandardChartSchema V2 — 对齐 POST /api/chart/create */

export type Gender = "male" | "female";
export type CalendarType = "solar" | "lunar";
export type SiHuaType = "禄" | "权" | "科" | "忌";
export type StarCategory = "main" | "lucky" | "sha" | "za";
export type StarType = "main" | "lucky" | "lu_cun" | "sha" | "za";

export interface ChartCreateRequest {
  name: string;
  gender: Gender;
  solar_date: string;
  time: string;
  location?: string;
  calendar_type?: CalendarType;
  is_leap_month?: boolean;
  persist?: boolean;
  user_id?: string;
  reference_year?: number;
}

export interface StarV2 {
  name: string;
  palace: string;
  branch: string;
  category: StarCategory;
  type: StarType;
  brightness?: string;
  sihua?: SiHuaType;
  isMain?: boolean;
}

export interface PalaceV2 {
  name: string;
  branch: string;
  ganzhi?: string;
  position: number;
  opposite: string;
  sanhe: string[];
  is_ming_gong: boolean;
  is_shen_gong: boolean;
  main_stars: StarV2[];
  lucky_stars: StarV2[];
  sha_stars: StarV2[];
  za_stars: StarV2[];
  transformations: Array<{ star: string; type: SiHuaType }>;
  daxian?: { palace: string; startAge: number; endAge: number } | null;
}

export interface FourTransformV2 {
  yearStem: string;
  lu: { star: string; palace: string; type: SiHuaType };
  quan: { star: string; palace: string; type: SiHuaType };
  ke: { star: string; palace: string; type: SiHuaType };
  ji: { star: string; palace: string; type: SiHuaType };
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
  shichen: string | { name: string; branch?: string };
}

export interface MetaV2 {
  name: string;
  gender: Gender;
  mingGong: string;
  shenGong: string;
  mingGongGanZhi?: string;
  wuxingJu: string;
  bureauNumber?: number;
  mingZhu?: string;
  shenZhu?: string;
  nayinElement?: string;
}

/** POST /api/chart/create 响应 — StandardChartSchema V2 */
export interface ChartCreateResponse {
  schema_version: "2.0";
  name: string;
  gender: Gender;
  birth: BirthInfo;
  meta: MetaV2;
  palaces: PalaceV2[];
  stars: {
    main: StarV2[];
    lucky: StarV2[];
    lu_cun: StarV2[];
    sha: StarV2[];
    za: StarV2[];
    all: StarV2[];
  };
  four_transform: FourTransformV2;
  brightness: Record<string, string>;
  sanhe: Record<string, string[]>;
  opposite: Record<string, string>;
  daxian: {
    direction: "forward" | "backward";
    ranges: Array<{ palace: string; startAge: number; endAge: number }>;
  };
  liunian: { year: number; branch: string; palace: string };
  xiaoxian: { enabled: boolean };
  trace: { traceId: string; steps: unknown[]; rulesVersion: string; source: string };
  warnings: string[];
  engine_version: string;
  rules_version: string;
  school: string;
  chart_id?: string | null;
  birth_profile_id?: string | null;
  persisted?: boolean;
}

export interface BirthFormData {
  name: string;
  gender: Gender;
  calendarType: CalendarType;
  date: string;
  time: string;
  location: string;
}

/** @deprecated V1 宫位结构，仅用于本地缓存迁移 */
export interface Palace {
  name: string;
  position: number;
  branch: string;
  ganzhi?: string;
  stars: Array<{ name: string; category?: string; sihua?: SiHuaType }>;
  transformations: Array<{ star: string; type: SiHuaType }>;
  is_ming_gong?: boolean;
  is_shen_gong?: boolean;
}
