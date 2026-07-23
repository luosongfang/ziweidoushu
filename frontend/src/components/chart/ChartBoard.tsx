import type { ChartData, EarthlyBranch, Palace } from "@/types/chart";
import { BRANCH_GRID } from "@/lib/chartLayout";
import PalaceCell from "./PalaceCell";
import ChartCenter from "./ChartCenter";

interface ChartBoardProps {
  data: ChartData;
}

const BRANCHES = Object.keys(BRANCH_GRID) as EarthlyBranch[];

function buildBranchMap(palaces: Palace[]): Map<EarthlyBranch, Palace> {
  return new Map(palaces.map((p) => [p.branch, p]));
}

export default function ChartBoard({ data }: ChartBoardProps) {
  const branchMap = buildBranchMap(data.palaces);

  return (
    <div className="mx-auto w-full max-w-4xl">
      <div
        className="grid gap-1 sm:gap-1.5"
        style={{
          gridTemplateColumns: "repeat(4, 1fr)",
          gridTemplateRows: "repeat(4, 1fr)",
        }}
      >
        {BRANCHES.map((branch) => {
          const palace = branchMap.get(branch);
          if (!palace) return null;
          const { row, col } = BRANCH_GRID[branch];
          return (
            <div key={branch} style={{ gridRow: row + 1, gridColumn: col + 1 }}>
              <PalaceCell palace={palace} />
            </div>
          );
        })}

        <div
          className="min-h-[160px] sm:min-h-[200px]"
          style={{ gridRow: "2 / 4", gridColumn: "2 / 4" }}
        >
          <ChartCenter meta={data.meta} />
        </div>
      </div>

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
