"use client";

import { motion } from "framer-motion";
import { Eye, Brain, Send, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CobeGlobe } from "@/components/ui/CobeGlobe";

interface WelcomeStepProps {
  onNext: () => void;
}

export function WelcomeStep({ onNext }: WelcomeStepProps) {
  return (
    <div className="flex flex-col items-center text-center">
      {/* ── Central Globe ─────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative w-64 h-64 mb-10"
      >
        <CobeGlobe className="w-full h-full" />
      </motion.div>

      {/* ── Heading ──────────────────────────────────────────────── */}
      <motion.h1
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="text-3xl md:text-4xl font-bold text-white mb-3"
      >
        Welcome to{" "}
        <span className="text-violet-400">Narad AI</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="text-slate-400 text-[15px] max-w-lg mb-12 leading-relaxed"
      >
        Your autonomous AI persona that discovers, analyzes and shares the most
        valuable AI &amp; Tech insights.
      </motion.p>

      {/* ── Feature Blocks ───────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="grid grid-cols-3 gap-6 mb-12 max-w-xl w-full"
      >
        {[
          {
            Icon: Eye,
            label: "Observes",
            desc: "Live information sources",
          },
          {
            Icon: Brain,
            label: "Thinks",
            desc: "Filters and judges what matters",
          },
          {
            Icon: Send,
            label: "Shares",
            desc: "Publishes valuable insights automatically",
          },
        ].map(({ Icon, label, desc }) => (
          <div key={label} className="flex flex-col items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-violet-500/[0.08] border border-violet-500/[0.15] flex items-center justify-center">
              <Icon className="w-5 h-5 text-violet-400" />
            </div>
            <div className="text-center">
              <p className="text-[13px] font-semibold text-white">{label}</p>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                {desc}
              </p>
            </div>
          </div>
        ))}
      </motion.div>

      {/* ── CTA ──────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.65 }}
      >
        <Button
          onClick={onNext}
          className="bg-violet-600 hover:bg-violet-500 text-white px-7 py-5 text-[13px] font-semibold rounded-lg transition-all duration-300 shadow-[0_0_24px_rgba(139,92,246,0.25)] hover:shadow-[0_0_32px_rgba(139,92,246,0.35)]"
        >
          Let&apos;s Get Started
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </motion.div>
    </div>
  );
}
