"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/AppShell";
import { BentoCard, staggerContainer } from "@/components/ui/BentoCard";
import { IntelligenceStats } from "@/components/intelligence/IntelligenceStats";
import { DiscoveryTrend } from "@/components/intelligence/DiscoveryTrend";
import { EditorialDecisions } from "@/components/intelligence/EditorialDecisions";
import { SourcePerformance } from "@/components/intelligence/SourcePerformance";
import { getCandidates, getStatus } from "@/lib/api";
import type { Candidate, AgentStatusResponse } from "@/lib/types";

const POLL_MS = 30_000;

export default function IntelligencePage() {
  const agentId = typeof window !== "undefined" ? localStorage.getItem("narad-agent-id") : null;

  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [status, setStatus] = useState<AgentStatusResponse | null>(null);

  const fetchData = useCallback(async () => {
    if (!agentId) return;
    try {
      const [cRes, sRes] = await Promise.allSettled([
        getCandidates(agentId, false),
        getStatus(agentId),
      ]);
      if (cRes.status === "fulfilled") setCandidates(cRes.value.candidates);
      if (sRes.status === "fulfilled") setStatus(sRes.value);
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
          <h1 className="text-2xl font-bold text-white">Intelligence</h1>
          <p className="text-slate-400 text-sm mt-1">
            Understanding Narad&apos;s decision-making
          </p>
        </div>

        <IntelligenceStats candidates={candidates} status={status} />

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
                <DiscoveryTrend candidates={candidates} />
              </BentoCard>
            </motion.div>
            <motion.div variants={staggerContainer}>
              <BentoCard>
                <EditorialDecisions candidates={candidates} />
              </BentoCard>
            </motion.div>
          </div>

          <motion.div variants={staggerContainer}>
            <BentoCard>
              <SourcePerformance candidates={candidates} />
            </BentoCard>
          </motion.div>
        </motion.div>
      </div>
    </AppShell>
  );
}
