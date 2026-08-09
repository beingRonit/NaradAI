"use client";

import type { Candidate, AgentStatusResponse } from "@/lib/types";

interface Props {
  candidates: Candidate[];
  status: AgentStatusResponse | null;
}

export function IntelligenceStats({ candidates, status }: Props) {
  const discovered = status?.cycle?.candidates ?? candidates.length;
  const scoredAbove50 = candidates.filter(c => c.score != null && c.score >= 50).length;
  const highReliability = candidates.filter(c => c.reliability >= 65).length;
  const multiSource = candidates.filter(c => c.sources >= 2).length;

  const stats = [
    { label: "Discovered", value: discovered, color: "text-violet-400", border: "border-l-violet-500", bg: "bg-violet-500/10" },
    { label: "Scored > 50", value: scoredAbove50, color: "text-cyan-400", border: "border-l-cyan-500", bg: "bg-cyan-500/10" },
    { label: "High Reliability", value: highReliability, color: "text-amber-400", border: "border-l-amber-500", bg: "bg-amber-500/10" },
    { label: "Multi-Source", value: multiSource, color: "text-emerald-400", border: "border-l-emerald-500", bg: "bg-emerald-500/10" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`bg-[#0f1423] border border-slate-700/60 border-l-2 ${stat.border} rounded-xl p-4 ${stat.bg} backdrop-blur-sm`}
        >
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">{stat.label}</p>
          <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
}
