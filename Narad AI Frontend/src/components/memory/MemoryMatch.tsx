"use client";

import { motion } from "framer-motion";
import { Tag, Building2, Cpu } from "lucide-react";
import type { MemoryEntry } from "@/lib/types";

interface Props {
  entries: MemoryEntry[];
}

export function MemoryMatch({ entries }: Props) {
  const latest = entries[entries.length - 1];

  if (!latest) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="h-full flex flex-col"
      >
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
          Latest Memory Entry
        </h3>
        <p className="text-sm text-slate-500">No memory entries yet</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="h-full flex flex-col"
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Latest Memory Entry
      </h3>

      <div className="flex-1 flex flex-col gap-3">
        <div className="bg-gradient-to-r from-violet-500/10 to-violet-500/5 border border-violet-500/20 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Tag className="w-3.5 h-3.5 text-violet-400" />
            <span className="text-[10px] font-semibold text-violet-400 uppercase tracking-wider">Topic</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed">{latest.topic}</p>
        </div>

        <div className="bg-slate-800/40 border border-slate-700/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Opinion</span>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed">{latest.opinion}</p>
        </div>

        {latest.companies && latest.companies.length > 0 && (
          <div className="bg-gradient-to-r from-cyan-500/10 to-cyan-500/5 border border-cyan-500/20 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[10px] font-semibold text-cyan-400 uppercase tracking-wider">Companies</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {latest.companies.map((c, i) => (
                <span key={i} className="px-2 py-0.5 bg-cyan-500/10 text-cyan-300 text-xs rounded-md border border-cyan-500/20">
                  {c}
                </span>
              ))}
            </div>
          </div>
        )}

        {latest.technologies && latest.technologies.length > 0 && (
          <div className="bg-gradient-to-r from-amber-500/10 to-amber-500/5 border border-amber-500/20 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider">Technologies</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {latest.technologies.map((t, i) => (
                <span key={i} className="px-2 py-0.5 bg-amber-500/10 text-amber-300 text-xs rounded-md border border-amber-500/20">
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
