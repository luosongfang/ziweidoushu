import type { Metadata } from "next";
import { Noto_Sans_SC, Noto_Serif_SC } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";
import { SITE } from "@/lib/constants";

const sans = Noto_Sans_SC({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const display = Noto_Serif_SC({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: `${SITE.name} · ${SITE.nameZh}`,
  description: SITE.heroDescription,
  keywords: ["紫微斗数", "传统文化", "自我认知", "AI导师", "人生规划"],
  openGraph: {
    title: `${SITE.name} · ${SITE.tagline}`,
    description: SITE.heroDescription,
    locale: "zh_CN",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className={`${sans.variable} ${display.variable}`}>
      <body className="font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
