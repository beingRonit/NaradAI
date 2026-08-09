"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/AppShell";
import { BentoCard, staggerContainer } from "@/components/ui/BentoCard";
import { LatestPublication } from "@/components/dashboard/LatestPublication";
import { AIBrain } from "@/components/dashboard/AIBrain";
import { LiveAgentConsole } from "@/components/dashboard/LiveAgentConsole";
import { DashboardSummary } from "@/components/dashboard/DashboardSummary";
import { AgentTimeline } from "@/components/dashboard/AgentTimeline";
import { DecisionTree } from "@/components/dashboard/DecisionTree";
import { getStatus, getFeed, getCandidates, getCycles } from "@/lib/api";
import type { AgentStatusResponse, Post, Candidate, Cycle } from "@/lib/types";

const POLL_MS = 15_000;

export default function DashboardPage() {
  const agentId = typeof window !== "undefined" ? localStorage.getItem("narad-agent-id") : null;

  const [status, setStatus] = useState<AgentStatusResponse | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [cycles, setCycles] = useState<Cycle[]>([]);

  const fetchAll = useCallback(async () => {
    if (!agentId) return;
    try {
      const [s, f, c, cy] = await Promise.allSettled([
        getStatus(agentId),
        getFeed(agentId),
        getCandidates(agentId, false),
        getCycles(agentId),
      ]);
      if (s.status === "fulfilled") setStatus(s.value);
      if (f.status === "fulfilled") setPosts(f.value.posts);
      if (c.status === "fulfilled") setCandidates(c.value.candidates);
      if (cy.status === "fulfilled") setCycles(cy.value.cycles);
    } catch {
      // silent
    }
  }, [agentId]);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, POLL_MS);
    return () => clearInterval(interval);
  }, [fetchAll]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">
            What is Narad doing right now?
          </p>
        </div>

        <motion.div
          className="grid gap-5"
          initial="hidden"
          variants={staggerContainer}
          viewport={{ once: true }}
          whileInView="visible"
        >
          {/* Row 1: Latest Publication + AI Brain */}
          <div className="grid gap-5 md:grid-cols-3">
            <motion.div className="md:col-span-2" variants={staggerContainer}>
              <BentoCard>
                <LatestPublication posts={posts} />
              </BentoCard>
            </motion.div>
            <motion.div className="md:col-span-1" variants={staggerContainer}>
              <BentoCard>
                <AIBrain status={status} />
              </BentoCard>
            </motion.div>
          </div>

          {/* Row 2: Console + Summary */}
          <div className="grid gap-5 md:grid-cols-3">
            <motion.div className="md:col-span-2" variants={staggerContainer}>
              <BentoCard>
                <LiveAgentConsole status={status} candidates={candidates} posts={posts} />
              </BentoCard>
            </motion.div>
            <motion.div className="md:col-span-1" variants={staggerContainer}>
              <BentoCard>
                <DashboardSummary status={status} candidates={candidates} />
              </BentoCard>
            </motion.div>
          </div>

          {/* Row 3: Timeline + Funnel */}
          <div className="grid gap-5 md:grid-cols-2">
            <motion.div variants={staggerContainer}>
              <BentoCard>
                <AgentTimeline cycles={cycles} />
              </BentoCard>
            </motion.div>
            <motion.div variants={staggerContainer}>
              <BentoCard>
                <DecisionTree candidates={candidates} />
              </BentoCard>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </AppShell>
  );
}
