"use client";

import { cn } from "@/lib/utils";

interface StepIndicatorProps {
  current: number;
  total: number;
}

export function StepIndicator({ current, total }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-[12px] text-slate-600 tracking-wide">
        Step {current + 1} of {total}
      </span>
      <div className="flex gap-1.5">
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "h-1.5 rounded-full transition-all duration-500",
              i < current && "w-4 bg-emerald-500/70",
              i === current && "w-5 bg-violet-500 shadow-[0_0_6px_rgba(139,92,246,0.4)]",
              i > current && "w-1.5 bg-slate-700"
            )}
          />
        ))}
      </div>
    </div>
  );
}
