import Logo from "./Logo";
import { SITE } from "@/lib/constants";

const VALUES = ["传统智慧", "科学分析", "安全可靠", "成长陪伴"] as const;

export default function Footer() {
  return (
    <footer className="border-t border-paper/10 bg-ink-soft/40">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div className="max-w-md">
            <Logo size="sm" showSubtitle />
            <p className="mt-4 text-sm leading-relaxed text-paper/50">{SITE.subtitle}</p>
            <p className="mt-3 text-xs text-paper/35">{SITE.notice}</p>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {VALUES.map((v) => (
              <div
                key={v}
                className="rounded-xl border border-paper/10 bg-ink/40 px-3 py-3 text-center text-sm text-paper/70"
              >
                {v}
              </div>
            ))}
          </div>
        </div>
        <div className="mt-10 border-t border-paper/10 pt-6 text-center text-xs text-paper/30">
          © {new Date().getFullYear()} {SITE.name} · {SITE.nameZh}. 传统智慧学习 · AI 人生导师
        </div>
      </div>
    </footer>
  );
}
