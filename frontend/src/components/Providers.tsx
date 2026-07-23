"use client";

import { ChartProvider } from "@/context/ChartContext";
import { MembershipProvider } from "@/context/MembershipContext";
import { AuthProvider } from "@/contexts/AuthContext";
import MobileNav from "@/components/MobileNav";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <MembershipProvider>
        <ChartProvider>
          <div className="pb-[4.5rem] md:pb-0">{children}</div>
          <MobileNav />
        </ChartProvider>
      </MembershipProvider>
    </AuthProvider>
  );
}
