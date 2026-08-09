"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import type { AgentStatusResponse, Candidate, Post } from "@/lib/types";

interface LogEntry {
  timestamp: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
}

function buildLogsFromState(
  status: AgentStatusResponse | null,
  candidates: Candidate[],
  posts: Post[]
): LogEntry[] {
  const logs: LogEntry[] = [];
  const now = new Date();
  const ts = (m: number) => {
    const d = new Date(now.getTime() - m * 60_000);
    return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
  };

  if (!status) {
    logs.push({ timestamp: ts(1), message: "Waiting for agent status...", type: "info" });
    return logs;
  }

  logs.push({ timestamp: ts(10), message: `Agent started — ${status.running ? "running" : "idle"} mode`, type: "info" });
  logs.push({ timestamp: ts(9), message: `${status.cycle?.candidates ?? 0} candidates in funnel`, type: "success" });

  const recent = candidates.slice(0, 5);
  for (const c of recent) {
    const verdict = c.status === "PUBLISHED" ? "✓ Published" : c.status === "SHORTLISTED" ? "Shortlisted" : `${c.status}`;
    logs.push({ timestamp: ts(7), message: `"${c.title.slice(0, 50)}" → ${verdict}`, type: c.status === "PUBLISHED" ? "success" : "warning" });
  }

  if (posts.length > 0) {
    logs.push({ timestamp: ts(2), message: `${posts.length} posts published`, type: "success" });
  }

  return logs;
}

interface Props {
  status: AgentStatusResponse | null;
  candidates: Candidate[];
  posts: Post[];
}

export function LiveAgentConsole({ status, candidates, posts }: Props) {
  const [visibleLogs, setVisibleLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevHash = useRef("");

  useEffect(() => {
    const hash = `${status?.running}-${candidates.length}-${posts.length}`;
    if (hash === prevHash.current) return;
    prevHash.current = hash;
    setVisibleLogs(buildLogsFromState(status, candidates, posts));
  }, [status, candidates, posts]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [visibleLogs]);

  const getLogColor = (type: string) => {
    switch (type) {
      case "success": return "text-emerald-400";
      case "warning": return "text-amber-400";
      case "error": return "text-red-400";
      default: return "text-slate-400";
    }
  };

  return (
    <div className="bg-[#0b101f] border border-slate-800/50 rounded-xl overflow-hidden h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Live Agent Console
        </span>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${status?.running ? "bg-emerald-500 animate-pulse" : "bg-slate-600"}`} />
          <span className={`text-xs font-medium ${status?.running ? "text-emerald-400" : "text-slate-500"}`}>
            {status?.running ? "LIVE" : "IDLE"}
          </span>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-sm min-h-[200px]"
      >
        <div className="text-violet-400 mb-2">
          $ narad://autonomous-loop
        </div>

        <div className="space-y-1">
          {visibleLogs.map((log, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              className="flex gap-2"
            >
              <span className="text-slate-600">[{log.timestamp}]</span>
              <span className={getLogColor(log.type)}>{log.message}</span>
            </motion.div>
          ))}
        </div>

        <div className="mt-2 text-violet-400">
          $ <span className="animate-pulse">_</span>
        </div>
      </div>
    </div>
  );
}
