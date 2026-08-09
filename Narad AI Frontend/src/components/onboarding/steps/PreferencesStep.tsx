"use client";

import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { OnboardingData } from "@/lib/types";

interface PreferencesStepProps {
  data: OnboardingData;
  onUpdate: (partial: Partial<OnboardingData>) => void;
  onBack: () => void;
  onNext: () => void;
}

const TOPIC_OPTIONS = [
  "AI Agents",
  "LLMs",
  "Machine Learning",
  "Robotics",
  "Open Source",
  "AI Safety",
  "Productivity",
  "Future Tech",
  "Data Science",
  "Research",
];

const TONE_OPTIONS = [
  "Insightful & Thoughtful",
  "Technical & Precise",
  "Bold & Opinionated",
  "Friendly & Approachable",
];

export function PreferencesStep({
  data,
  onUpdate,
  onBack,
  onNext,
}: PreferencesStepProps) {
  const parseFrequency = () => {
    const parts = data.frequency.split(/[:\s]/);
    return {
      hour: parts[0] || "",
      minute: parts[1] || "",
      period: parts[2] || "AM",
    };
  };

  const isValidHour = (val: string) => {
    if (val === "") return true;
    const num = parseInt(val);
    return !isNaN(num) && num >= 1 && num <= 12;
  };

  const isValidMinute = (val: string) => {
    if (val === "") return true;
    const num = parseInt(val);
    return !isNaN(num) && num >= 0 && num <= 59;
  };

  const toggleTopic = (topic: string) => {
    const current = data.topics;
    if (current.includes(topic)) {
      onUpdate({ topics: current.filter((t) => t !== topic) });
    } else {
      onUpdate({ topics: [...current, topic] });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 18 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35 }}
    >
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">Set your preferences</h2>
        <p className="text-slate-400 text-[13px] mt-1.5">
          Choose what Narad AI should focus on and how it should operate.
        </p>
      </div>

      {/* ── Topics of Interest ──────────────────────────────────── */}
      <div className="mb-8">
        <label className="text-[12px] font-semibold text-slate-500 mb-3 block uppercase tracking-wider">
          Topics of Interest
        </label>
        <div className="flex flex-wrap gap-2">
          {TOPIC_OPTIONS.map((topic) => {
            const isSelected = data.topics.includes(topic);
            return (
              <motion.button
                key={topic}
                onClick={() => toggleTopic(topic)}
                whileTap={{ scale: 0.92 }}
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 400, damping: 17 }}
                className={cn(
                  "inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-[12px] font-medium border",
                  isSelected
                    ? "bg-violet-500/15 text-violet-300 border-violet-500/30"
                    : "bg-slate-900/50 text-slate-500 border-slate-800 hover:border-slate-700 hover:text-slate-400"
                )}
              >
                {isSelected && <Check className="w-3 h-3" />}
                {topic}
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* ── Time + Tone ────────────────────────────────────── */}
      <div className="grid sm:grid-cols-2 gap-5 mb-8">
        <div>
          <label className="text-[12px] font-semibold text-slate-500 mb-1.5 block uppercase tracking-wider">
            Publishing Time
          </label>
          <div className="flex gap-2 items-start">
            {/* Hour */}
            <div className="flex-1">
              <input
                type="text"
                maxLength={2}
                value={parseFrequency().hour}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, "");
                  const { minute, period } = parseFrequency();
                  onUpdate({ frequency: `${val}:${minute} ${period}` });
                }}
                onBlur={(e) => {
                  const val = e.target.value;
                  if (val !== "") {
                    const padded = val.padStart(2, "0");
                    const { minute, period } = parseFrequency();
                    onUpdate({ frequency: `${padded}:${minute} ${period}` });
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.currentTarget.blur();
                  }
                }}
                className={cn(
                  "w-full h-10 px-2 rounded-md bg-slate-900/50 border text-white text-[13px] text-center focus:outline-none focus:ring-1 focus:ring-violet-500/50",
                  isValidHour(parseFrequency().hour) ? "border-slate-800" : "border-red-500/50"
                )}
                placeholder="07"
              />
            </div>

            <span className="text-slate-600 text-[13px] mt-2">:</span>

            {/* Minute */}
            <div className="flex-1">
              <input
                type="text"
                maxLength={2}
                value={parseFrequency().minute}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, "");
                  const { hour, period } = parseFrequency();
                  onUpdate({ frequency: `${hour}:${val} ${period}` });
                }}
                onBlur={(e) => {
                  const val = e.target.value;
                  if (val !== "") {
                    const padded = val.padStart(2, "0");
                    const { hour, period } = parseFrequency();
                    onUpdate({ frequency: `${hour}:${padded} ${period}` });
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.currentTarget.blur();
                  }
                }}
                className={cn(
                  "w-full h-10 px-2 rounded-md bg-slate-900/50 border text-white text-[13px] text-center focus:outline-none focus:ring-1 focus:ring-violet-500/50",
                  isValidMinute(parseFrequency().minute) ? "border-slate-800" : "border-red-500/50"
                )}
                placeholder="30"
              />
            </div>

            {/* AM/PM Toggle */}
            <motion.button
              type="button"
              whileTap={{ scale: 0.92 }}
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
              onClick={() => {
                const { hour, minute } = parseFrequency();
                const newPeriod = parseFrequency().period === "AM" ? "PM" : "AM";
                onUpdate({ frequency: `${hour}:${minute} ${newPeriod}` });
              }}
              className="w-16 h-10 rounded-md bg-slate-900/50 border border-slate-800 text-white text-[13px] font-semibold cursor-pointer hover:bg-slate-800/50 hover:border-slate-700 transition-colors"
            >
              {parseFrequency().period}
            </motion.button>
          </div>

        </div>

        <div>
          <label className="text-[12px] font-semibold text-slate-500 mb-1.5 block uppercase tracking-wider">
            Tone of Voice
          </label>
          <select
            value={data.tone}
            onChange={(e) => onUpdate({ tone: e.target.value })}
            className="w-full h-10 px-3 rounded-md bg-slate-900/50 border border-slate-800 text-white text-[13px] appearance-none cursor-pointer"
          >
            {TONE_OPTIONS.map((opt) => (
              <option key={opt} value={opt} className="bg-[#0D0D14]">
                {opt}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-slate-600 mt-1.5">
            How should Narad communicate?
          </p>
        </div>
      </div>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <div className="flex justify-between mt-10">
        <Button
          variant="ghost"
          onClick={onBack}
          className="text-slate-500 hover:text-white hover:bg-white/[0.04] text-[13px]"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <Button
          onClick={onNext}
          className="bg-violet-600 hover:bg-violet-500 text-white px-6 rounded-lg font-semibold text-[13px] shadow-[0_0_18px_rgba(139,92,246,0.2)]"
        >
          Next
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}
