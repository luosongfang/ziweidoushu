import { NextRequest, NextResponse } from "next/server";

/**
 * 服务端代理 → FastAPI。
 * 仅使用 BACKEND_URL（不要用 NEXT_PUBLIC_* 暴露后端地址给浏览器侧配置）。
 * 本地未配置时回退 localhost，便于开发。
 */
const BACKEND_URL = (process.env.BACKEND_URL || "http://localhost:8000").replace(
  /\/$/,
  "",
);

function mapError(raw?: string | null): string {
  if (!raw) return "AI服务暂时不可用，请稍后再试。";
  if (raw.includes("未配置")) return "请配置AI服务。";
  if (raw.includes("调用失败") || raw.includes("暂时不可用") || raw.includes("返回为空")) {
    return "AI服务暂时不可用，请稍后再试。";
  }
  return raw;
}

export async function POST(request: NextRequest) {
  let body: { chart?: string; chartData?: string; prompt?: string };

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { success: false, error: "请求格式无效" },
      { status: 400 },
    );
  }

  const chartData = (body.chartData ?? body.chart ?? "").trim();
  const prompt = body.prompt ?? "";

  try {
    const response = await fetch(`${BACKEND_URL}/api/ai-test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chartData, prompt }),
      signal: AbortSignal.timeout(120_000),
    });

    const data = (await response.json().catch(() => null)) as {
      success?: boolean;
      result?: string;
      model?: string;
      error?: string;
      detail?: string;
    } | null;

    if (!response.ok || !data?.success) {
      return NextResponse.json(
        {
          success: false,
          error: mapError(data?.error ?? data?.detail),
        },
        { status: response.ok ? 200 : response.status >= 500 ? 503 : response.status },
      );
    }

    return NextResponse.json({
      success: true,
      result: data.result,
      model: data.model,
    });
  } catch {
    return NextResponse.json(
      { success: false, error: "AI服务暂时不可用，请稍后再试。" },
      { status: 503 },
    );
  }
}
