"use client";

import { ChartProvider } from "@/context/ChartContext";
import { MembershipProvider } from "@/context/MembershipContext";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <MembershipProvider>
      <ChartProvider>{children}</ChartProvider>
    </MembershipProvider>
  );
}
