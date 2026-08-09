"use client";

import { motion } from "framer-motion";
import type { NewsSource } from "@/lib/types";

function deriveDomain(url: string): string {
  try {
    return new URL(url).hostname.replace("www.", "");
  } catch {
    return url;
  }
}

interface Props {
  sources: NewsSource[];
}

export function ActiveSources({ sources }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="h-full flex flex-col"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Active Sources
      </h3>

      <div className="flex-1 space-y-4">
        {sources.length === 0 && (
          <p className="text-sm text-slate-500">No sources configured</p>
        )}
        {sources.map((source) => {
          const domain = deriveDomain(source.url);
          const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;

          return (
            <div key={source.name} className="space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <img
                    src={faviconUrl}
                    alt={source.name}
                    className="w-5 h-5 rounded-sm"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
                  />
                  <span className="text-sm font-semibold text-slate-200">{source.name}</span>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-4 text-xs">
                <span className="text-slate-500 truncate max-w-xs">{domain}</span>
              </div>

              <div className="border-b border-slate-800/50" />
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
