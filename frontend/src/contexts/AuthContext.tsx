"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  getAuthMode,
  getSession,
  isSupabaseConfigured,
  loginWithEmail,
  logout,
  onAuthStateChange,
  registerWithEmail,
  type AuthSession,
} from "@/lib/auth/authService";
import { resolveAppUser, type AppUser } from "@/lib/auth/user";

interface AuthContextValue {
  user: AppUser | null;
  session: AuthSession | null;
  isAuthenticated: boolean;
  isGuest: boolean;
  isLoading: boolean;
  authMode: "supabase" | "dev";
  supabaseConfigured: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, nickname?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  /** @deprecated 使用 logout */
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);
  const [session, setSession] = useState<AuthSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const s = await getSession();
    setSession(s);
    setUser(s?.user ?? (await resolveAppUser()));
  }, []);

  useEffect(() => {
    let mounted = true;
    (async () => {
      await refreshUser();
      if (mounted) setIsLoading(false);
    })();
    const unsub = onAuthStateChange(() => void refreshUser());
    return () => {
      mounted = false;
      unsub();
    };
  }, [refreshUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      await loginWithEmail({ email, password });
      await refreshUser();
    },
    [refreshUser],
  );

  const register = useCallback(
    async (email: string, password: string, nickname?: string) => {
      await registerWithEmail({ email, password, nickname });
      await refreshUser();
    },
    [refreshUser],
  );

  const doLogout = useCallback(async () => {
    await logout();
    setUser(null);
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      session,
      isAuthenticated: Boolean(user),
      isGuest: !user,
      isLoading,
      authMode: getAuthMode(),
      supabaseConfigured: isSupabaseConfigured,
      login,
      register,
      logout: doLogout,
      signOut: doLogout,
      refreshUser,
    }),
    [user, session, isLoading, login, register, doLogout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
