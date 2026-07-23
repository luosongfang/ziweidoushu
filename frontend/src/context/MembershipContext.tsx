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
import { useAuth } from "@/contexts/AuthContext";
import { getMembership, setMembershipPreview } from "@/services/memberService";
import { PLAN_LABELS } from "@/lib/constants";

export type PlanId = "free" | "basic" | "vip" | "svip";

interface MembershipState {
  userId: string;
  planId: PlanId;
  planLabel: string;
  points: number;
  freeAnalysisUsed: boolean;
  hydrated: boolean;
  isGuest: boolean;
  setPlan: (plan: PlanId) => Promise<void>;
  spendPoints: (amount: number) => boolean;
  grantPoints: (amount: number) => void;
  markAnalysisUsed: () => void;
  syncFromServer: () => Promise<void>;
}

const STORAGE_KEY = "ziwei-membership-v1";

const MembershipContext = createContext<MembershipState | null>(null);

function loadGuest(): { freeAnalysisUsed: boolean } {
  if (typeof window === "undefined") return { freeAnalysisUsed: false };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const data = raw ? JSON.parse(raw) : {};
    return { freeAnalysisUsed: Boolean(data.freeAnalysisUsed) };
  } catch {
    return { freeAnalysisUsed: false };
  }
}

function saveGuest(freeAnalysisUsed: boolean) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ freeAnalysisUsed }));
}

export function MembershipProvider({ children }: { children: ReactNode }) {
  const { user, isGuest, isAuthenticated } = useAuth();
  const [planId, setPlanId] = useState<PlanId>("free");
  const [planLabel, setPlanLabel] = useState(PLAN_LABELS.free);
  const [points, setPoints] = useState(0);
  const [freeAnalysisUsed, setFreeAnalysisUsed] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  const syncFromServer = useCallback(async () => {
    if (!isAuthenticated || !user) return;
    const status = await getMembership();
    if (status) {
      const plan = status.plan_id as PlanId;
      setPlanId(plan in { free: 1, basic: 1, vip: 1, svip: 1 } ? plan : "free");
      setPlanLabel(status.plan_label || PLAN_LABELS[plan] || plan.toUpperCase());
      setPoints(status.points);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    const guest = loadGuest();
    setFreeAnalysisUsed(guest.freeAnalysisUsed);
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    if (isGuest) {
      saveGuest(freeAnalysisUsed);
    }
  }, [freeAnalysisUsed, isGuest, hydrated]);

  useEffect(() => {
    if (isAuthenticated) {
      void syncFromServer();
    } else {
      setPlanId("free");
      setPlanLabel(PLAN_LABELS.free);
      setPoints(0);
    }
  }, [isAuthenticated, syncFromServer]);

  const setPlan = useCallback(async (plan: PlanId) => {
    if (isAuthenticated) {
      const status = await setMembershipPreview(plan);
      if (status) {
        setPlanId(status.plan_id);
        setPlanLabel(status.plan_label || PLAN_LABELS[status.plan_id] || status.plan_id.toUpperCase());
        setPoints(status.points);
        return;
      }
    }
    setPlanId(plan);
    setPlanLabel(PLAN_LABELS[plan] || plan.toUpperCase());
    if (plan === "vip") setPoints((p) => Math.max(p, 300));
    if (plan === "svip") setPoints((p) => Math.max(p, 9999));
    if (plan === "free" || plan === "basic") setPoints(0);
  }, [isAuthenticated]);

  const spendPoints = useCallback((amount: number) => {
    let ok = false;
    setPoints((prev) => {
      if (planId === "svip") {
        ok = true;
        return prev;
      }
      if (prev < amount) {
        ok = false;
        return prev;
      }
      ok = true;
      return prev - amount;
    });
    return ok;
  }, [planId]);

  const grantPoints = useCallback((amount: number) => {
    setPoints((p) => p + amount);
  }, []);

  const markAnalysisUsed = useCallback(() => {
    setFreeAnalysisUsed(true);
  }, []);

  const value = useMemo(
    () => ({
      userId: user?.id ?? "guest",
      planId,
      planLabel,
      points,
      freeAnalysisUsed,
      hydrated,
      isGuest,
      setPlan,
      spendPoints,
      grantPoints,
      markAnalysisUsed,
      syncFromServer,
    }),
    [
      user?.id,
      planId,
      planLabel,
      points,
      freeAnalysisUsed,
      hydrated,
      isGuest,
      setPlan,
      spendPoints,
      grantPoints,
      markAnalysisUsed,
      syncFromServer,
    ],
  );

  return <MembershipContext.Provider value={value}>{children}</MembershipContext.Provider>;
}

export function useMembership() {
  const ctx = useContext(MembershipContext);
  if (!ctx) throw new Error("useMembership must be used within MembershipProvider");
  return ctx;
}
