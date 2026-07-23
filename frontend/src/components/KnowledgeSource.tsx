import type { KnowledgeSourceItem } from "@/types/analysis";

interface KnowledgeSourceProps {
  sources?: KnowledgeSourceItem[];
  locked?: boolean;
  title?: string;
}

/** 知识来源引用展示 — 免费用户可锁定完整引用 */
export default function KnowledgeSource({
  sources = [],
  locked = false,
  title = "知识来源",
}: KnowledgeSourceProps) {
  return (
    <div className="surface-panel p-5">
      <div className="flex items-center justify-between gap-3">
        <h4 className="font-display text-base font-semibold text-paper">{title}</h4>
        {locked && (
          <span className="rounded-full border border-gold/30 px-2.5 py-0.5 text-[11px] text-gold">
            会员可查看完整引用
          </span>
        )}
      </div>

      {locked ? (
        <p className="mt-3 text-sm text-paper/45">
          完整知识引用体系对会员开放。当前仅展示部分来源线索，不作绝对预测。
        </p>
      ) : sources.length === 0 ? (
        <p className="mt-3 text-sm text-paper/40">暂无引用。分析仍可作为自我认知参考。</p>
      ) : (
        <ul className="mt-4 space-y-2">
          {sources.slice(0, 8).map((s, i) => (
            <li
              key={`${s.book || s.name || "src"}-${i}`}
              className="rounded-lg border border-paper/10 bg-ink/35 px-3 py-2 text-sm text-paper/75"
            >
              <span className="text-gold/90">{s.book || s.name || "知识条目"}</span>
              {s.page != null && <span className="text-paper/40"> · 第 {String(s.page)} 页</span>}
              {s.chapter && <span className="text-paper/40"> · {s.chapter}</span>}
              {s.category && <span className="text-paper/35"> · {s.category}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
