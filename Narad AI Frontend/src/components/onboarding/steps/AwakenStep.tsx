"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowLeft, Check, Loader2, AlertCircle } from "lucide-react";
import { ParticleButton } from "@/components/ui/particle-button";
import type { OnboardingData } from "@/lib/types";

interface AwakenStepProps {
  data: OnboardingData;
  onBack: () => void;
  onComplete: (data: OnboardingData) => void;
  initializing: boolean;
  error: string | null;
}

const CHECKLIST_LEFT = [
  "Connecting to live sources",
  "Loading memory systems",
  "Initializing editorial engine",
];

const CHECKLIST_RIGHT = [
  "Starting autonomous loop",
  "Ready to discover & share",
  "Narad will awaken shortly...",
];

export function AwakenStep({ data, onBack, onComplete, initializing, error }: AwakenStepProps) {
  const [completedCount, setCompletedCount] = useState(0);
  const totalItems = CHECKLIST_LEFT.length + CHECKLIST_RIGHT.length;

  useEffect(() => {
    const interval = setInterval(() => {
      setCompletedCount((prev) => {
        if (prev >= totalItems) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 480);

    return () => clearInterval(interval);
  }, [totalItems]);

  const allComplete = completedCount >= totalItems;

  const renderCheckItem = (text: string, index: number) => {
    const isComplete = index < completedCount;
    return (
      <div key={text} className="flex items-center gap-3 py-1.5">
        <div className="w-5 h-5 shrink-0">
          {isComplete ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 400, damping: 18 }}
              className="w-5 h-5 rounded-full bg-violet-500 flex items-center justify-center shadow-[0_0_10px_rgba(139,92,246,0.3)]"
            >
              <Check className="w-3 h-3 text-white stroke-[3]" />
            </motion.div>
          ) : (
            <div className="w-5 h-5 rounded-full border-2 border-slate-700" />
          )}
        </div>
        <span
          className={`text-[12px] transition-colors duration-300 ${
            isComplete ? "text-slate-200" : "text-slate-600"
          }`}
        >
          {text}
        </span>
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 18 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35 }}
      className="flex flex-col items-center text-center"
    >
      {/* ── Header ──────────────────────────────────────────────── */}
      <h2 className="text-2xl font-bold text-white mb-2">
        Awaken{" "}
        <span className="text-violet-400">Narad</span>
      </h2>
      <p className="text-slate-400 text-[13px] mb-10 max-w-md leading-relaxed">
        Narad will start observing the world and sharing valuable insights.
      </p>

      {/* ── Central Avatar with Glow ────────────────────────────── */}
      <div className="relative w-80 h-80 mb-10">
        {/* Outermost diffuse glow */}
        <div className="absolute inset-0 rounded-full bg-violet-500/[0.05] blur-2xl" />

        {/* Outer orbit ring */}
        <motion.div
          className="absolute inset-2 rounded-full border border-violet-500/15"
          animate={{ rotate: 360 }}
          transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
        />

        {/* Middle orbit ring */}
        <motion.div
          className="absolute inset-9 rounded-full border border-violet-400/10"
          animate={{ rotate: -360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />

        {/* Inner glow halo */}
        <motion.div
          className="absolute inset-12 rounded-full bg-violet-500/[0.08] blur-lg"
          animate={{ opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Avatar */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="relative w-[174px] h-[174px] rounded-full overflow-hidden border-2 border-violet-500/40"
            animate={{
              boxShadow: [
                "0 0 30px rgba(139,92,246,0.25), 0 0 60px rgba(139,92,246,0.08)",
                "0 0 50px rgba(139,92,246,0.4), 0 0 100px rgba(139,92,246,0.12)",
                "0 0 30px rgba(139,92,246,0.25), 0 0 60px rgba(139,92,246,0.08)",
              ],
            }}
            transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
          >
            <Image
              src="/Logo.png"
              alt="Narad AI"
              fill
              className="object-cover"
              priority
            />
          </motion.div>
        </div>

        {/* Star particles */}
        {[
          { top: "3%", left: "50%", delay: 0 },
          { top: "18%", left: "92%", delay: 0.7 },
          { top: "78%", left: "4%", delay: 1.3 },
          { top: "88%", left: "82%", delay: 0.4 },
          { top: "10%", left: "8%", delay: 1.0 },
          { top: "70%", left: "95%", delay: 0.2 },
          { top: "92%", left: "45%", delay: 0.8 },
          { top: "42%", left: "0%", delay: 1.5 },
          { top: "5%", left: "75%", delay: 0.5 },
          { top: "60%", left: "2%", delay: 1.1 },
        ].map((star, i) => (
          <motion.div
            key={i}
            className="absolute w-[2px] h-[2px] bg-white/40 rounded-full"
            style={{ top: star.top, left: star.left }}
            animate={{ opacity: [0.15, 0.7, 0.15], scale: [1, 1.5, 1] }}
            transition={{
              duration: 2.2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: star.delay,
            }}
          />
        ))}
      </div>

      {/* ── Checklist — Two Columns ─────────────────────────────── */}
      <div className="grid grid-cols-2 gap-x-14 gap-y-0 mb-10 text-left w-full max-w-lg">
        <div>
          {CHECKLIST_LEFT.map((item, i) => renderCheckItem(item, i))}
        </div>
        <div>
          {CHECKLIST_RIGHT.map((item, i) =>
            renderCheckItem(item, CHECKLIST_LEFT.length + i)
          )}
        </div>
      </div>

      {/* ── Error Message ───────────────────────────────────────── */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-xs text-red-400 mb-4 px-1"
        >
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          {error}
        </motion.div>
      )}

      {/* ── Awaken Button ───────────────────────────────────────── */}
      <ParticleButton
        onClick={() => onComplete(data)}
        disabled={!allComplete || initializing}
        className="bg-violet-600 hover:bg-violet-500 text-white px-8 py-5 text-[13px] font-semibold rounded-lg transition-all duration-300 shadow-[0_0_24px_rgba(139,92,246,0.3)] hover:shadow-[0_0_32px_rgba(139,92,246,0.4)] disabled:opacity-30 disabled:cursor-not-allowed disabled:shadow-none"
      >
        {initializing ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Initializing...
          </>
        ) : allComplete ? (
          "Awaken Narad 🚀"
        ) : (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Preparing...
          </>
        )}
      </ParticleButton>

      {/* ── Back link ───────────────────────────────────────────── */}
      <button
        onClick={onBack}
        disabled={initializing}
        className="mt-5 text-[12px] text-slate-600 hover:text-slate-400 transition-colors inline-flex items-center gap-1.5 disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Go back
      </button>
    </motion.div>
  );
}
