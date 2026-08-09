"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { MemoryEntry } from "@/lib/types";

interface Props {
  entries: MemoryEntry[];
}

function buildKeywordFrequency(entries: MemoryEntry[]) {
  const freq: Record<string, number> = {};
  for (const e of entries) {
    for (const kw of e.keywords ?? []) {
      freq[kw] = (freq[kw] ?? 0) + 1;
    }
  }
  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([keyword, count]) => ({ keyword, count }));
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) => {
  if (!active || !payload?.[0]) return null;
  return (
    <div className="bg-[#0b101f] border border-slate-700 rounded-lg p-3 shadow-lg">
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className="text-sm text-white font-medium">{payload[0].value} mentions</p>
    </div>
  );
};

export function MemoryOverview({ entries }: Props) {
  const data = buildKeywordFrequency(entries);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="h-full flex flex-col"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Top Keywords
      </h3>

      <div className="flex-1 min-h-[220px]">
        {data.length === 0 ? (
          <p className="text-sm text-slate-500 mt-8 text-center">No memory data yet</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 10, left: 60, bottom: 0 }}>
              <XAxis type="number" tick={{ fontSize: 11, fill: "#64748B" }} axisLine={{ stroke: "#1E293B" }} allowDecimals={false} />
              <YAxis type="category" dataKey="keyword" tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} width={60} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </motion.div>
  );
}
