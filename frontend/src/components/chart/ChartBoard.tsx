import type { ChartData, Palace, PalaceName } from "@/types/chart";
import PalaceCell from "./PalaceCell";
import ChartCenter from "./ChartCenter";

interface ChartBoardProps {
  data: ChartData;
}

/** 将宫位数组转为「宫名 → 宫位」映射 */
function buildPalaceMap(palaces: Palace[]): Map<PalaceName, Palace> {
  return new Map(palaces.map((p) => [p.name, p]));
}

export default function ChartBoard({ data }: ChartBoardProps) {
  const palaceMap = buildPalaceMap(data.palaces);

  /** 按传统 4×4 布局取宫位 */
  const getPalace = (name: PalaceName) => {
    const palace = palaceMap.get(name);
    if (!palace) throw new Error(`Missing palace: ${name}`);
    return palace;
  };

  return (
    <div className="mx-auto w-full max-w-4xl">
      {/*
        传统十二宫专业排盘：4 列 × 4 行
        中心 grid-area 合并为信息区
      */}
      <div
        className="grid gap-1 sm:gap-1.5"
        style={{
          gridTemplateColumns: "repeat(4, 1fr)",
          gridTemplateRows: "repeat(4, 1fr)",
        }}
      >
        {/* 第一行 */}
        <div style={{ gridRow: 1, gridColumn: 1 }}>
          <PalaceCell palace={getPalace("兄弟")} />
        </div>
        <div style={{ gridRow: 1, gridColumn: 2 }}>
          <PalaceCell palace={getPalace("命宫")} />
        </div>
        <div style={{ gridRow: 1, gridColumn: 3 }}>
          <PalaceCell palace={getPalace("父母")} />
        </div>
        <div style={{ gridRow: 1, gridColumn: 4 }}>
          <PalaceCell palace={getPalace("福德")} />
        </div>

        {/* 左侧列 */}
        <div style={{ gridRow: 2, gridColumn: 1 }}>
          <PalaceCell palace={getPalace("官禄")} />
        </div>
        <div style={{ gridRow: 3, gridColumn: 1 }}>
          <PalaceCell palace={getPalace("交友")} />
        </div>

        {/* 中心信息区（合并 2×2） */}
        <div
          className="min-h-[160px] sm:min-h-[200px]"
          style={{ gridRow: "2 / 4", gridColumn: "2 / 4" }}
        >
          <ChartCenter meta={data.meta} />
        </div>

        {/* 右侧列 */}
        <div style={{ gridRow: 2, gridColumn: 4 }}>
          <PalaceCell palace={getPalace("田宅")} />
        </div>
        <div style={{ gridRow: 3, gridColumn: 4 }}>
          <PalaceCell palace={getPalace("夫妻")} />
        </div>

        {/* 第四行 */}
        <div style={{ gridRow: 4, gridColumn: 1 }}>
          <PalaceCell palace={getPalace("迁移")} />
        </div>
        <div style={{ gridRow: 4, gridColumn: 2 }}>
          <PalaceCell palace={getPalace("疾厄")} />
        </div>
        <div style={{ gridRow: 4, gridColumn: 3 }}>
          <PalaceCell palace={getPalace("财帛")} />
        </div>
        <div style={{ gridRow: 4, gridColumn: 4 }}>
          <PalaceCell palace={getPalace("子女")} />
        </div>
      </div>

      {/* 四化图例 */}
      <div className="mt-3 flex flex-wrap items-center justify-center gap-3 sm:mt-4 sm:gap-4">
        {(["禄", "权", "科", "忌"] as const).map((type) => (
          <div key={type} className="flex items-center gap-1.5">
            <span
              className={`flex h-4 w-4 items-center justify-center rounded border text-[10px] font-medium ${
                type === "禄"
                  ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-400"
                  : type === "权"
                    ? "border-purple-400/30 bg-purple-400/10 text-purple-300"
                    : type === "科"
                      ? "border-sky-400/30 bg-sky-400/10 text-sky-300"
                      : "border-rose-400/30 bg-rose-400/10 text-rose-400"
              }`}
            >
              {type}
            </span>
            <span className="text-[10px] text-white/30 sm:text-xs">
              {type === "禄" ? "化禄" : type === "权" ? "化权" : type === "科" ? "化科" : "化忌"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
