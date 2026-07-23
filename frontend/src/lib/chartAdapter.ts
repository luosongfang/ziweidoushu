import type { ChartData, EarthlyBranch, PalaceName, Star } from "@/types/chart";
import type { ApiPalace, ApiStar, ChartApiOutput } from "@/types/api";
import type { ChartCreateResponse, StarV2 } from "@/types/ziwei";

function formatSolarDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10);
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

function shichenLabel(shichen: ChartCreateResponse["birth"]["shichen"]): string {
  return typeof shichen === "string" ? shichen : shichen.name;
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
    branch: palace.branch as EarthlyBranch,
    mainStars: palace.mainStars.map(adaptStar),
    auxStars,
    daxian: palace.daxian,
    isMingGong: palace.isMingGong,
    isShenGong: palace.isShenGong,
  };
}

function adaptV2Star(star: StarV2): Star {
  return {
    name: star.name,
    brightness: (star.brightness || "") as Star["brightness"],
    sihua: star.sihua,
    isMain: star.isMain ?? star.category === "main",
  };
}

/** 将 StandardChartSchema V2 响应转为专业排盘 ChartData */
export function adaptChartCreateResponse(response: ChartCreateResponse): ChartData {
  const { birth, meta, palaces } = response;
  const g = birth.ganzhi;

  return {
    meta: {
      name: response.name,
      gender: response.gender,
      birthDate: formatSolarDate(birth.solar),
      birthTime: shichenLabel(birth.shichen),
      calendar: "solar",
      lunarDate: birth.lunar,
      yearStemBranch: `${g.year_gan}${g.year_zhi}`,
      monthStemBranch: `${g.month_gan}${g.month_zhi}`,
      dayStemBranch: `${g.day_gan}${g.day_zhi}`,
      hourStemBranch: `${g.hour_gan}${g.hour_zhi}`,
      wuxingJu: meta.wuxingJu,
      mingZhu: meta.mingZhu ?? "",
      shenZhu: meta.shenZhu ?? "",
      mingGong: meta.mingGong as EarthlyBranch,
      shenGong: meta.shenGong as EarthlyBranch,
    },
    palaces: palaces.map((palace) => ({
      name: palace.name as PalaceName,
      branch: palace.branch as EarthlyBranch,
      ganzhi: palace.ganzhi,
      mainStars: palace.main_stars.map(adaptV2Star),
      auxStars: [...palace.lucky_stars, ...palace.za_stars].map(adaptV2Star),
      shaStars: palace.sha_stars.map(adaptV2Star),
      daxian: {
        startAge: palace.daxian?.startAge ?? 0,
        endAge: palace.daxian?.endAge ?? 0,
      },
      isMingGong: palace.is_ming_gong,
      isShenGong: palace.is_shen_gong,
    })),
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
