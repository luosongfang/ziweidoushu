import Button from "@/components/ui/Button";
import { AI_PLANNING_ITEMS } from "@/lib/constants";

export default function AILifePlanning() {
  return (
    <section id="ai-planning" className="relative px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          {/* 左侧：AI 助手视觉 */}
          <div className="relative order-2 lg:order-1">
            <div className="glass-card relative overflow-hidden p-6 sm:p-8">
              {/* 模拟 AI 对话界面 */}
              <div className="mb-4 flex items-center gap-3 border-b border-white/5 pb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-purple-glow to-purple-deep">
                  <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <div className="text-sm font-medium text-white">AI 人生规划师</div>
                  <div className="text-xs text-white/40">基于你的命盘实时分析</div>
                </div>
                <div className="ml-auto flex items-center gap-1">
                  <span className="h-2 w-2 animate-twinkle rounded-full bg-green-400" />
                  <span className="text-xs text-white/30">在线</span>
                </div>
              </div>

              {/* 对话气泡 */}
              <div className="space-y-4">
                <div className="flex gap-3">
                  <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-purple-deep/40 px-4 py-3 text-sm leading-relaxed text-white/80">
                    根据你的命宫「紫微七杀」格局，2025年事业宫化禄，是突破职场的关键年份。建议把握Q2-Q3的机遇窗口…
                  </div>
                </div>
                <div className="flex justify-end gap-3">
                  <div className="max-w-[75%] rounded-2xl rounded-tr-sm border border-gold/20 bg-gold/5 px-4 py-3 text-sm text-gold-light">
                    我的2025年事业运势如何？
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-purple-deep/40 px-4 py-3 text-sm leading-relaxed text-white/80">
                    财帛宫有天府坐守，流年逢化科，副业与投资理财均有不错的机会。需注意农历三月…
                  </div>
                </div>
              </div>

              {/* 建议问题 */}
              <div className="mt-6 flex flex-wrap gap-2">
                {["2025事业运势", "感情走向", "财富机遇"].map((q) => (
                  <span
                    key={q}
                    className="cursor-default rounded-full border border-white/10 px-3 py-1 text-xs text-white/40 transition-colors hover:border-purple-glow/30 hover:text-white/60"
                  >
                    {q}
                  </span>
                ))}
              </div>
            </div>

            {/* 浮动装饰 */}
            <div className="absolute -right-4 -top-4 hidden h-20 w-20 animate-float rounded-2xl border border-gold/20 bg-gold/5 backdrop-blur-sm sm:block">
              <div className="flex h-full flex-col items-center justify-center">
                <span className="text-lg font-bold text-gradient-gold">86</span>
                <span className="text-[10px] text-white/40">综合评分</span>
              </div>
            </div>
          </div>

          {/* 右侧：文案 */}
          <div className="order-1 lg:order-2">
            <span className="text-xs font-medium tracking-[0.3em] text-gold uppercase">
              AI Life Planning
            </span>
            <h2 className="mt-3 font-display text-3xl font-bold text-white sm:text-4xl md:text-5xl">
              AI 人生
              <span className="text-gradient-purple">规划师</span>
            </h2>
            <p className="mt-4 text-base leading-relaxed text-white/50 sm:text-lg">
              不只是排盘，更是懂你。AI 结合 RAG 知识库与 LLM 大模型，对你的命盘进行多维度深度解读，
              提供个性化的人生规划建议。
            </p>

            <ul className="mt-8 space-y-4">
              {AI_PLANNING_ITEMS.map((item, index) => (
                <li key={item.title} className="flex gap-4">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-purple-glow/30 bg-purple-glow/10 text-xs font-bold text-purple-mist">
                    {String(index + 1).padStart(2, "0")}
                  </div>
                  <div>
                    <h3 className="font-medium text-white">{item.title}</h3>
                    <p className="mt-0.5 text-sm text-white/40">{item.description}</p>
                  </div>
                </li>
              ))}
            </ul>

            <div className="mt-10">
              <Button href="/chart" variant="gold" size="lg">
                开始生成命盘
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
