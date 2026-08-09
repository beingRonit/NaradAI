"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { OnboardingData } from "@/lib/types";

interface PersonaSetupStepProps {
  data: OnboardingData;
  onUpdate: (partial: Partial<OnboardingData>) => void;
  onBack: () => void;
  onNext: () => void;
}

const domains = [
  "AI & Technology",
  "AI Security",
  "Machine Learning",
  "Robotics",
  "Data Science",
  "Developer Tools",
];

const defaultBio =
  "An inquisitive AI sage that explores the future of technology and shares meaningful insights.";

export function PersonaSetupStep({
  data,
  onUpdate,
  onBack,
  onNext,
}: PersonaSetupStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 18 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35 }}
    >
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">
          Let&apos;s create your persona
        </h2>
        <p className="text-slate-400 text-[13px] mt-1.5">
          This helps Narad AI stay consistent in voice and focus.
        </p>
      </div>

      {/* ── Two-column layout ───────────────────────────────────── */}
      <div className="grid md:grid-cols-5 gap-8 items-start">
        {/* Form — left 3 cols */}
        <div className="md:col-span-3 space-y-5">
          {/* Persona Name */}
          <div>
            <label className="text-[12px] font-medium text-slate-400 mb-1.5 block">
              Persona Name
            </label>
            <Input
              value={data.name}
              onChange={(e) => onUpdate({ name: e.target.value })}
              className="bg-white/[0.03] border-white/[0.07] text-white placeholder:text-slate-700 h-10 text-[13px]"
              placeholder="Narad"
            />
            <p className="text-[11px] text-slate-600 mt-1.5">
              This will be the identity of your AI persona.
            </p>
          </div>

          {/* Domain */}
          <div>
            <label className="text-[12px] font-medium text-slate-400 mb-1.5 block">
              Domain / Focus Area
            </label>
            <select
              value={data.domain}
              onChange={(e) => onUpdate({ domain: e.target.value })}
              className="w-full h-10 px-3 rounded-md bg-white/[0.03] border border-white/[0.07] text-white text-[13px] appearance-none cursor-pointer"
            >
              {domains.map((d) => (
                <option key={d} value={d} className="bg-[#0D0D14]">
                  {d}
                </option>
              ))}
            </select>
            <p className="text-[11px] text-slate-600 mt-1.5">
              Primary area Narad will focus on.
            </p>
          </div>

          {/* Bio */}
          <div>
            <label className="text-[12px] font-medium text-slate-400 mb-1.5 block">
              Short Bio{" "}
              <span className="text-slate-600 font-normal">(Optional)</span>
            </label>
            <Textarea
              value={data.bio}
              onChange={(e) => {
                if (e.target.value.length <= 160) {
                  onUpdate({ bio: e.target.value });
                }
              }}
              className="bg-white/[0.03] border-white/[0.07] text-white placeholder:text-slate-700 min-h-[88px] resize-none text-[13px]"
              placeholder={defaultBio}
            />
            <p className="text-[11px] text-slate-600 mt-1 text-right">
              {data.bio.length}/160
            </p>
          </div>
        </div>

        {/* Preview Card — right 2 cols */}
        <div className="md:col-span-2">
          <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest mb-3">
            Preview
          </p>
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-6">
            <div className="flex flex-col items-center text-center">
              {/* Avatar */}
              <div className="relative w-16 h-16 rounded-full overflow-hidden border-2 border-violet-500/30 mb-3 shadow-[0_0_20px_rgba(139,92,246,0.15)]">
                <Image
                  src="/Logo.png"
                  alt="Narad AI"
                  fill
                  className="object-cover"
                />
              </div>

              {/* Name */}
              <h3 className="text-[15px] font-bold text-white">
                {data.name || "Narad"}
              </h3>

              {/* Domain */}
              <p className="text-[11px] text-violet-400 mt-1">{data.domain}</p>

              {/* Bio */}
              <p className="text-[11px] text-slate-500 mt-3 leading-relaxed max-w-[200px]">
                {data.bio || defaultBio}
              </p>
            </div>
          </div>
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
