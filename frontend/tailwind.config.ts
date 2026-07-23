import type { Config } from "tailwindcss";

/** Ziwei AI V1.0 — 深蓝 / 米白 / 金色 · 东方智慧 + 现代 AI */
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0D1B2A",
          soft: "#1B263B",
          mid: "#415A77",
        },
        paper: {
          DEFAULT: "#E0E1DD",
          soft: "#F4F5F2",
          muted: "#C5C7C0",
        },
        gold: {
          DEFAULT: "#C9A227",
          light: "#E4C65A",
          dark: "#A6841A",
        },
        // legacy aliases during migration
        void: {
          DEFAULT: "#0D1B2A",
          50: "#122033",
          100: "#1B263B",
          200: "#243447",
        },
        purple: {
          glow: "#415A77",
          deep: "#1B263B",
          mist: "#8FA3B8",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "hero-glow":
          "radial-gradient(ellipse 70% 55% at 70% 20%, rgba(201,162,39,0.14), transparent 60%)",
        "page-glow":
          "radial-gradient(ellipse 80% 40% at 50% -10%, rgba(65,90,119,0.35), transparent)",
        "gold-shimmer":
          "linear-gradient(135deg, #A6841A 0%, #C9A227 45%, #E4C65A 100%)",
      },
      animation: {
        "fade-in": "fadeIn 0.7s ease-out forwards",
        "fade-in-up": "fadeInUp 0.8s ease-out forwards",
        float: "float 7s ease-in-out infinite",
        "pulse-soft": "pulseSoft 5s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.45" },
          "50%": { opacity: "0.85" },
        },
      },
      boxShadow: {
        soft: "0 12px 40px rgba(13, 27, 42, 0.35)",
        gold: "0 8px 28px rgba(201, 162, 39, 0.28)",
        panel: "0 1px 0 rgba(224,225,221,0.06) inset, 0 16px 48px rgba(0,0,0,0.28)",
      },
    },
  },
  plugins: [],
};

export default config;
