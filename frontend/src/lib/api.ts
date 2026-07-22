import axios, { AxiosError } from "axios";
import type { ChartCreateRequest, ChartCreateResponse } from "@/types/ziwei";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** 调用 Phase 2 排盘引擎 */
export async function createChart(data: ChartCreateRequest): Promise<ChartCreateResponse> {
  try {
    const response = await client.post<ChartCreateResponse>("/api/chart/create", data);
    return response.data;
  } catch (err) {
    if (err instanceof AxiosError) {
      const detail =
        (err.response?.data as { detail?: string })?.detail ??
        err.message ??
        "排盘服务暂时不可用";
      throw new ApiError(detail, err.response?.status);
    }
    throw new ApiError("网络连接失败，请确认后端已启动");
  }
}

export { API_BASE };
