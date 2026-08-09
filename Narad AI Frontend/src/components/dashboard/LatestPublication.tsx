"use client";

import { useEffect, useState } from "react";
import { getFeed } from "@/lib/api";
import type { Post } from "@/lib/types";
import { Clock, CheckCircle2 } from "lucide-react";

function getSourceLabels(post: Post): string[] {
  if (Array.isArray(post.sources)) return post.sources;
  if (typeof post.sources === "string") return post.sources.split(" ").filter(Boolean);
  return [];
}

function deriveSourceLabel(src: string): string {
  if (src.startsWith("http")) {
    try { return new URL(src).hostname.replace("www.", ""); } catch { return src; }
  }
  return src;
}

export function LatestPublication({ posts: initialPosts }: { posts: Post[] }) {
  const [posts, setPosts] = useState(initialPosts);

  useEffect(() => { setPosts(initialPosts); }, [initialPosts]);

  const post = posts[0];

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const agentId = localStorage.getItem("narad-agent-id");
        if (agentId) {
          const res = await getFeed(agentId);
          setPosts(res.posts);
        }
      } catch { /* silent */ }
    }, 15_000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
  };

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins} min ago`;
    const hours = Math.floor(mins / 60);
    return `${hours}h ago`;
  };

  if (!post) {
    return (
      <div className="h-full">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Latest Publication</span>
        <p className="text-sm text-slate-500 mt-4">No publications yet. Narad is scanning sources...</p>
      </div>
    );
  }

  return (
    <div className="h-full">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Latest Publication</span>
      </div>

      <h2 className="text-xl font-bold text-white mb-3 leading-tight">
        {post.title || post.text.split("\n")[0]?.slice(0, 80)}
      </h2>

      <div className="flex items-center gap-3 mb-4 text-sm text-slate-400">
        <span className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5" />
          {formatTime(post.createdAt)} · {timeAgo(post.createdAt)}
        </span>
        {post.score != null && (
          <span className="text-violet-400 font-semibold">{post.score} / 10</span>
        )}
      </div>

      {post.tags && post.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag) => (
            <span key={tag} className="px-2.5 py-1 bg-violet-500/10 text-violet-400 text-xs font-medium rounded-md border border-violet-500/20">
              {tag}
            </span>
          ))}
        </div>
      )}

      <p className="text-sm text-slate-300 leading-relaxed mb-5 line-clamp-3">{post.text}</p>

      <div className="border-t border-slate-800 pt-4">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Why Narad Chose This</p>
        <div className="space-y-1.5">
          {post.rationale.split(". ").slice(0, 3).map((reason, i) => (
            <div key={i} className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
              <span className="text-xs text-slate-400">{reason}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/50">
        <p className="text-xs text-slate-500">
          Sources:{" "}
          {getSourceLabels(post).map((src, i) => (
            <span key={i}>
              <span className="text-slate-400">{deriveSourceLabel(src)}</span>
              {i < getSourceLabels(post).length - 1 && ", "}
            </span>
          ))}
        </p>
      </div>
    </div>
  );
}
