"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/AppShell";
import { BentoCard, staggerContainer } from "@/components/ui/BentoCard";
import { MemoryStats } from "@/components/memory/MemoryStats";
import { MemoryOverview } from "@/components/memory/MemoryOverview";
import { MemoryMatch } from "@/components/memory/MemoryMatch";
import { MemoryTable } from "@/components/memory/MemoryTable";
import { getMemory } from "@/lib/api";
import type { MemoryEntry } from "@/lib/types";

const POLL_MS = 30_000;

export default function MemoryPage() {
  const agentId = typeof window !== "undefined" ? localStorage.getItem("narad-agent-id") : null;
  const [entries, setEntries] = useState<MemoryEntry[]>([]);

  const fetchData = useCallback(async () => {
    if (!agentId) return;
    try {
      const res = await getMemory(agentId);
      setEntries(res.memory ?? []);
    } catch { /* silent */ }
  }, [agentId]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, POLL_MS);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Memory</h1>
          <p className="text-slate-400 text-sm mt-1">
            What Narad remembers
          </p>
        </div>

        <MemoryStats entries={entries} />

        <motion.div
          className="grid gap-5"
          initial="hidden"
          variants={staggerContainer}
          viewport={{ once: true }}
          whileInView="visible"
        >
          <div className="grid gap-5 md:grid-cols-2">
            <motion.div variants={staggerContainer}>
              <BentoCard>
                <MemoryOverview entries={entries} />
              </BentoCard>
            </motion.div>
            <motion.div variants={staggerContainer}>
              <BentoCard>
                <MemoryMatch entries={entries} />
              </BentoCard>
            </motion.div>
          </div>

          <motion.div variants={staggerContainer}>
            <BentoCard>
              <MemoryTable entries={entries} />
            </BentoCard>
          </motion.div>
        </motion.div>
      </div>
    </AppShell>
  );
}
