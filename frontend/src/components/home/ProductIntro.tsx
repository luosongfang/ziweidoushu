import FeatureCard from "./FeatureCard";
import { FEATURES } from "@/lib/constants";

export default function ProductIntro() {
  return (
    <section id="features" className="relative px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
      <div className="mx-auto max-w-7xl">
        {/* 区块标题 */}
        <div className="mb-12 text-center sm:mb-16">
          <span className="text-xs font-medium tracking-[0.3em] text-purple-mist uppercase">
            Core Features
          </span>
          <h2 className="mt-3 font-display text-3xl font-bold text-white sm:text-4xl md:text-5xl">
            传统命理
            <span className="text-gradient-gold"> × </span>
            现代 AI
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-base text-white/50 sm:text-lg">
            完整继承紫微斗数排盘体系，以 AI 大语言模型赋予千年星象智慧全新的解读深度。
          </p>
        </div>

        {/* 功能卡片网格 */}
        <div className="grid gap-4 sm:grid-cols-2 sm:gap-6 lg:gap-8">
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>

        {/* 命盘预览装饰 */}
        <div className="mt-16 flex justify-center sm:mt-20">
          <div className="glass-card relative w-full max-w-3xl overflow-hidden p-6 sm:p-10">
            <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-purple-glow/10 blur-3xl" />
            <div className="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-gold/10 blur-3xl" />

            <div className="relative grid grid-cols-4 gap-1.5 sm:gap-2">
              {["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "交友", "官禄", "田宅", "福德", "父母"].map(
                (name, i) => (
                  <div
                    key={name}
                    className={`flex aspect-square flex-col items-center justify-center rounded-lg border text-center transition-colors ${
                      i === 0
                        ? "border-gold/40 bg-gold/10 shadow-glow-gold"
                        : "border-white/10 bg-white/[0.03] hover:border-purple-glow/20"
                    }`}
                  >
                    <span className={`text-[10px] sm:text-xs ${i === 0 ? "text-gold-light" : "text-white/40"}`}>
                      {name}
                    </span>
                    {i === 0 && (
                      <span className="mt-0.5 text-[9px] text-gold/70 sm:text-[10px]">紫微·七杀</span>
                    )}
                  </div>
                )
              )}
            </div>

            <p className="mt-6 text-center text-xs text-white/30 sm:text-sm">
              十二宫命盘预览 · 精准还原传统紫微斗数结构
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
