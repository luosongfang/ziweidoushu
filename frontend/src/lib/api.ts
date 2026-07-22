import { adaptChartOutput } from "@/lib/chartAdapter";
import type { ChartData } from "@/types/chart";
import type { BirthInputPayload, ChartApiOutput } from "@/types/api";
import { DEMO_BIRTH } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

/** 使用出生信息排盘并转为前端格式 */
export async function generateChart(birth: BirthInputPayload = DEMO_BIRTH): Promise<ChartData> {
  const output = await postJson<ChartApiOutput>("/api/v1/charts/generate/birth-input", birth);
  return adaptChartOutput(output);
}

/** 默认演示盘（REF-01） */
export async function fetchDemoChart(): Promise<ChartData> {
  return generateChart(DEMO_BIRTH);
}

export { API_URL };
