"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/AppShell";
import { BentoCard, staggerContainer } from "@/components/ui/BentoCard";
import { SourceStats } from "@/components/sources/SourceStats";
import { ActiveSources } from "@/components/sources/ActiveSources";
import { SourceEvents } from "@/components/sources/SourceEvents";
import { getNewsSources, getNewsLatest } from "@/lib/api";
import type { NewsSource, NewsTopic } from "@/lib/types";

const POLL_MS = 60_000;

export default function SourcesPage() {
  const [sources, setSources] = useState<NewsSource[]>([]);
  const [latestTopics, setLatestTopics] = useState<NewsTopic[]>([]);

  const fetchData = useCallback(async () => {
    try {
      const [sRes, tRes] = await Promise.allSettled([
        getNewsSources(),
        getNewsLatest(20),
      ]);
      if (sRes.status === "fulfilled") setSources(sRes.value.sources);
      if (tRes.status === "fulfilled") setLatestTopics(tRes.value.topics);
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, POLL_MS);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Sources</h1>
          <p className="text-slate-400 text-sm mt-1">
            Where Narad gets live information
          </p>
        </div>

        <SourceStats sources={sources} />

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
                <ActiveSources sources={sources} />
              </BentoCard>
            </motion.div>
            <motion.div variants={staggerContainer}>
              <BentoCard>
                <SourceEvents topics={latestTopics} />
              </BentoCard>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </AppShell>
  );
}
