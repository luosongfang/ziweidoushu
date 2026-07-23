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

export type PlanId = "free" | "basic" | "vip" | "svip";

interface MembershipState {
  userId: string;
  planId: PlanId;
  points: number;
  freeAnalysisUsed: boolean;
  hydrated: boolean;
  setPlan: (plan: PlanId) => void;
  spendPoints: (amount: number) => boolean;
  grantPoints: (amount: number) => void;
  markAnalysisUsed: () => void;
}

const STORAGE_KEY = "ziwei-membership-v1";

const MembershipContext = createContext<MembershipState | null>(null);

function load(): Partial<MembershipState> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Partial<MembershipState>) : {};
  } catch {
    return {};
  }
}

function save(data: {
  userId: string;
  planId: PlanId;
  points: number;
  freeAnalysisUsed: boolean;
}) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function MembershipProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState("guest-local");
  const [planId, setPlanId] = useState<PlanId>("free");
  const [points, setPoints] = useState(0);
  const [freeAnalysisUsed, setFreeAnalysisUsed] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const data = load();
    setUserId(data.userId || `guest-${Math.random().toString(36).slice(2, 10)}`);
    setPlanId((data.planId as PlanId) || "free");
    setPoints(typeof data.points === "number" ? data.points : 0);
    setFreeAnalysisUsed(Boolean(data.freeAnalysisUsed));
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    save({ userId, planId, points, freeAnalysisUsed });
  }, [userId, planId, points, freeAnalysisUsed, hydrated]);

  const setPlan = useCallback((plan: PlanId) => {
    setPlanId(plan);
    if (plan === "vip") setPoints((p) => Math.max(p, 300));
    if (plan === "svip") setPoints((p) => Math.max(p, 9999));
  }, []);

  const spendPoints = useCallback((amount: number) => {
    let ok = false;
    setPoints((prev) => {
      if (prev < amount) {
        ok = false;
        return prev;
      }
      ok = true;
      return prev - amount;
    });
    return ok;
  }, []);

  const grantPoints = useCallback((amount: number) => {
    setPoints((p) => p + amount);
  }, []);

  const markAnalysisUsed = useCallback(() => {
    setFreeAnalysisUsed(true);
  }, []);

  const value = useMemo(
    () => ({
      userId,
      planId,
      points,
      freeAnalysisUsed,
      hydrated,
      setPlan,
      spendPoints,
      grantPoints,
      markAnalysisUsed,
    }),
    [
      userId,
      planId,
      points,
      freeAnalysisUsed,
      hydrated,
      setPlan,
      spendPoints,
      grantPoints,
      markAnalysisUsed,
    ],
  );

  return (
    <MembershipContext.Provider value={value}>{children}</MembershipContext.Provider>
  );
}

export function useMembership() {
  const ctx = useContext(MembershipContext);
  if (!ctx) throw new Error("useMembership must be used within MembershipProvider");
  return ctx;
}
