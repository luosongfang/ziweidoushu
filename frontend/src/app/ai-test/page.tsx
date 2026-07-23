"use client";

import { useCallback, useMemo, useState } from "react";
import { Brain, Loader2, Sparkles } from "lucide-react";
import StarryBackground from "@/components/background/StarryBackground";
import Header from "@/components/layout/Header";
import { Button } from "@/components/ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { useChart } from "@/context/ChartContext";
import type { ChartCreateResponse } from "@/types/ziwei";

const PLACEHOLDER = `命宫：紫微天府
官禄宫：武曲天相
财帛宫：天府`;

function formatChartAsText(data: ChartCreateResponse): string {
  const shichen = typeof data.birth?.shichen === "string"
    ? data.birth.shichen
    : data.birth?.shichen?.name ?? "";
  const lines: string[] = [
    `姓名：${data.name}`,
    `性别：${data.gender === "male" ? "男" : "女"}`,
    `公历：${data.birth?.solar ?? ""}`,
    `农历：${data.birth?.lunar ?? ""}`,
    `命宫：${data.meta?.mingGong ?? ""}`,
    `身宫：${data.meta?.shenGong ?? ""}`,
    `五行局：${data.meta?.wuxingJu ?? ""}`,
    "",
    "【十二宫】",
  ];

  for (const p of data.palaces ?? []) {
    const stars = [
      ...p.main_stars.map((s) => s.name),
      ...p.lucky_stars.map((s) => s.name),
      ...p.sha_stars.map((s) => s.name),
      ...p.za_stars.map((s) => s.name),
    ].join("、") || "无主星标注";
    const hua = (p.transformations ?? [])
      .map((t) => `${t.star}化${t.type}`)
      .join("、");
    lines.push(
      `${p.name}（${p.branch ?? ""}）：${stars}${hua ? ` · ${hua}` : ""}`,
    );
  }

  return lines.join("\n");
}

function mapFriendlyError(raw?: string | null): string {
  if (!raw) return "AI服务暂时不可用，请稍后再试。";
  if (raw.includes("未配置") || raw.includes("请配置AI服务")) {
    return "请配置AI服务。";
  }
  if (
    raw.includes("调用失败") ||
    raw.includes("暂时不可用") ||
    raw.includes("返回为空")
  ) {
    return "AI服务暂时不可用，请稍后再试。";
  }
  return raw;
}

interface AiTestApiResponse {
  success: boolean;
  result?: string | null;
  error?: string | null;
  model?: string | null;
}

export default function AiTestPage() {
  const { chart, isHydrated } = useChart();
  const [chartData, setChartData] = useState(PLACEHOLDER);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [model, setModel] = useState<string | null>(null);

  const hasStoredChart = Boolean(isHydrated && chart);

  const loadStoredChart = useCallback(() => {
    if (!chart) {
      setError("暂无已生成命盘，请先前往 /chart 排盘");
      return;
    }
    setChartData(formatChartAsText(chart));
    setError(null);
  }, [chart]);

  const handleAnalyze = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setModel(null);

    try {
      const response = await fetch("/api/ai-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chartData, prompt }),
      });

      const data = (await response.json()) as AiTestApiResponse;

      if (!data.success) {
        setError(mapFriendlyError(data.error));
        return;
      }

      setResult(data.result ?? "");
      setModel(data.model ?? null);
    } catch {
      setError("AI服务暂时不可用，请稍后再试。");
    } finally {
      setLoading(false);
    }
  }, [chartData, prompt]);

  const resultBlocks = useMemo(() => {
    if (!result) return [];
    const parts = result
      .split(/\n(?=#{1,3}\s)/)
      .map((block) => block.trim())
      .filter(Boolean);
    return parts;
  }, [result]);

  return (
    <>
      <StarryBackground />
      <Header />
      <main className="min-h-screen px-4 pb-16 pt-24 sm:px-6">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-purple-glow/30 bg-purple-glow/10 px-4 py-1.5 text-xs text-purple-mist">
            <Brain className="h-3.5 w-3.5" />
            SiliconFlow · DeepSeek-V3
          </div>
          <h1 className="font-display text-3xl font-bold text-white sm:text-4xl">
            AI紫微<span className="text-gradient-gold">智能分析测试</span>
          </h1>
          <p className="mt-3 text-sm text-white/50 sm:text-base">
            输入命盘信息，测试大模型生成人生规划参考报告
          </p>
        </div>

        <div className="mx-auto mt-10 max-w-3xl space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-gold" />
                命盘输入
              </CardTitle>
              <CardDescription>
                可粘贴宫位文本，或加载 /chart 已生成的命盘摘要
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={loadStoredChart}
                  disabled={!hasStoredChart}
                >
                  加载已有命盘
                </Button>
                <Button type="button" variant="ghost" size="sm" href="/chart">
                  前往排盘
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="chartData">命盘文本</Label>
                <textarea
                  id="chartData"
                  value={chartData}
                  onChange={(e) => setChartData(e.target.value)}
                  rows={10}
                  placeholder={PLACEHOLDER}
                  disabled={loading}
                  className="flex w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 font-mono text-sm leading-relaxed text-white placeholder:text-white/30 backdrop-blur-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-glow/40 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="prompt">附加说明（可选）</Label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={2}
                  placeholder="例如：请侧重事业与财运方向"
                  disabled={loading}
                  className="flex w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/30 backdrop-blur-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-glow/40 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <Button
                type="button"
                variant="gold"
                size="lg"
                className="w-full sm:w-auto"
                onClick={handleAnalyze}
                disabled={loading || !chartData.trim()}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4" />
                    开始AI分析
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {error && (
            <Card className="border-red-500/30 bg-red-500/5">
              <CardContent className="pt-6">
                <p className="text-sm text-red-300">{error}</p>
              </CardContent>
            </Card>
          )}

          {result && (
            <Card className="border-purple-glow/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-4 w-4 text-gold" />
                  AI 返回结果
                </CardTitle>
                {model && <CardDescription>模型：{model}</CardDescription>}
              </CardHeader>
              <CardContent className="space-y-4">
                {resultBlocks.length > 1 ? (
                  resultBlocks.map((block, i) => {
                    const [titleLine, ...rest] = block.split("\n");
                    const title = titleLine.replace(/^#{1,3}\s*/, "").trim();
                    const body = rest.join("\n").trim();
                    return (
                      <div
                        key={`${title}-${i}`}
                        className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
                      >
                        <h3 className="mb-2 text-sm font-semibold text-gold-light">
                          {title}
                        </h3>
                        <p className="whitespace-pre-wrap text-sm leading-relaxed text-white/70">
                          {body}
                        </p>
                      </div>
                    );
                  })
                ) : (
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-white/70">
                    {result}
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}
