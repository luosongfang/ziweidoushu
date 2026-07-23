/**
 * Supabase Auth 客户端 — V1.2 统一入口
 * @see authService.ts 业务方法
 */
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

export type AuthMode = "supabase" | "dev";

let client: SupabaseClient | null = null;

export function getAuthClient(): SupabaseClient | null {
  if (!isSupabaseConfigured) return null;
  if (!client) {
    client = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
  }
  return client;
}

/** @deprecated 使用 getAuthClient */
export const getSupabaseClient = getAuthClient;

export function getAuthMode(): AuthMode {
  return isSupabaseConfigured ? "supabase" : "dev";
}
