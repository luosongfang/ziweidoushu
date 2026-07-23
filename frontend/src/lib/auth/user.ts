import type { Session } from "@supabase/supabase-js";
import { getAuthSessionRaw } from "@/lib/auth/auth";

export interface AppUser {
  id: string;
  email: string | null;
  nickname: string;
  avatar: string | null;
  created_at: string;
}

export function mapSessionToUser(session: Session | null): AppUser | null {
  if (!session?.user) return null;
  const meta = session.user.user_metadata ?? {};
  return {
    id: session.user.id,
    email: session.user.email ?? null,
    nickname: (meta.nickname as string) || session.user.email?.split("@")[0] || "用户",
    avatar: (meta.avatar_url as string) || null,
    created_at: session.user.created_at ?? new Date().toISOString(),
  };
}

export function mapDevUser(raw: {
  user: { id: string; email: string; nickname: string; avatar: string | null; created_at: string };
}): AppUser {
  return {
    id: raw.user.id,
    email: raw.user.email,
    nickname: raw.user.nickname,
    avatar: raw.user.avatar,
    created_at: raw.user.created_at,
  };
}

export async function resolveAppUser(): Promise<AppUser | null> {
  const session = await getAuthSessionRaw();
  if (!session) return null;

  const maybeSession = session as Session;
  if (maybeSession.user?.app_metadata !== undefined || maybeSession.user?.aud) {
    return mapSessionToUser(maybeSession);
  }

  if ("user" in session && session.user && "nickname" in session.user) {
    return mapDevUser(
      session as { user: { id: string; email: string; nickname: string; avatar: string | null; created_at: string } },
    );
  }

  return null;
}
