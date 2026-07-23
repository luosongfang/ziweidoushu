import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { FREE_EXPERIENCE_BENEFITS } from "@/lib/constants";

export default function FirstExperience() {
  return (
    <section className="border-t border-paper/10 px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl">
        <div className="surface-panel overflow-hidden p-6 sm:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="section-label">免费体验</p>
              <h2 className="mt-2 font-display text-2xl font-semibold text-paper sm:text-3xl">
                开始你的第一次 ZiweiX AI 探索
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-paper/55">
                无需注册即可生成个人星盘，并获得一次专业解读预览。
              </p>
              <ul className="mt-5 space-y-2">
                {FREE_EXPERIENCE_BENEFITS.map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-paper/70">
                    <span className="text-gold">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="shrink-0 lg:text-right">
              <Button href="/chart" variant="gold" size="lg" className="w-full sm:w-auto">
                开始体验
              </Button>
              <p className="mt-3 text-xs text-paper/35">
                已有账号？
                <Link href="/profile" className="ml-1 text-gold/70 hover:underline">
                  查看成长档案
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
