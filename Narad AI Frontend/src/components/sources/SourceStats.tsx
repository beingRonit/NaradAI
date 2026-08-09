"use client";

import type { NewsSource } from "@/lib/types";

interface Props {
  sources: NewsSource[];
}

export function SourceStats({ sources }: Props) {
  const stats = [
    { label: "Total Sources", value: sources.length, color: "text-violet-400", border: "border-l-violet-500", bg: "bg-violet-500/10" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
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
