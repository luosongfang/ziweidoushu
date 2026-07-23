"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Compass, BarChart3, MessageCircle, User } from "lucide-react";
import { MOBILE_NAV } from "@/lib/constants";
import { cn } from "@/lib/utils";

const ICONS = {
  home: Home,
  chart: Compass,
  analysis: BarChart3,
  advisor: MessageCircle,
  profile: User,
} as const;

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-50 border-t border-paper/10 bg-ink/95 backdrop-blur-xl md:hidden"
      aria-label="主导航"
    >
      <div className="mx-auto flex max-w-lg items-stretch justify-around px-2 pb-[env(safe-area-inset-bottom)]">
        {MOBILE_NAV.map((item) => {
          const Icon = ICONS[item.icon];
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex min-w-0 flex-1 flex-col items-center gap-0.5 px-1 py-2.5 text-[10px] transition",
                active ? "text-gold" : "text-paper/45 hover:text-paper/70",
              )}
            >
              <Icon className={cn("h-5 w-5", active && "text-gold-light")} strokeWidth={active ? 2.25 : 1.75} />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
