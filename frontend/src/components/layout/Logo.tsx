import Link from "next/link";
import { SITE } from "@/lib/constants";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showSubtitle?: boolean;
}

const sizeMap = {
  sm: { icon: "h-7 w-7", title: "text-base", sub: "text-[10px]" },
  md: { icon: "h-9 w-9", title: "text-lg", sub: "text-xs" },
  lg: { icon: "h-12 w-12", title: "text-2xl", sub: "text-sm" },
};

export default function Logo({ size = "md", showSubtitle = true }: LogoProps) {
  const s = sizeMap[size];

  return (
    <Link href="/" className="group flex items-center gap-3">
      {/* 星象 Logo 图标 */}
      <div
        className={`${s.icon} relative flex shrink-0 items-center justify-center rounded-xl border border-gold/30 bg-gradient-to-br from-purple-deep/60 to-void-100 shadow-glow-gold transition-transform duration-300 group-hover:scale-105`}
      >
        <svg
          viewBox="0 0 32 32"
          fill="none"
          className="h-[55%] w-[55%]"
          aria-hidden
        >
          <polygon
            points="16,4 19,13 28,13 21,19 24,28 16,22 8,28 11,19 4,13 13,13"
            fill="url(#goldGrad)"
            stroke="#f0d78c"
            strokeWidth="0.5"
          />
          <circle cx="16" cy="16" r="3" fill="#8b5cf6" opacity="0.8" />
          <defs>
            <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f0d78c" />
              <stop offset="100%" stopColor="#b8860b" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="flex flex-col">
        <span className={`${s.title} font-display font-semibold tracking-wide text-white`}>
          {SITE.name}
          <span className="ml-1.5 text-gradient-gold">2.0</span>
        </span>
        {showSubtitle && (
          <span className={`${s.sub} tracking-[0.2em] text-white/40 uppercase`}>
            {SITE.nameEn}
          </span>
        )}
      </div>
    </Link>
  );
}
