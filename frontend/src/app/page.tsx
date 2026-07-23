"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { LIFE_DOMAINS, SITE } from "@/lib/constants";

export default function HomePage() {
  return (
    <>
      <Header />
      <main>
        {/* Hero — brand first, one composition */}
        <section className="relative min-h-[100svh] overflow-hidden px-4 pb-16 pt-28 sm:px-6 lg:px-8">
          <div className="pointer-events-none absolute inset-0 bg-hero-glow" />
          <div className="relative mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <motion.p
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="font-display text-3xl font-semibold tracking-wide text-gold-light sm:text-4xl"
              >
                {SITE.name}
              </motion.p>
              <motion.h1
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 }}
                className="mt-5 max-w-xl font-display text-4xl font-bold leading-tight text-paper sm:text-5xl"
              >
                {SITE.tagline}
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.16 }}
                className="mt-5 max-w-lg text-base leading-relaxed text-paper/60 sm:text-lg"
              >
                {SITE.subtitle}
              </motion.p>
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.24 }}
                className="mt-8 flex flex-wrap gap-3"
              >
                <Button href="/chart" variant="gold" size="lg">
                  立即排盘
                </Button>
                <Button href="/analysis" variant="outline" size="lg">
                  免费体验一次专业解盘
                </Button>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.12, duration: 0.7 }}
              className="relative mx-auto aspect-square w-full max-w-md"
              aria-hidden
            >
              <div className="absolute inset-[8%] rounded-full border border-gold/25" />
              <div className="absolute inset-[18%] animate-pulse-soft rounded-full border border-paper/15" />
              <div className="absolute inset-[28%] rounded-full bg-gradient-to-br from-ink-soft to-ink shadow-soft" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="font-display text-5xl text-gold/90">紫微</div>
                  <div className="mt-2 text-xs tracking-[0.35em] text-paper/40">TWELVE PALACES</div>
                </div>
              </div>
              {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
                <span
                  key={deg}
                  className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gold/70"
                  style={{
                    transform: `rotate(${deg}deg) translateY(-11.5rem)`,
                  }}
                />
              ))}
            </motion.div>
          </div>
        </section>

        {/* Feature modules — below first viewport */}
        <section className="border-t border-paper/10 px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <p className="section-label">核心能力</p>
            <h2 className="mt-3 font-display text-3xl font-semibold text-paper">三步开始自我探索</h2>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              <Module
                title="免费排盘"
                body="输入出生信息，生成十二宫、十四主星与四化结构。注册赠送一次专业分析。"
                href="/chart"
                cta="去排盘"
              />
              <Module
                title="AI 人生分析"
                body="从事业、财富、关系、成长与性格优势出发，以传统理论分析作为自我探索参考。"
                href="/analysis"
                cta="查看分析"
              />
              <Module
                title="AI 人生导师"
                body="长期陪伴式对话，结合命盘、咨询历史与知识库，辅助人生规划与决策。"
                href="/advisor"
                cta="开始咨询"
              />
            </div>
          </div>
        </section>

        <section className="px-4 pb-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <p className="section-label">探索领域</p>
            <h2 className="mt-3 font-display text-3xl font-semibold text-paper">
              人生六大领域
            </h2>
            <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
              {LIFE_DOMAINS.map((d) => (
                <div
                  key={d.key}
                  className="rounded-2xl border border-paper/10 bg-ink-soft/60 px-4 py-6 text-center"
                >
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-gold/30 text-gold">
                    {d.label.slice(0, 1)}
                  </div>
                  <div className="mt-3 text-sm font-medium text-paper">{d.label}</div>
                  <div className="mt-1 text-xs text-paper/40">{d.hint}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-paper/10 px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto grid max-w-7xl items-center gap-10 lg:grid-cols-2">
            <div
              className="min-h-[280px] rounded-3xl bg-cover bg-center"
              style={{
                backgroundImage:
                  "linear-gradient(135deg, rgba(13,27,42,0.2), rgba(13,27,42,0.65)), radial-gradient(circle at 30% 40%, #415A77, #0D1B2A 70%)",
              }}
            />
            <div>
              <p className="section-label">长期陪伴</p>
              <h2 className="mt-3 font-display text-3xl font-semibold text-paper">
                AI 人生导师，陪你做更好的选择
              </h2>
              <p className="mt-4 text-paper/60 leading-relaxed">
                不是算命，而是把紫微斗数当作自我认知工具。你可以问「现在适合换行业吗」「创业需要注意什么」——我们提供趋势参考与行动建议。
              </p>
              <Button href="/member" variant="gold" className="mt-6">
                了解会员权益
              </Button>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

function Module({
  title,
  body,
  href,
  cta,
}: {
  title: string;
  body: string;
  href: string;
  cta: string;
}) {
  return (
    <div className="rounded-2xl border border-paper/10 bg-ink-soft/50 p-6">
      <h3 className="font-display text-xl font-semibold text-paper">{title}</h3>
      <p className="mt-3 text-sm leading-relaxed text-paper/55">{body}</p>
      <Link href={href} className="mt-5 inline-block text-sm text-gold hover:underline">
        {cta} →
      </Link>
    </div>
  );
}
