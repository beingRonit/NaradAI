"use client";

import { motion } from "framer-motion";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { Candidate } from "@/lib/types";

const COLORS = ["#8B5CF6", "#EF4444", "#F59E0B", "#06B6D4", "#64748B"];

function buildDecisionData(candidates: Candidate[]) {
  const verdictCounts: Record<string, number> = {};
  for (const c of candidates) {
    let bucket = "Unknown";
    if (c.score != null && c.score >= 68 && c.reliability >= 65 && c.sources >= 2) {
      bucket = "Ready";
    } else if (c.score != null && c.score >= 60) {
      bucket = "High Score";
    } else if (c.reliability >= 65) {
      bucket = "Reliable";
    } else if (c.sources >= 2) {
      bucket = "Multi-Source";
    } else {
      bucket = "Below Threshold";
    }
    verdictCounts[bucket] = (verdictCounts[bucket] ?? 0) + 1;
  }
  return Object.entries(verdictCounts)
    .map(([reason, count]) => ({ reason, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: { reason: string; count: number } }> }) => {
  if (!active || !payload?.[0]) return null;
  return (
    <div className="bg-[#0b101f] border border-slate-700 rounded-lg p-3 shadow-lg">
      <p className="text-xs text-slate-400">{payload[0].payload.reason}</p>
      <p className="text-sm text-white font-medium">{payload[0].payload.count} topics</p>
    </div>
  );
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const renderCustomLabel = (props: any) => {
  const { cx, cy, midAngle, innerRadius, outerRadius, percent } = props;
  if (!percent || percent < 0.08) return null;
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" className="text-[11px] font-bold">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

interface Props {
  candidates: Candidate[];
}

export function EditorialDecisions({ candidates }: Props) {
  const data = buildDecisionData(candidates);
  const total = data.reduce((sum, d) => sum + d.count, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="h-full flex flex-col"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-5">
        Editorial Decisions
      </h3>

      <div className="flex-1 flex items-center gap-6">
        <div className="w-1/2 h-52 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={65} outerRadius={95} paddingAngle={3} dataKey="count" labelLine={false} label={renderCustomLabel}>
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="none" />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="w-1/2 space-y-3">
          {data.map((item, i) => {
            const pct = total > 0 ? Math.round((item.count / total) * 100) : 0;
            return (
              <div key={item.reason} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                    <span className="text-sm text-slate-300">{item.reason}</span>
                  </div>
                  <span className="text-sm font-bold text-white">{item.count}</span>
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.6, delay: 0.4 + i * 0.1 }}
                    className="h-full rounded-full"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
