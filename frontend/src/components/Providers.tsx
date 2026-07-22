"use client";

import { ChartProvider } from "@/context/ChartContext";

export default function Providers({ children }: { children: React.ReactNode }) {
  return <ChartProvider>{children}</ChartProvider>;
}
