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
import type { ChartCreateResponse } from "@/types/ziwei";

const STORAGE_KEY = "ziwei-chart-v1";

interface ChartContextValue {
  chart: ChartCreateResponse | null;
  setChart: (data: ChartCreateResponse | null) => void;
  clearChart: () => void;
  isHydrated: boolean;
}

const ChartContext = createContext<ChartContextValue | undefined>(undefined);

export function ChartProvider({ children }: { children: ReactNode }) {
  const [chart, setChartState] = useState<ChartCreateResponse | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) setChartState(JSON.parse(raw) as ChartCreateResponse);
    } catch {
      sessionStorage.removeItem(STORAGE_KEY);
    }
    setIsHydrated(true);
  }, []);

  const setChart = useCallback((data: ChartCreateResponse | null) => {
    setChartState(data);
    if (data) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const clearChart = useCallback(() => setChart(null), [setChart]);

  const value = useMemo(
    () => ({ chart, setChart, clearChart, isHydrated }),
    [chart, setChart, clearChart, isHydrated],
  );

  return <ChartContext.Provider value={value}>{children}</ChartContext.Provider>;
}

export function useChart() {
  const ctx = useContext(ChartContext);
  if (!ctx) throw new Error("useChart must be used within ChartProvider");
  return ctx;
}
