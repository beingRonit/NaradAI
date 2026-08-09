"use client";

import Image from "next/image";
import { Check, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface OnboardingSidebarProps {
  currentStep: number;
  steps: readonly string[];
}

export function OnboardingSidebar({ currentStep, steps }: OnboardingSidebarProps) {
  return (
    <aside className="hidden lg:flex flex-col w-[280px] bg-[#0D0D14] border-r border-white/[0.04] h-screen select-none">
      {/* ── Avatar + Wordmark ──────────────────────────────────────── */}
      <div className="flex flex-col items-center pt-10 pb-8">
        {/* Avatar with layered glow */}
        <div className="relative mb-5">
          <div className="absolute -inset-3 rounded-full bg-violet-500/[0.12] blur-xl" />
          <div className="absolute -inset-1.5 rounded-full border border-violet-500/30" />
          <div className="relative w-[72px] h-[72px] rounded-full overflow-hidden border-2 border-violet-500/50 shadow-[0_0_30px_rgba(139,92,246,0.25)]">
            <Image
              src="/Logo.png"
              alt="Narad AI"
              fill
              className="object-cover"
              priority
            />
          </div>
        </div>

        {/* Wordmark */}
        <h1 className="text-lg font-bold text-white tracking-wide">
          NARAD{" "}
          <span className="text-violet-400">AI</span>
        </h1>
        <p className="text-[11px] text-slate-500 mt-1 tracking-widest uppercase">
          Autonomous Creator
        </p>
      </div>

      {/* ── Divider ────────────────────────────────────────────────── */}
      <div className="mx-5 h-px bg-white/[0.04]" />

      {/* ── Step List ──────────────────────────────────────────────── */}
      <nav className="flex-1 px-4 py-5">
        <ul className="space-y-0.5">
          {steps.map((label, i) => {
            const isCompleted = i < currentStep;
            const isCurrent = i === currentStep;

            return (
              <li key={label}>
                <div
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300",
                    isCurrent && "bg-violet-500/[0.08]",
                    isCompleted && "opacity-90",
                    !isCompleted && !isCurrent && "opacity-40"
                  )}
                >
                  {/* Step circle */}
                  <div
                    className={cn(
                      "w-[22px] h-[22px] rounded-full flex items-center justify-center shrink-0 transition-all duration-300",
                      isCompleted &&
                        "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.35)]",
                      isCurrent &&
                        "bg-violet-500 shadow-[0_0_14px_rgba(139,92,246,0.5)]",
                      !isCompleted &&
                        !isCurrent &&
                        "border-2 border-slate-700"
                    )}
                  >
                    {isCompleted ? (
                      <Check className="w-3 h-3 text-white stroke-[3]" />
                    ) : (
                      <span className="text-[10px] font-bold text-slate-600">
                        {i + 1}
                      </span>
                    )}
                  </div>

                  {/* Label */}
                  <span
                    className={cn(
                      "text-[13px] transition-colors duration-300",
                      isCurrent && "text-white font-semibold",
                      isCompleted && "text-slate-300 font-medium",
                      !isCompleted && !isCurrent && "text-slate-600"
                    )}
                  >
                    {label}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* ── Bottom Status Card ─────────────────────────────────────── */}
      <div className="px-4 pb-5">
        <div className="bg-white/[0.02] border border-white/[0.04] rounded-xl px-4 py-3.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <div>
                <p className="text-[11px] font-semibold text-slate-300 leading-tight">
                  System Status
                </p>
                <p className="text-[10px] text-slate-600 mt-0.5">
                  All systems operational
                </p>
              </div>
            </div>
            <Shield className="w-3.5 h-3.5 text-slate-700" />
          </div>
        </div>
      </div>
    </aside>
  );
}
