/** 后端 Chart JSON V1.0 Final 类型（精简） */

export interface ApiStar {
  name: string;
  brightness?: string;
  sihua?: "禄" | "权" | "科" | "忌" | null;
  isMain?: boolean;
}

export interface ApiPalace {
  name: string;
  branch: string;
  mainStars: ApiStar[];
  auxStars: ApiStar[];
  shaStars?: ApiStar[];
  zaStars?: ApiStar[];
  daxian: { startAge: number; endAge: number };
  isMingGong?: boolean;
  isShenGong?: boolean;
}

export interface ChartApiOutput {
  version: string;
  meta: {
    name: string;
    gender: "male" | "female";
    mingGong: string;
    shenGong: string;
    wuxingJu: string;
    mingZhu: string;
    shenZhu: string;
  };
  birth: {
    solar: string;
    lunar: string;
    shichen: { name: string; range: string; branch: string };
    ganzhi: { year: string; month: string; day: string; hour: string };
  };
  palaces: ApiPalace[];
}

export interface BirthInputPayload {
  name: string;
  gender: "male" | "female";
  date: string;
  time: string;
  calendar_type?: "solar" | "lunar";
  location?: {
    country?: string;
    city?: string;
    longitude?: number;
    latitude?: number;
  };
  timezone?: string;
}

/** REF-01 基准盘出生信息 */
export const DEMO_BIRTH: BirthInputPayload = {
  name: "基准男盘",
  gender: "male",
  date: "1990-05-15",
  time: "14:30",
  location: { country: "China", city: "深圳", longitude: 114.0579 },
  timezone: "Asia/Shanghai",
};
