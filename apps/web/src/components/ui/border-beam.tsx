"use client";

import { cn } from "@/lib/utils";

interface BorderBeamProps {
  className?: string;
  size?: number;
  duration?: number;
  delay?: number;
  colorFrom?: string;
  colorTo?: string;
  borderWidth?: number;
}

export function BorderBeam({
  className,
  size = 200,
  duration = 15,
  delay = 0,
  colorFrom = "#14b8a6",
  colorTo = "#10b981",
  borderWidth = 2,
}: BorderBeamProps) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 rounded-full",
        className
      )}
      style={
        {
          "--size": size,
          "--duration": duration,
          "--delay": delay,
          "--color-from": colorFrom,
          "--color-to": colorTo,
          "--border-width": borderWidth,
        } as React.CSSProperties
      }
    >
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: `transparent`,
          border: `${borderWidth}px solid transparent`,
          borderRadius: "50%",
        }}
      />
      <div
        className="absolute inset-0 rounded-full animate-border-beam"
        style={{
          background: `linear-gradient(to right, transparent, transparent) padding-box, 
            conic-gradient(from calc(270deg - (var(--size) * 0.5deg)), 
              transparent 0%, 
              ${colorFrom} 10%, 
              ${colorTo} 20%, 
              transparent 25%
            ) border-box`,
          border: `${borderWidth}px solid transparent`,
          borderRadius: "50%",
          animation: `border-beam ${duration}s linear infinite`,
          animationDelay: `${delay}s`,
        }}
      />
    </div>
  );
}
