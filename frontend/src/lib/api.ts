import axios, { AxiosError } from "axios";
import { getAuthHeaders } from "@/lib/auth/authService";
import type { ChartCreateRequest, ChartCreateResponse } from "@/types/ziwei";
import type { KnowledgeAnalyzeRequest, KnowledgeAnalyzeResponse } from "@/types/analysis";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const ANALYZE_TIMEOUT_MS = 180_000;

async function buildClient() {
  const authHeaders = await getAuthHeaders();
  return axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json", ...authHeaders },
    timeout: 90000,
  });
}

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function wrapError(err: unknown, fallback: string): never {
  if (err instanceof AxiosError) {
    if (err.code === "ECONNABORTED" || err.message.includes("timeout")) {
      throw new ApiError("分析耗时较长，请稍后重试或切换网络后再试", err.response?.status);
    }
    const detail =
      (err.response?.data as { detail?: string; error?: string })?.detail ??
      (err.response?.data as { error?: string })?.error ??
      err.message ??
      fallback;
    throw new ApiError(typeof detail === "string" ? detail : fallback, err.response?.status);
  }
  throw new ApiError(fallback);
}

/** Phase 2 排盘引擎 */
export async function createChart(data: ChartCreateRequest): Promise<ChartCreateResponse> {
  try {
    const client = await buildClient();
    const response = await client.post<ChartCreateResponse>("/api/chart/create", data);
    return response.data;
  } catch (err) {
    wrapError(err, "排盘服务暂时不可用");
  }
}

/** Knowledge Core V5.x 分析 */
export async function analyzeKnowledge(
  data: KnowledgeAnalyzeRequest,
): Promise<KnowledgeAnalyzeResponse> {
  try {
    const client = await buildClient();
    client.defaults.timeout = ANALYZE_TIMEOUT_MS;
    const response = await client.post<KnowledgeAnalyzeResponse>(
      "/api/v1/knowledge/analyze",
      data,
    );
    return response.data;
  } catch (err) {
    wrapError(err, "分析服务暂时不可用");
  }
}

export async function fetchMembershipPlans(): Promise<unknown[]> {
  try {
    const client = await buildClient();
    const response = await client.get("/api/v1/membership/plans");
    return Array.isArray(response.data) ? response.data : [];
  } catch {
    return [];
  }
}

export { API_BASE };
