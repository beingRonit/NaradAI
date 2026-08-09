"use client";

import { motion } from "framer-motion";
import type { Candidate } from "@/lib/types";

function buildSourceStats(candidates: Candidate[]) {
  const byPath: Record<string, { count: number; avgScore: number; totalScore: number }> = {};
  for (const c of candidates) {
    const path = c.path ?? "unknown";
    if (!byPath[path]) byPath[path] = { count: 0, avgScore: 0, totalScore: 0 };
    byPath[path].count++;
    byPath[path].totalScore += c.score ?? 0;
  }
  return Object.entries(byPath)
    .map(([name, data]) => ({
      name,
      count: data.count,
      avgScore: data.count > 0 ? (data.totalScore / data.count).toFixed(1) : "0.0",
    }))
    .sort((a, b) => b.count - a.count);
}

interface Props {
  candidates: Candidate[];
}

export function SourcePerformance({ candidates }: Props) {
  const sources = buildSourceStats(candidates);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className="bg-slate-900/50 border border-slate-800 rounded-xl p-5"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Path Performance
      </h3>

      <div className="space-y-3">
        {sources.length === 0 && (
          <p className="text-sm text-slate-500">No source data yet</p>
        )}
        {sources.map((source) => {
          return (
            <div key={source.name} className="flex items-center justify-between py-2 border-b border-slate-800/50 last:border-0">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center text-xs font-bold text-violet-400">
                  {source.name.charAt(0).toUpperCase()}
                </span>
                <span className="text-sm text-slate-300 capitalize">{source.name}</span>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <span className="text-slate-400">{source.count} candidates</span>
                <span className="text-violet-400 font-medium">avg {source.avgScore}</span>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
