"use client";

import { motion } from "framer-motion";
import type { Cycle } from "@/lib/types";

interface Props {
  cycles: Cycle[];
}

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function AgentTimeline({ cycles }: Props) {
  const events = cycles.slice(0, 8);

  return (
    <div className="h-full">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Agent Timeline
      </h3>

      <div className="relative">
        <div className="absolute left-[5px] top-2 bottom-2 w-px bg-slate-800" />

        <div className="space-y-4">
          {events.length === 0 && (
            <p className="text-sm text-slate-500 ml-6">No cycles recorded yet</p>
          )}
          {events.map((cycle, i) => {
            const cycleId = cycle.cycle_id ?? i;
            const startedAt = cycle.started_at ?? "";
            const discovered = Array.isArray(cycle.discovered_topics) ? cycle.discovered_topics.length : 0;

            return (
              <motion.div
                key={cycleId}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: i * 0.08 }}
                className="flex gap-3 relative"
              >
                <div className="w-3 h-3 rounded-full mt-1 shrink-0 z-10 bg-violet-500" />
                <div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs font-mono text-slate-500">
                      {startedAt ? timeAgo(startedAt) : "recent"}
                    </span>
                    <span className="text-sm font-medium text-slate-300">
                      Cycle {cycle.cycle_id ?? i + 1}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {discovered} topics discovered
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
