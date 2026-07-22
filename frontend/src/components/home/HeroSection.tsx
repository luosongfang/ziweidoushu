import Button from "@/components/ui/Button";

export default function HeroSection() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-4 pt-24 pb-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        {/* Logo + 副标题 */}
        <div className="mb-6 animate-fade-in">
          <div className="font-display text-sm font-semibold tracking-[0.3em] text-gold-light uppercase">
            Ziwei AI
          </div>
          <p className="mt-2 text-lg text-purple-mist sm:text-xl">AI紫微 · 探索人生趋势</p>
        </div>

        {/* 主标题 */}
        <h1 className="animate-fade-in-up font-display text-3xl font-bold leading-snug tracking-tight sm:text-4xl md:text-5xl lg:text-6xl">
          <span className="text-white">用东方智慧，</span>
          <br />
          <span className="text-gradient-purple">连接 AI 时代的人生规划</span>
        </h1>

        <p className="animate-fade-in-up animation-delay-200 mx-auto mt-6 max-w-2xl text-base text-white/50 sm:text-lg">
          千年紫微斗数十二宫 · 十四主星 · 四化飞星
          <br className="hidden sm:block" />
          融合 AI 分析，洞见性格、事业、财富与情感趋势
        </p>

        <div className="animate-fade-in-up animation-delay-400 mt-10">
          <Button href="/chart" variant="gold" size="lg">
            立即排盘
          </Button>
        </div>

        <div className="animate-fade-in-up animation-delay-600 mt-16 grid grid-cols-3 gap-4 sm:gap-8">
          {[
            { value: "12", label: "宫位" },
            { value: "14", label: "主星" },
            { value: "AI", label: "解读" },
          ].map((stat) => (
            <div key={stat.label} className="glass-card px-3 py-4 sm:px-6 sm:py-5">
              <div className="text-xl font-bold text-gradient-gold sm:text-2xl">{stat.value}</div>
              <div className="mt-1 text-xs text-white/40 sm:text-sm">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 背景光效圆环 */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 animate-float opacity-20 sm:h-[700px] sm:w-[700px]">
        <div className="absolute inset-0 rounded-full bg-gradient-radial from-purple-glow/30 to-transparent blur-3xl" />
        <svg viewBox="0 0 400 400" className="h-full w-full" aria-hidden>
          <circle cx="200" cy="200" r="180" fill="none" stroke="#8b5cf6" strokeWidth="0.5" strokeDasharray="4 8" />
          <circle cx="200" cy="200" r="140" fill="none" stroke="#d4a853" strokeWidth="0.5" strokeDasharray="2 6" />
        </svg>
      </div>
    </section>
  );
}
