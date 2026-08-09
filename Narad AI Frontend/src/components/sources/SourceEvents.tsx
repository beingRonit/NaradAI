"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Clock } from "lucide-react";
import type { NewsTopic } from "@/lib/types";

function deriveDomain(name: string): string {
  const map: Record<string, string> = {
    "TechCrunch AI": "techcrunch.com",
    "The Verge AI": "theverge.com",
    "Ars Technica": "arstechnica.com",
  };
  return map[name] ?? name;
}

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  return `${hours}h ago`;
}

interface Props {
  topics: NewsTopic[];
}

export function SourceEvents({ topics }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="h-full flex flex-col"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Recent Events
      </h3>

      <div className="flex-1 space-y-0">
        {topics.length === 0 && (
          <p className="text-sm text-slate-500">No recent events</p>
        )}
        {topics.map((topic, i) => {
          const domain = deriveDomain(topic.source);
          const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
          const enrichStatus = topic.enrichment?.status ?? "UNKNOWN";
          const action = enrichStatus === "SUCCESS" ? "enriched" : enrichStatus === "FAILED" ? "failed" : "pending";

          return (
            <motion.div
              key={topic.id ?? i}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.1 * i }}
              className="flex items-start gap-3 py-3 border-b border-slate-800/40 last:border-0"
            >
              <div className="mt-0.5">
                {action === "enriched" && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                {action === "failed" && <XCircle className="w-4 h-4 text-red-400" />}
                {action === "pending" && <Clock className="w-4 h-4 text-slate-500" />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <img
                    src={faviconUrl}
                    alt={topic.source}
                    className="w-3.5 h-3.5 rounded-sm"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
                  />
                  <span className="text-xs text-slate-500">{topic.source}</span>
                  <span className="text-xs text-slate-600">·</span>
                  <span className="text-xs text-slate-600">{timeAgo(topic.discoveredAt)}</span>
                </div>
                <p className="text-sm text-slate-300 truncate">{topic.title}</p>
              </div>

              <div className="mt-0.5">
                {action === "enriched" && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-medium uppercase tracking-wider">
                    Enriched
                  </span>
                )}
                {action === "failed" && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 font-medium uppercase tracking-wider">
                    Failed
                  </span>
                )}
                {action === "pending" && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-500/15 text-slate-400 font-medium uppercase tracking-wider">
                    Pending
                  </span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
