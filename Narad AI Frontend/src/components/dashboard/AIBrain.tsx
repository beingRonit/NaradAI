"use client";

import { motion } from "framer-motion";
import type { AgentStatusResponse } from "@/lib/types";

const stateMap: Record<string, { label: string; description: string }> = {
  idle: { label: "IDLE", description: "Waiting for next cycle" },
  scanning: { label: "SCANNING", description: "Finding topics from live sources" },
  judging: { label: "JUDGING", description: "Evaluating quality and relevance" },
  checking_memory: { label: "CHECKING MEMORY", description: "Comparing against past posts" },
  writing: { label: "WRITING", description: "Generating publication" },
  publishing: { label: "PUBLISHING", description: "Saving to feed" },
  sleeping: { label: "SLEEPING", description: "Waiting for next cycle" },
};

interface Props {
  status: AgentStatusResponse | null;
}

export function AIBrain({ status }: Props) {
  const isRunning = status?.running ?? false;
  const mode = isRunning ? "scanning" : "idle";
  const state = stateMap[mode] ?? stateMap.idle;

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="relative w-40 h-40 mb-4">
        <motion.div
          className="absolute inset-0 border-2 border-violet-500/40 rounded-full"
          style={{ borderTopColor: "transparent" }}
          animate={{ rotate: isRunning ? 360 : 0 }}
          transition={{ duration: 3, repeat: isRunning ? Infinity : 0, ease: "linear" }}
        />

        <motion.div
          className="absolute inset-3 bg-gradient-to-br from-violet-500/20 to-violet-700/10 rounded-full"
          animate={{ scale: isRunning ? [1, 1.1, 1] : 1 }}
          transition={{ duration: 2, repeat: isRunning ? Infinity : 0, ease: "easeInOut" }}
        />

        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="w-10 h-10 bg-violet-500 rounded-full glow-violet-sm"
            animate={{ scale: isRunning ? [1, 1.2, 1] : 1 }}
            transition={{ duration: 1.5, repeat: isRunning ? Infinity : 0, ease: "easeInOut" }}
          />
        </div>
      </div>

      <motion.div
        key={state.label}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mt-6"
      >
        <p className="text-base font-bold text-violet-400 tracking-wider">
          {state.label}
        </p>
        <p className="text-sm text-slate-500 mt-1">{state.description}</p>
        {status?.cycle && (
          <p className="text-xs text-slate-600 mt-2">
            {status.cycle.historical_cycles} cycles · {status.memoryEntries} memories
          </p>
        )}
      </motion.div>
    </div>
  );
}
