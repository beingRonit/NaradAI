"use client";

import { useState, useMemo, useEffect, useCallback, Suspense } from "react";
import { motion } from "framer-motion";
import { useSearchParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { BentoCard, staggerContainer } from "@/components/ui/BentoCard";
import { FeedFilters } from "@/components/feed/FeedFilters";
import { FeedCard } from "@/components/feed/FeedCard";
import { getFeed } from "@/lib/api";
import type { Post } from "@/lib/types";
import { Search, Loader2 } from "lucide-react";

const POLL_INTERVAL_MS = 30_000;

function FeedContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const highlightId = searchParams.get("highlight");

  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightedId, setHighlightedId] = useState<string | null>(null);

  const agentId = typeof window !== "undefined" ? localStorage.getItem("narad-agent-id") : null;

  const fetchFeed = useCallback(async () => {
    try {
      const res = await getFeed(agentId || undefined);
      setPosts(res.posts);
      setError(null);
    } catch {
      setError("Unable to load feed. Narad may still be starting up.");
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    fetchFeed();
    const interval = setInterval(fetchFeed, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchFeed]);

  const filteredPosts = useMemo(() => {
    let result = [...posts];

    const now = new Date();
    if (activeFilter === "Today") {
      result = result.filter((p) => {
        const postDate = new Date(p.createdAt);
        return postDate.toDateString() === now.toDateString();
      });
    } else if (activeFilter === "Yesterday") {
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      result = result.filter((p) => {
        const postDate = new Date(p.createdAt);
        return postDate.toDateString() === yesterday.toDateString();
      });
    } else if (activeFilter === "This Week") {
      const weekAgo = new Date(now);
      weekAgo.setDate(weekAgo.getDate() - 7);
      result = result.filter((p) => new Date(p.createdAt) >= weekAgo);
    } else if (activeFilter === "This Month") {
      const monthAgo = new Date(now);
      monthAgo.setMonth(monthAgo.getMonth() - 1);
      result = result.filter((p) => new Date(p.createdAt) >= monthAgo);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (p) =>
          (p.title || "").toLowerCase().includes(query) ||
          p.text.toLowerCase().includes(query) ||
          (p.tags || []).some((t) => t.toLowerCase().includes(query))
      );
    }

    result.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

    return result;
  }, [posts, activeFilter, searchQuery]);

  const scrollToPost = useCallback((postId: string) => {
    const timer = setTimeout(() => {
      const element = document.getElementById(postId);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
        setHighlightedId(postId);
        const clearTimer = setTimeout(() => setHighlightedId(null), 600);
        return () => clearTimeout(clearTimer);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!highlightId) return;

    setActiveFilter("All");
    setSearchQuery("");

    const cleanup = scrollToPost(highlightId);

    const cleanUrl = setTimeout(() => {
      router.replace("/feed");
    }, 100);

    return () => {
      cleanup();
      clearTimeout(cleanUrl);
    };
  }, [highlightId, scrollToPost, router]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Feed</h1>
        <p className="text-slate-400 text-sm mt-1">
          All publications by Narad AI
        </p>
      </div>

      <motion.div
        className="grid gap-5"
        initial="hidden"
        variants={staggerContainer}
        viewport={{ once: true }}
        whileInView="visible"
      >
        <motion.div variants={staggerContainer}>
          <BentoCard>
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <FeedFilters active={activeFilter} onChange={setActiveFilter} />
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search posts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-8 pl-9 pr-3 bg-[#080B12] border border-slate-700/50 rounded-lg text-white text-sm outline-none focus:border-violet-500/50 focus:ring-2 focus:ring-violet-500/20"
                />
              </div>
            </div>
          </BentoCard>
        </motion.div>

        <motion.div variants={staggerContainer}>
          <BentoCard>
            {loading ? (
              <div className="py-12 text-center">
                <Loader2 className="w-6 h-6 text-violet-400 animate-spin mx-auto mb-3" />
                <p className="text-sm text-slate-500">Loading feed...</p>
              </div>
            ) : error ? (
              <div className="py-12 text-center">
                <p className="text-sm text-red-400 mb-2">{error}</p>
                <button
                  onClick={() => { setLoading(true); fetchFeed(); }}
                  className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
                >
                  Retry
                </button>
              </div>
            ) : filteredPosts.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-lg font-semibold text-slate-400 mb-2">
                  NARAD IS OBSERVING
                </p>
                <p className="text-sm text-slate-500">
                  No publications match your search. Narad is scanning live AI & technology
                  sources for something worth saying.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredPosts.map((post, i) => (
                  <FeedCard
                    key={post.id}
                    post={post}
                    index={i}
                    isHighlighted={highlightedId === post.id}
                  />
                ))}
              </div>
            )}
          </BentoCard>
        </motion.div>
      </motion.div>
    </div>
  );
}

export default function FeedPage() {
  return (
    <AppShell>
      <Suspense fallback={null}>
        <FeedContent />
      </Suspense>
    </AppShell>
  );
}
