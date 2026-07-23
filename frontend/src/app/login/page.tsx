"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import PrivacyNotice from "@/components/PrivacyNotice";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getAuthMode, loginWithWechat, isSupabaseConfigured } from "@/lib/auth/authService";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { refreshUser, isAuthenticated, isLoading, login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/profile");
    }
  }, [isAuthenticated, isLoading, router]);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "register") {
        await register(email, password, nickname);
      } else {
        await login(email, password);
      }
      router.push("/profile");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  const handleWechat = async () => {
    setError(null);
    try {
      await loginWithWechat();
    } catch (err) {
      setError(err instanceof Error ? err.message : "微信登录暂未开放");
    }
  };

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ink text-paper/50">
        加载中…
      </div>
    );
  }

  return (
    <>
      <Header />
      <main className="min-h-screen px-4 pb-20 pt-24 sm:px-6">
        <div className="mx-auto max-w-md">
          <div className="text-center">
            <p className="section-label">账户</p>
            <h1 className="mt-2 font-display text-3xl font-bold text-paper">欢迎进入 ZiweiX AI</h1>
            <p className="mt-3 text-sm leading-relaxed text-paper/55">
              创建你的个人成长档案，开启长期 AI 人生导师陪伴。
            </p>
          </div>

          {!isSupabaseConfigured && (
            <div className="mt-6 rounded-xl border border-amber-500/25 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
              当前为开发模式（{getAuthMode()}）。填写邮箱即可创建本地预览账户，接入 Supabase 后自动切换真实认证。
            </div>
          )}

          <form onSubmit={handleEmailSubmit} className="mt-8 space-y-4 surface-panel p-6">
            <div className="flex gap-2 rounded-xl border border-paper/10 p-1">
              {(["login", "register"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className={`flex-1 rounded-lg py-2 text-sm ${
                    mode === m ? "bg-gold/20 text-gold-light" : "text-paper/45"
                  }`}
                >
                  {m === "login" ? "邮箱登录" : "注册账户"}
                </button>
              ))}
            </div>

            {mode === "register" && (
              <div className="space-y-2">
                <Label htmlFor="nickname">昵称</Label>
                <Input
                  id="nickname"
                  placeholder="如何称呼你"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">邮箱</Label>
              <Input
                id="email"
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                type="password"
                required
                minLength={6}
                placeholder="至少 6 位"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                {error}
              </p>
            )}

            <Button type="submit" variant="gold" className="w-full" disabled={loading}>
              {loading ? "处理中…" : mode === "login" ? "邮箱登录" : "创建账户并登录"}
            </Button>

            <Button type="button" variant="outline" className="w-full" onClick={() => void handleWechat()}>
              微信登录（即将开放）
            </Button>

            <PrivacyNotice className="text-center" />
          </form>

          <p className="mt-6 text-center text-sm text-paper/45">
            暂不登录？
            <Link href="/chart" className="ml-1 text-gold/80 hover:underline">
              以游客身份体验
            </Link>
          </p>
        </div>
      </main>
      <Footer />
    </>
  );
}
