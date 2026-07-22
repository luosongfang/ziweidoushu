import Button from "@/components/ui/Button";
import { SITE } from "@/lib/constants";

export default function HeroSection() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-4 pt-24 pb-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        {/* 标签 */}
        <div
          className="mb-6 inline-flex animate-fade-in items-center gap-2 rounded-full border border-gold/20 bg-gold/5 px-4 py-1.5"
        >
          <span className="h-1.5 w-1.5 animate-twinkle rounded-full bg-gold" />
          <span className="text-xs tracking-widest text-gold-light uppercase">
            Ziwei Dou Shu × AI
          </span>
        </div>

        {/* 主标题 */}
        <h1 className="animate-fade-in-up font-display text-4xl font-bold leading-tight tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
          <span className="text-white">洞见命盘</span>
          <br />
          <span className="text-gradient-purple">智绘人生</span>
        </h1>

        {/* 副标题 */}
        <p className="animate-fade-in-up animation-delay-200 mx-auto mt-6 max-w-2xl text-base leading-relaxed text-white/60 sm:text-lg md:text-xl">
          {SITE.tagline}
          <br className="hidden sm:block" />
          千年紫微斗数智慧，融合 AI 大模型，为你解读十二宫命盘、四化飞星与大限流年。
        </p>

        {/* CTA 按钮组 */}
        <div className="animate-fade-in-up animation-delay-400 mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button href="/chart" variant="gold" size="lg">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
              />
            </svg>
            开始生成命盘
          </Button>
          <Button href="#ai-planning" variant="ghost" size="lg">
            了解 AI 人生规划
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
            </svg>
          </Button>
        </div>

        {/* 数据指标 */}
        <div className="animate-fade-in-up animation-delay-600 mt-16 grid grid-cols-3 gap-4 sm:gap-8">
          {[
            { value: "12", label: "宫位解析" },
            { value: "14", label: "主星体系" },
            { value: "AI", label: "智能解读" },
          ].map((stat) => (
            <div key={stat.label} className="glass-card px-3 py-4 sm:px-6 sm:py-5">
              <div className="text-xl font-bold text-gradient-gold sm:text-2xl">
                {stat.value}
              </div>
              <div className="mt-1 text-xs text-white/40 sm:text-sm">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 装饰性命盘圆环 */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 animate-float opacity-20 sm:h-[700px] sm:w-[700px]">
        <svg viewBox="0 0 400 400" className="h-full w-full" aria-hidden>
          <circle cx="200" cy="200" r="180" fill="none" stroke="#8b5cf6" strokeWidth="0.5" strokeDasharray="4 8" />
          <circle cx="200" cy="200" r="140" fill="none" stroke="#d4a853" strokeWidth="0.5" strokeDasharray="2 6" />
          <circle cx="200" cy="200" r="100" fill="none" stroke="#8b5cf6" strokeWidth="0.3" />
          {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => {
            const rad = (deg * Math.PI) / 180;
            const x = 200 + 180 * Math.cos(rad);
            const y = 200 + 180 * Math.sin(rad);
            return <circle key={deg} cx={x} cy={y} r="2" fill="#d4a853" opacity="0.6" />;
          })}
        </svg>
      </div>
    </section>
  );
}
