import ChartView from "@/components/chart/ChartView";
import { fetchDemoChart } from "@/lib/api";
import { MOCK_CHART } from "@/lib/mockChartData";

export default async function ChartPage() {
  let chart = MOCK_CHART;
  let source: "engine" | "mock" = "mock";

  try {
    chart = await fetchDemoChart();
    source = "engine";
  } catch {
    // 后端未启动时降级为 mock，便于前端独立开发
  }

  return <ChartView data={chart} source={source} />;
}
