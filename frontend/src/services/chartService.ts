import axios from "axios";
import { getAuthHeaders } from "@/lib/auth/authService";
import { createChart as apiCreateChart } from "@/lib/api";
import type { ChartCreateRequest, ChartCreateResponse } from "@/types/ziwei";
import type { ChartInsights } from "@/lib/chartInsights";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SavedChartSummary {
  id: string;
  name: string;
  is_default: boolean;
  ming_gong: string;
  five_element: string;
  birth_date?: string | null;
  created_at: string;
}

export interface SavedChartDetail {
  id: string;
  user_id: string;
  name: string;
  is_default: boolean;
  chart_data: Record<string, unknown>;
  birth_info: Record<string, unknown>;
  birth_date?: string | null;
  birth_time?: string | null;
  birth_place?: string | null;
  gender?: string | null;
  created_at: string;
}

export interface UserProfile {
  id: string;
  auth_user_id: string;
  nickname: string;
  avatar_url?: string | null;
  email?: string | null;
  membership: string;
  points: number;
}

async function authedClient() {
  const headers = await getAuthHeaders();
  return axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json", ...headers },
    timeout: 90000,
  });
}

export async function createChart(
  data: ChartCreateRequest & { user_id?: string },
): Promise<ChartCreateResponse> {
  return apiCreateChart(data);
}

function parseBirthMeta(chart: ChartCreateResponse) {
  const solar = chart.birth.solar || "";
  return {
    birth_date: solar.slice(0, 10) || undefined,
    birth_time: undefined as string | undefined,
    birth_place: undefined as string | undefined,
    gender: chart.gender,
  };
}

export async function saveChart(
  chart: ChartCreateResponse,
  options?: { setDefault?: boolean },
): Promise<SavedChartDetail> {
  const client = await authedClient();
  const meta = parseBirthMeta(chart);
  const response = await client.post<SavedChartDetail>("/api/user/charts", {
    name: chart.name || "我的命盘",
    chart_data: chart,
    birth_info: { ...chart.birth, gender: chart.gender, display_name: chart.name },
    birth_date: meta.birth_date,
    birth_time: meta.birth_time,
    birth_place: meta.birth_place,
    gender: meta.gender,
    set_default: options?.setDefault ?? true,
  });
  return response.data;
}

export async function saveAnalysisSnapshot(
  chart: ChartCreateResponse,
  insights: ChartInsights,
): Promise<void> {
  const client = await authedClient();
  const summary = [
    ...insights.mainStructure.slice(0, 2),
    insights.strengths.thinking,
    insights.lifeStage.title,
    ...insights.growth.slice(0, 2),
  ]
    .filter(Boolean)
    .join("；");
  await client.post("/api/user/history", {
    chart_id: chart.chart_id ?? null,
    question: "命盘概览分析",
    analysis_type: "overview",
    summary,
  });
}

export async function getUserProfile(): Promise<UserProfile | null> {
  try {
    const client = await authedClient();
    const response = await client.get<UserProfile>("/api/user/profile");
    return response.data;
  } catch {
    return null;
  }
}

export async function getUserCharts(): Promise<SavedChartSummary[]> {
  const client = await authedClient();
  const response = await client.get<SavedChartSummary[]>("/api/user/charts");
  return response.data;
}

export async function loadSavedChart(chartId: string): Promise<ChartCreateResponse | null> {
  const client = await authedClient();
  const response = await client.get<SavedChartDetail>(`/api/user/charts/${chartId}`);
  const detail = response.data;
  const raw = detail.chart_data as Partial<ChartCreateResponse> & { chart?: ChartCreateResponse["palaces"] };

  if (raw.schema_version === "2.0" && raw.meta && raw.palaces) {
    return {
      ...(raw as ChartCreateResponse),
      name: detail.name || raw.name || "我的命盘",
      gender: ((detail.gender || raw.gender || "male") as ChartCreateResponse["gender"]),
      birth: (detail.birth_info as ChartCreateResponse["birth"]) || raw.birth!,
      chart_id: detail.id,
      persisted: true,
    };
  }

  return null;
}

export async function setDefaultChart(chartId: string): Promise<SavedChartDetail> {
  const client = await authedClient();
  const response = await client.post<SavedChartDetail>(`/api/v1/user/charts/${chartId}/default`);
  return response.data;
}
