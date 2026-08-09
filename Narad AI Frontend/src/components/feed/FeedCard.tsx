"use client";

import { motion } from "framer-motion";
import { Clock, CheckCircle2 } from "lucide-react";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";

interface FeedCardProps {
  post: Post;
  index: number;
  isHighlighted?: boolean;
}

function deriveTitle(text: string): string {
  const firstLine = text.split("\n")[0]?.trim();
  if (firstLine && firstLine.length > 5 && firstLine.length < 200) return firstLine;
  return text.slice(0, 80).trim() + (text.length > 80 ? "..." : "");
}

function getSourceLabels(post: Post): string[] {
  if (Array.isArray(post.sources)) return post.sources;
  if (typeof post.sources === "string") return post.sources.split(" ").filter(Boolean);
  return [];
}

function deriveSourceLabel(source: string): string {
  if (source.startsWith("http")) {
    try {
      return new URL(source).hostname.replace("www.", "");
    } catch {
      return source;
    }
  }
  return source;
}

export function FeedCard({ post, index, isHighlighted }: FeedCardProps) {
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const time = date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
    const day = date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
    return `${day} · ${time}`;
  };

  const title = post.title || deriveTitle(post.text);
  const tags = post.tags || [];

  return (
    <motion.div
      id={post.id}
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.08 }}
      className={cn(
        "bg-slate-900/50 border rounded-xl p-5 transition-colors duration-200 scroll-mt-24",
        isHighlighted
          ? "border-violet-500 highlight-pulse"
          : "border-slate-800 hover:border-slate-700"
      )}
    >
      {/* Time & Score */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono text-slate-500 flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          {formatTime(post.createdAt)}
        </span>
        {post.score != null && (
          <span className="text-sm font-bold text-violet-400">
            {post.score} / 10
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-lg font-bold text-white mb-2 leading-snug">
        {title}
      </h3>

      {/* Excerpt */}
      <p className="text-sm text-slate-400 leading-relaxed mb-4 line-clamp-2">
        {post.text}
      </p>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 bg-violet-500/10 text-violet-400 text-xs font-medium rounded border border-violet-500/20"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Rationale */}
      <div className="bg-slate-800/30 rounded-lg p-3 mb-4">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Why Narad Chose This
        </p>
        <div className="space-y-1">
          {post.rationale.split(". ").slice(0, 4).map((reason, i) => (
            <div key={i} className="flex items-start gap-2">
              <CheckCircle2 className="w-3 h-3 text-emerald-400 mt-0.5 shrink-0" />
              <span className="text-xs text-slate-400">{reason}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Sources */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span>Sources:</span>
        {getSourceLabels(post).map((src, i) => {
          const label = deriveSourceLabel(src);
          const faviconUrl = `https://www.google.com/s2/favicons?domain=${label}&sz=32`;
          return (
            <span key={i} className="inline-flex items-center gap-1.5 text-slate-400">
              <img
                src={faviconUrl}
                alt={label}
                className="w-3.5 h-3.5 rounded-sm"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
              {label}
              {i < post.sources.length - 1 && ","}
            </span>
          );
        })}
      </div>
    </motion.div>
  );
}
