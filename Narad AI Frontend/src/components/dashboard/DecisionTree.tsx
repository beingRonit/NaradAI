"use client";

import { motion } from "framer-motion";
import type { Candidate } from "@/lib/types";

interface Props {
  candidates: Candidate[];
}

const GAP = 8;
const funnelWidths = [100, 88, 76, 64, 52];

function buildFunnel(candidates: Candidate[]) {
  const stages = [
    { label: "Discovered", count: candidates.length },
    { label: "Scored > 50", count: candidates.filter(c => c.score != null && c.score >= 50).length },
    { label: "Scored > 60", count: candidates.filter(c => c.score != null && c.score >= 60).length },
    { label: "High Reliability", count: candidates.filter(c => c.reliability >= 65).length },
    { label: "Ready", count: candidates.filter(c => {
      return c.score != null && c.score >= 68 && c.reliability >= 65 && c.sources >= 2;
    }).length },
  ];
  return stages;
}

export function DecisionTree({ candidates }: Props) {
  const funnel = buildFunnel(candidates);

  return (
    <div className="h-full">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Editorial Funnel
      </h3>

      <div className="flex flex-col items-center" style={{ gap: `${GAP}px` }}>
        {funnel.map((node, i) => {
          const isLast = i === funnel.length - 1;
          const width = funnelWidths[i] ?? 30;
          const prevCount = i > 0 ? funnel[i - 1].count : null;
          const dropped = prevCount !== null && prevCount > node.count ? prevCount - node.count : 0;

          return (
            <motion.div
              key={node.label}
              initial={{ opacity: 0, scaleX: 0 }}
              animate={{ opacity: 1, scaleX: 1 }}
              transition={{ duration: 0.4, delay: i * 0.08, ease: "easeOut" as const }}
              className="w-full flex flex-col items-center"
            >
              <div
                className={`flex items-center justify-between px-4 py-2.5 rounded-md border ${
                  isLast
                    ? "bg-gradient-to-r from-emerald-600/30 to-emerald-500/20 border-emerald-500/30"
                    : "bg-gradient-to-r from-violet-600/20 to-violet-500/10 border-violet-500/20"
                }`}
                style={{ width: `${width}%` }}
              >
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-semibold tracking-wider ${
                    isLast ? "text-emerald-300" : "text-violet-300"
                  }`}>
                    {node.label}
                  </span>
                  {dropped > 0 && (
                    <span className="text-[9px] text-red-400/60 font-mono">
                      -{dropped}
                    </span>
                  )}
                </div>
                <span className={`text-sm font-bold ${
                  isLast ? "text-emerald-400" : "text-violet-400"
                }`}>
                  {node.count}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
