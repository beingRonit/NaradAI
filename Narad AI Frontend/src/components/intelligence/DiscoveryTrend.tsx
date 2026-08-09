"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { Candidate } from "@/lib/types";

interface Props {
  candidates: Candidate[];
}

function buildScoreDistribution(candidates: Candidate[]) {
  const buckets = [
    { range: "0-30", min: 0, max: 30, count: 0 },
    { range: "30-40", min: 30, max: 40, count: 0 },
    { range: "40-50", min: 40, max: 50, count: 0 },
    { range: "50-60", min: 50, max: 60, count: 0 },
    { range: "60-70", min: 60, max: 70, count: 0 },
    { range: "70+", min: 70, max: Infinity, count: 0 },
  ];
  for (const c of candidates) {
    const s = c.score ?? 0;
    for (const b of buckets) {
      if (s >= b.min && s < b.max) {
        b.count++;
        break;
      }
    }
  }
  return buckets.map(({ range, count }) => ({ range, count }));
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) => {
  if (!active || !payload?.[0]) return null;
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
      <p className="text-xs text-slate-400 mb-1">Score {label}</p>
      <p className="text-sm text-white font-medium">{payload[0].value} candidates</p>
    </div>
  );
};

export function DiscoveryTrend({ candidates }: Props) {
  const data = buildScoreDistribution(candidates);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-slate-900/50 border border-slate-800 rounded-xl p-5"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Score Distribution
      </h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="range" tick={{ fontSize: 11, fill: "#64748B" }} axisLine={{ stroke: "#1E293B" }} />
            <YAxis tick={{ fontSize: 11, fill: "#64748B" }} axisLine={{ stroke: "#1E293B" }} allowDecimals={false} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" name="Candidates" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-center gap-6 mt-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-violet-500" />
          <span className="text-xs text-slate-400">Candidates by score range</span>
        </div>
      </div>
    </motion.div>
  );
}
