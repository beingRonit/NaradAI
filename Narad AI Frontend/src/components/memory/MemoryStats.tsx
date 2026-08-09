"use client";

import type { MemoryEntry } from "@/lib/types";

interface Props {
  entries: MemoryEntry[];
}

export function MemoryStats({ entries }: Props) {
  const total = entries.length;
  const uniqueTopics = new Set(entries.map(e => e.topic)).size;
  const allKeywords = new Set(entries.flatMap(e => e.keywords ?? []));
  const allCompanies = new Set(entries.flatMap(e => e.companies ?? []));

  const stats = [
    { label: "Total Memories", value: total, color: "text-violet-400", border: "border-l-violet-500", bg: "bg-violet-500/10" },
    { label: "Unique Topics", value: uniqueTopics, color: "text-cyan-400", border: "border-l-cyan-500", bg: "bg-cyan-500/10" },
    { label: "Keywords Tracked", value: allKeywords.size, color: "text-amber-400", border: "border-l-amber-500", bg: "bg-amber-500/10" },
    { label: "Companies Mentioned", value: allCompanies.size, color: "text-emerald-400", border: "border-l-emerald-500", bg: "bg-emerald-500/10" },
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
