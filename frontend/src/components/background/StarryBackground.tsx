"use client";

import { useEffect, useRef } from "react";

interface Star {
  x: number;
  y: number;
  radius: number;
  opacity: number;
  twinkleSpeed: number;
  twinkleOffset: number;
}

export default function StarryBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId: number;
    let stars: Star[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars();
    };

    const initStars = () => {
      const count = Math.floor((canvas.width * canvas.height) / 8000);
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1.5 + 0.3,
        opacity: Math.random() * 0.8 + 0.2,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinkleOffset: Math.random() * Math.PI * 2,
      }));
    };

    const draw = (time: number) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const star of stars) {
        const twinkle =
          0.5 +
          0.5 * Math.sin(time * star.twinkleSpeed + star.twinkleOffset);
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity * twinkle})`;
        ctx.fill();
      }

      animationId = requestAnimationFrame(draw);
    };

    resize();
    window.addEventListener("resize", resize);
    animationId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* 深空渐变底色 */}
      <div className="absolute inset-0 bg-void" />
      <div className="absolute inset-0 bg-gradient-radial from-purple-deep/30 via-void to-void" />
      <div className="absolute inset-0 bg-hero-glow" />

      {/* 紫色星云光晕 */}
      <div className="absolute -left-1/4 top-1/4 h-[600px] w-[600px] animate-pulse-glow rounded-full bg-purple-glow/10 blur-[120px]" />
      <div className="absolute -right-1/4 bottom-1/4 h-[500px] w-[500px] animate-pulse-glow rounded-full bg-purple-deep/20 blur-[100px] animation-delay-600" />
      <div className="absolute left-1/2 top-0 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-gold/5 blur-[80px]" />

      {/* 动态星点 */}
      <canvas ref={canvasRef} className="absolute inset-0" aria-hidden />

      {/* 东方星座装饰线 */}
      <svg
        className="absolute inset-0 h-full w-full opacity-[0.06]"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden
      >
        <circle cx="15%" cy="20%" r="80" fill="none" stroke="#d4a853" strokeWidth="0.5" />
        <circle cx="85%" cy="30%" r="60" fill="none" stroke="#8b5cf6" strokeWidth="0.5" />
        <line x1="15%" y1="20%" x2="25%" y2="35%" stroke="#d4a853" strokeWidth="0.5" />
        <line x1="25%" y1="35%" x2="35%" y2="25%" stroke="#d4a853" strokeWidth="0.5" />
        <line x1="85%" y1="30%" x2="78%" y2="45%" stroke="#8b5cf6" strokeWidth="0.5" />
        <line x1="78%" y1="45%" x2="90%" y2="50%" stroke="#8b5cf6" strokeWidth="0.5" />
      </svg>
    </div>
  );
}
