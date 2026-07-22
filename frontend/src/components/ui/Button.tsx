import Link from "next/link";
import { type ReactNode } from "react";

type Variant = "gold" | "purple" | "ghost";
type Size = "sm" | "md" | "lg";

interface ButtonProps {
  children: ReactNode;
  href?: string;
  variant?: Variant;
  size?: Size;
  className?: string;
  onClick?: () => void;
  type?: "button" | "submit";
}

const variantStyles: Record<Variant, string> = {
  gold: "bg-gold-shimmer text-void font-semibold shadow-glow-gold hover:brightness-110 hover:shadow-[0_0_40px_rgba(212,168,83,0.5)]",
  purple:
    "bg-gradient-to-r from-purple-deep to-purple-glow text-white shadow-glow hover:brightness-110",
  ghost:
    "border border-white/20 bg-white/5 text-white/80 backdrop-blur-sm hover:border-gold/40 hover:text-gold-light",
};

const sizeStyles: Record<Size, string> = {
  sm: "px-4 py-2 text-sm rounded-lg",
  md: "px-6 py-3 text-sm rounded-xl",
  lg: "px-8 py-4 text-base rounded-xl",
};

export default function Button({
  children,
  href,
  variant = "purple",
  size = "md",
  className = "",
  onClick,
  type = "button",
}: ButtonProps) {
  const classes = `inline-flex items-center justify-center gap-2 transition-all duration-300 ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} className={classes} onClick={onClick}>
      {children}
    </button>
  );
}
