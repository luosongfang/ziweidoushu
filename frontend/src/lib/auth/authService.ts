/**
 * 认证业务服务 — Email / 微信预留 / 开发模式
 */
import type { Session } from "@supabase/supabase-js";
import { getAuthClient, getAuthMode, isSupabaseConfigured, type AuthMode } from "@/lib/auth/authClient";
import type { AppUser } from "@/lib/auth/user";

export type { AuthMode };
export { getAuthMode, isSupabaseConfigured };

export interface AuthSession {
  access_token: string;
  user: AppUser;
}

export interface RegisterInput {
  email: string;
  password: string;
  nickname?: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

const DEV_KEY = "ziweix-dev-session";

interface DevSession {
  access_token: string;
  user: AppUser & { email: string };
}

export async function register(input: RegisterInput) {
  return registerWithEmail(input);
}

export async function login(input: LoginInput) {
  return loginWithEmail(input);
}

export async function loginWithEmail({ email, password }: LoginInput) {
  const client = getAuthClient();
  if (!client) {
    return devSignIn(email);
  }
  const { data, error } = await client.auth.signInWithPassword({ email, password });
  if (error) throw new Error(error.message);
  return data;
}

export async function registerWithEmail(input: RegisterInput) {
  const client = getAuthClient();
  if (!client) {
    return devSignIn(input.email, input.nickname);
  }
  const { data, error } = await client.auth.signUp({
    email: input.email,
    password: input.password,
    options: { data: { nickname: input.nickname || input.email.split("@")[0] } },
  });
  if (error) throw new Error(error.message);
  return data;
}

export async function logout() {
  const client = getAuthClient();
  if (client) {
    const { error } = await client.auth.signOut();
    if (error) throw new Error(error.message);
  }
  clearDevSession();
}

export async function loginWithWechat() {
  throw new Error("微信登录即将开放，请先使用邮箱登录");
}

export async function loginWithPhone(_phone: string) {
  throw new Error("手机号登录即将开放，请先使用邮箱登录");
}

export async function getSession(): Promise<AuthSession | null> {
  const raw = await getSessionRaw();
  if (!raw) return null;
  const user = await resolveUserFromSession(raw);
  if (!user) return null;
  const token =
    "access_token" in raw && typeof raw.access_token === "string" ? raw.access_token : user.id;
  return { access_token: token, user };
}

export async function getAccessToken(): Promise<string | null> {
  const session = await getSession();
  return session?.access_token ?? null;
}

export async function getAuthHeaders(): Promise<Record<string, string>> {
  const token = await getAccessToken();
  if (!token) return {};
  if (getAuthMode() === "dev") {
    return { Authorization: `Bearer ${token}`, "X-Dev-User-Id": token };
  }
  return { Authorization: `Bearer ${token}` };
}

export function onAuthStateChange(callback: (session: Session | null) => void) {
  const client = getAuthClient();
  if (!client) return () => {};
  const { data } = client.auth.onAuthStateChange((_event, session) => callback(session));
  return () => data.subscription.unsubscribe();
}

async function getSessionRaw(): Promise<DevSession | Session | null> {
  const client = getAuthClient();
  if (client) {
    const { data } = await client.auth.getSession();
    return data.session;
  }
  return loadDevSession();
}

async function resolveUserFromSession(raw: DevSession | Session): Promise<AppUser | null> {
  const { mapSessionToUser, mapDevUser } = await import("@/lib/auth/user");
  if ("user" in raw && raw.user && "aud" in (raw as Session).user) {
    return mapSessionToUser(raw as Session);
  }
  if ("user" in raw && raw.user && "nickname" in raw.user) {
    return mapDevUser(raw as DevSession);
  }
  return null;
}

function devSignIn(email: string, nickname?: string) {
  const id = devUserIdFromEmail(email);
  const session: DevSession = {
    access_token: id,
    user: {
      id,
      email,
      nickname: nickname || email.split("@")[0] || "访客",
      avatar: null,
      created_at: new Date().toISOString(),
    },
  };
  saveDevSession(session);
  return { session: session as unknown as Session, user: session.user as unknown as Session["user"] };
}

function saveDevSession(session: DevSession) {
  if (typeof window !== "undefined") localStorage.setItem(DEV_KEY, JSON.stringify(session));
}

export function clearDevSession() {
  if (typeof window !== "undefined") localStorage.removeItem(DEV_KEY);
}

function loadDevSession(): DevSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(DEV_KEY);
    return raw ? (JSON.parse(raw) as DevSession) : null;
  } catch {
    return null;
  }
}

function devUserIdFromEmail(email: string): string {
  let hash = 0;
  for (let i = 0; i < email.length; i++) {
    hash = (hash << 5) - hash + email.charCodeAt(i);
    hash |= 0;
  }
  const hex = Math.abs(hash).toString(16).padStart(8, "0");
  return `00000000-0000-4000-8000-${hex.padStart(12, "0").slice(0, 12)}`;
}

/** 兼容旧模块 re-export */
export const signUpWithEmail = registerWithEmail;
export const signInWithEmail = loginWithEmail;
export const signOut = logout;
export const signInWithWechat = loginWithWechat;
export const signInWithPhone = loginWithPhone;
export const getAuthSessionRaw = getSessionRaw;
