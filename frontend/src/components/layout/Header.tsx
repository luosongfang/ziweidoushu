"use client";

import { useState } from "react";
import Link from "next/link";
import Logo from "./Logo";
import { Button } from "@/components/ui/Button";
import { NAV_LINKS } from "@/lib/constants";
import { useMembership } from "@/context/MembershipContext";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { points, planId, hydrated } = useMembership();

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-paper/10 bg-ink/75 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo size="sm" />

        <nav className="hidden items-center gap-7 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-paper/65 transition-colors hover:text-gold-light"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {hydrated && (
            <span className="rounded-full border border-paper/10 px-3 py-1 text-xs text-paper/55">
              {planId.toUpperCase()} · 积分 {points}
            </span>
          )}
          <Button href="/chart" variant="gold" size="sm">
            立即排盘
          </Button>
        </div>

        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-paper/15 md:hidden"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="打开菜单"
        >
          <span className="text-paper/70">{menuOpen ? "✕" : "☰"}</span>
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-paper/10 bg-ink/95 px-4 py-4 md:hidden">
          <nav className="flex flex-col gap-2">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-lg px-3 py-2 text-sm text-paper/75 hover:bg-paper/5"
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <Button href="/chart" variant="gold" size="md" className="mt-2 w-full">
              立即排盘
            </Button>
          </nav>
        </div>
      )}
    </header>
  );
}
