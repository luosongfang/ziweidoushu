interface AnalysisCardProps {
  title: string;
  traditional?: string[];
  modern?: string[];
  actions?: string[];
  loading?: boolean;
}

/** 分析模块卡片：传统依据 + 现代解释 + 行动建议 */
export default function AnalysisCard({
  title,
  traditional = [],
  modern = [],
  actions = [],
  loading,
}: AnalysisCardProps) {
  return (
    <article className="surface-panel p-5 sm:p-6">
      <h3 className="font-display text-xl font-semibold text-paper">{title}</h3>
      <p className="mt-1 text-xs text-paper/40">
        传统理论分析认为……可作为自我探索参考
      </p>

      {loading ? (
        <p className="mt-6 text-sm text-paper/50">
          正在结合知识库生成分析，首次约需 1–2 分钟，请稍候…
        </p>
      ) : (
        <div className="mt-5 space-y-5">
          <Block label="传统依据" items={traditional} empty="暂无传统依据摘录" />
          <Block label="现代解释" items={modern} empty="暂无现代解释" />
          <Block label="行动建议" items={actions} empty="暂无行动建议" accent />
        </div>
      )}
    </article>
  );
}

function Block({
  label,
  items,
  empty,
  accent,
}: {
  label: string;
  items: string[];
  empty: string;
  accent?: boolean;
}) {
  return (
    <div>
      <div className={`text-xs font-medium tracking-wide ${accent ? "text-gold" : "text-paper/45"}`}>
        {label}
      </div>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-paper/35">{empty}</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {items.map((item) => (
            <li
              key={item.slice(0, 24)}
              className="rounded-lg border border-paper/10 bg-ink/40 px-3 py-2 text-sm leading-relaxed text-paper/80"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
