import type { Metadata } from "next";
import { Inter, Noto_Sans_SC } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const notoSansSC = Noto_Sans_SC({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI紫微 - 东方智慧AI分析平台",
  description: "智能紫微斗数排盘与人生趋势分析",
  keywords: ["紫微斗数", "AI", "命盘", "人生规划", "东方智慧"],
  openGraph: {
    title: "AI紫微 - 东方智慧AI分析平台",
    description: "智能紫微斗数排盘与人生趋势分析",
    locale: "zh_CN",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${notoSansSC.variable}`}>
      <body className="font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
