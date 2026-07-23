import Link from "next/link";
import { SITE } from "@/lib/constants";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showSubtitle?: boolean;
}

const sizeMap = {
  sm: { mark: "h-8 w-8 text-sm", title: "text-base", zh: "text-[10px]" },
  md: { mark: "h-10 w-10 text-base", title: "text-lg", zh: "text-[11px]" },
  lg: { mark: "h-12 w-12 text-lg", title: "text-2xl", zh: "text-xs" },
};

export default function Logo({ size = "md", showSubtitle = false }: LogoProps) {
  const s = sizeMap[size];
  return (
    <Link href="/" className="group flex items-center gap-3">
      <div
        className={`${s.mark} flex items-center justify-center rounded-full border border-gold/40 bg-ink-soft font-display font-semibold text-gold transition group-hover:border-gold`}
      >
        紫
      </div>
      <div>
        <div className={`${s.title} font-display font-semibold tracking-wide text-paper`}>
          {SITE.name}
        </div>
        <div className={`${s.zh} tracking-wider text-gold/70`}>{SITE.nameZh}</div>
        {showSubtitle && (
          <div className="mt-0.5 text-[11px] text-paper/40">{SITE.tagline}</div>
        )}
      </div>
    </Link>
  );
}
