import type { ChartData } from "@/types/chart";

/**
 * 演示命盘数据
 * 1990-05-15 14:30 男 · 庚午年 · 命宫午 · 身宫戌
 * 待阶段 1 命盘引擎完成后替换为真实计算结果
 */
export const MOCK_CHART: ChartData = {
  meta: {
    name: "演示命盘",
    gender: "male",
    birthDate: "1990年5月15日",
    birthTime: "未时 (13:00–15:00)",
    calendar: "solar",
    lunarDate: "一九九〇年四月廿一",
    yearStemBranch: "庚午",
    monthStemBranch: "辛巳",
    dayStemBranch: "庚辰",
    hourStemBranch: "癸未",
    wuxingJu: "土五局",
    mingZhu: "贪狼",
    shenZhu: "天同",
    mingGong: "午",
    shenGong: "戌",
  },
  palaces: [
    {
      name: "兄弟",
      branch: "巳",
      isMingGong: false,
      mainStars: [{ name: "天机", brightness: "平" }],
      auxStars: [
        { name: "文昌", brightness: "" },
        { name: "天马", brightness: "" },
      ],
      daxian: { startAge: 12, endAge: 21 },
    },
    {
      name: "命宫",
      branch: "午",
      isMingGong: true,
      mainStars: [
        { name: "紫微", brightness: "庙" },
        { name: "七杀", brightness: "旺" },
      ],
      auxStars: [
        { name: "左辅", brightness: "" },
        { name: "天魁", brightness: "" },
      ],
      daxian: { startAge: 2, endAge: 11 },
    },
    {
      name: "父母",
      branch: "未",
      mainStars: [{ name: "天同", brightness: "不", sihua: "忌" }],
      auxStars: [
        { name: "陀罗", brightness: "" },
        { name: "封诰", brightness: "" },
      ],
      daxian: { startAge: 112, endAge: 121 },
    },
    {
      name: "福德",
      branch: "申",
      mainStars: [{ name: "武曲", brightness: "利", sihua: "权" }],
      auxStars: [
        { name: "禄存", brightness: "" },
        { name: "地空", brightness: "" },
      ],
      daxian: { startAge: 102, endAge: 111 },
    },
    {
      name: "官禄",
      branch: "戌",
      isShenGong: true,
      mainStars: [
        { name: "太阳", brightness: "陷", sihua: "禄" },
        { name: "天梁", brightness: "庙" },
      ],
      auxStars: [
        { name: "擎羊", brightness: "" },
        { name: "天刑", brightness: "" },
      ],
      daxian: { startAge: 82, endAge: 91 },
    },
    {
      name: "田宅",
      branch: "酉",
      mainStars: [{ name: "天相", brightness: "旺" }],
      auxStars: [
        { name: "右弼", brightness: "" },
        { name: "天钺", brightness: "" },
        { name: "凤阁", brightness: "" },
      ],
      daxian: { startAge: 92, endAge: 101 },
    },
    {
      name: "交友",
      branch: "亥",
      mainStars: [{ name: "巨门", brightness: "旺" }],
      auxStars: [
        { name: "文曲", brightness: "" },
        { name: "红鸾", brightness: "" },
      ],
      daxian: { startAge: 72, endAge: 81 },
    },
    {
      name: "夫妻",
      branch: "辰",
      mainStars: [
        { name: "廉贞", brightness: "利" },
        { name: "天府", brightness: "庙" },
      ],
      auxStars: [
        { name: "火星", brightness: "" },
        { name: "天喜", brightness: "" },
      ],
      daxian: { startAge: 32, endAge: 41 },
    },
    {
      name: "迁移",
      branch: "子",
      mainStars: [{ name: "破军", brightness: "庙" }],
      auxStars: [
        { name: "铃星", brightness: "" },
        { name: "地劫", brightness: "" },
      ],
      daxian: { startAge: 62, endAge: 71 },
    },
    {
      name: "疾厄",
      branch: "丑",
      mainStars: [{ name: "贪狼", brightness: "庙" }],
      auxStars: [
        { name: "天姚", brightness: "" },
        { name: "天哭", brightness: "" },
      ],
      daxian: { startAge: 52, endAge: 61 },
    },
    {
      name: "财帛",
      branch: "寅",
      mainStars: [{ name: "太阴", brightness: "旺", sihua: "科" }],
      auxStars: [
        { name: "天巫", brightness: "" },
        { name: "龙池", brightness: "" },
      ],
      daxian: { startAge: 42, endAge: 51 },
    },
    {
      name: "子女",
      branch: "卯",
      mainStars: [{ name: "天同", brightness: "平" }],
      auxStars: [
        { name: "天寿", brightness: "" },
        { name: "台辅", brightness: "" },
      ],
      daxian: { startAge: 22, endAge: 31 },
    },
  ],
};
