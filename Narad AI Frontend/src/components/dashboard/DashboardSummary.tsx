"use client";

import type { AgentStatusResponse, Candidate } from "@/lib/types";

interface Props {
  status: AgentStatusResponse | null;
  candidates: Candidate[];
}

export function DashboardSummary({ status, candidates }: Props) {
  const rejected = candidates.filter(c => {
    const s = (c.status ?? "").toUpperCase();
    return s !== "ACTIVE" && s !== "SHORTLISTED" && s !== "PUBLISHED";
  }).length;

  const stats = [
    { label: "Topics discovered", value: status?.cycle?.candidates ?? candidates.length, color: "text-violet-400" },
    { label: "Topics rejected", value: rejected, color: "text-red-400" },
    { label: "Posts published", value: status?.posts ?? 0, color: "text-emerald-400" },
    { label: "Memory entries", value: status?.memoryEntries ?? 0, color: "text-cyan-400" },
    { label: "Cycles completed", value: status?.cycle?.historical_cycles ?? 0, color: "text-amber-400" },
  ];

  return (
    <div className="h-full">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Summary
      </h3>

      <div className="space-y-3">
        {stats.map((stat) => (
          <div key={stat.label} className="flex items-center justify-between">
            <span className="text-sm text-slate-400">{stat.label}</span>
            <span className={`text-sm font-bold ${stat.color}`}>{stat.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
