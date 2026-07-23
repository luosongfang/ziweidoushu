"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import FirstExperience from "@/components/FirstExperience";
import { Button } from "@/components/ui/Button";
import { LIFE_DOMAINS, SITE, TRUST_CARDS } from "@/lib/constants";

export default function HomePage() {
  return (
    <>
      <Header />
      <main>
        {/* Hero */}
        <section className="relative min-h-[100svh] overflow-hidden px-4 pb-16 pt-28 sm:px-6 lg:px-8">
          <div className="pointer-events-none absolute inset-0 bg-hero-glow" />
          <div className="relative mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <motion.p
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="font-display text-2xl font-semibold tracking-wide text-gold-light sm:text-3xl"
              >
                {SITE.name}
              </motion.p>
              <motion.p
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.04 }}
                className="mt-1 text-sm tracking-[0.25em] text-gold/70"
              >
                {SITE.nameZh}
              </motion.p>
              <motion.p
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 }}
                className="mt-4 text-sm font-medium text-paper/50"
              >
                {SITE.tagline}
              </motion.p>
              <motion.h1
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.12 }}
                className="mt-5 max-w-xl font-display text-3xl font-bold leading-snug text-paper sm:text-4xl lg:text-[2.75rem]"
              >
                {SITE.heroTitle}
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.18 }}
                className="mt-5 max-w-lg text-base leading-relaxed text-paper/60 sm:text-lg"
              >
                {SITE.heroDescription}
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
                <Button href="/report" variant="outline" size="lg">
                  查看人生档案
                </Button>
                <Button href="/advisor" variant="outline" size="lg">
                  AI 导师陪伴
                </Button>
              </motion.div>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-5 max-w-lg text-sm leading-relaxed text-paper/45"
              >
                不是预测未来，而是通过传统文化理解自己，帮助做出更好的选择。
              </motion.p>
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
                  <div className="font-display text-4xl text-gold/90 sm:text-5xl">紫微</div>
                  <div className="mt-2 text-xs tracking-[0.35em] text-paper/40">TRADITION × AI</div>
                </div>
              </div>
              {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => (
                <span
                  key={deg}
                  className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gold/60"
                  style={{ transform: `rotate(${deg}deg) translateY(-11.5rem)` }}
                />
              ))}
            </motion.div>
          </div>
        </section>

        {/* Trust */}
        <section id="about" className="border-t border-paper/10 px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <p className="section-label">可信赖</p>
            <h2 className="mt-3 font-display text-3xl font-semibold text-paper">
              为什么选择 ZiweiX AI？
            </h2>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              {TRUST_CARDS.map((card, i) => (
                <div
                  key={card.title}
                  className="rounded-2xl border border-paper/10 bg-ink-soft/50 p-6"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full border border-gold/30 font-display text-lg text-gold">
                    {i + 1}
                  </div>
                  <h3 className="mt-4 font-display text-xl font-semibold text-paper">{card.title}</h3>
                  <ul className="mt-3 space-y-2">
                    {card.items.map((item) => (
                      <li key={item} className="text-sm text-paper/55">
                        · {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>

        <FirstExperience />

        {/* User flow */}
        <section className="border-t border-paper/10 px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <p className="section-label">使用流程</p>
            <h2 className="mt-3 font-display text-3xl font-semibold text-paper">三步开启成长之旅</h2>
            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {[
                { step: "01", title: "立即排盘", body: "建立个人命盘与传统文化分析档案", href: "/chart" },
                { step: "02", title: "查看人生档案", body: "生成六维成长报告，理解优势与方向", href: "/report" },
                { step: "03", title: "AI 导师陪伴", body: "长期对话与成长记录，辅助重要选择", href: "/advisor" },
              ].map((item) => (
                <Link key={item.step} href={item.href} className="surface-panel block p-5 transition hover:border-gold/30">
                  <span className="font-display text-sm text-gold/60">{item.step}</span>
                  <h3 className="mt-2 font-display text-lg font-semibold text-paper">{item.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-paper/50">{item.body}</p>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="px-4 pb-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <p className="section-label">探索领域</p>
            <h2 className="mt-3 font-display text-3xl font-semibold text-paper">人生六大关注方向</h2>
            <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
              {LIFE_DOMAINS.map((d) => (
                <Link
                  key={d.key}
                  href="/analysis"
                  className="rounded-2xl border border-paper/10 bg-ink-soft/60 px-4 py-6 text-center transition hover:border-gold/30"
                >
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-gold/30 text-gold">
                    {d.label.slice(0, 1)}
                  </div>
                  <div className="mt-3 text-sm font-medium text-paper">{d.label}</div>
                  <div className="mt-1 text-xs text-paper/40">{d.hint}</div>
                </Link>
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
                ZiweiX AI Mentor — 你的专属人生分析助手
              </h2>
              <p className="mt-4 leading-relaxed text-paper/60">
                不是算命，而是把紫微斗数当作自我认知工具。你可以问事业方向、创业选择、关系经营——我们提供传统文化视角下的分析与行动建议。
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
