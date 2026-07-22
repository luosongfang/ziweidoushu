import type { ChartData, PalaceName, Star } from "@/types/chart";
import type { ApiPalace, ApiStar, ChartApiOutput } from "@/types/api";

const BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"] as const;

function formatSolarDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10);
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

function adaptStar(star: ApiStar): Star {
  return {
    name: star.name,
    brightness: (star.brightness || "") as Star["brightness"],
    sihua: star.sihua ?? undefined,
    isMain: star.isMain,
  };
}

function adaptPalace(palace: ApiPalace) {
  const auxStars = [
    ...(palace.auxStars ?? []),
    ...(palace.shaStars ?? []),
    ...(palace.zaStars ?? []),
  ].map(adaptStar);

  return {
    name: palace.name as PalaceName,
    branch: palace.branch as (typeof BRANCHES)[number],
    mainStars: palace.mainStars.map(adaptStar),
    auxStars,
    daxian: palace.daxian,
    isMingGong: palace.isMingGong,
    isShenGong: palace.isShenGong,
  };
}

/** 将后端 Chart JSON V1.0 Final 转为前端 ChartData */
export function adaptChartOutput(output: ChartApiOutput): ChartData {
  const { meta, birth } = output;
  return {
    meta: {
      name: meta.name,
      gender: meta.gender,
      birthDate: formatSolarDate(birth.solar),
      birthTime: `${birth.shichen.name} (${birth.shichen.range})`,
      calendar: "solar",
      lunarDate: birth.lunar,
      yearStemBranch: birth.ganzhi.year,
      monthStemBranch: birth.ganzhi.month,
      dayStemBranch: birth.ganzhi.day,
      hourStemBranch: birth.ganzhi.hour,
      wuxingJu: meta.wuxingJu,
      mingZhu: meta.mingZhu,
      shenZhu: meta.shenZhu,
      mingGong: meta.mingGong as ChartData["meta"]["mingGong"],
      shenGong: meta.shenGong as ChartData["meta"]["shenGong"],
    },
    palaces: output.palaces.map(adaptPalace),
  };
}
