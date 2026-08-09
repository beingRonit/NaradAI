"use client";

import { motion } from "framer-motion";
import type { MemoryEntry } from "@/lib/types";

interface Props {
  entries: MemoryEntry[];
}

export function MemoryTable({ entries }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
    >
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        Recent Memory Entries
      </h3>

      <div className="overflow-x-auto">
        {entries.length === 0 ? (
          <p className="text-sm text-slate-500">No memory entries yet</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left py-2 text-xs font-medium text-slate-500">Topic</th>
                <th className="text-left py-2 text-xs font-medium text-slate-500">Companies</th>
                <th className="text-left py-2 text-xs font-medium text-slate-500">Technologies</th>
                <th className="text-left py-2 text-xs font-medium text-slate-500">Keywords</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => (
                <tr key={`${entry.topic}-${i}`} className="border-b border-slate-800/50 last:border-0">
                  <td className="py-2.5 text-slate-300 max-w-xs truncate">{entry.topic}</td>
                  <td className="py-2.5">
                    <div className="flex flex-wrap gap-1">
                      {(entry.companies ?? []).slice(0, 3).map((c, j) => (
                        <span key={j} className="px-1.5 py-0.5 bg-cyan-500/10 text-cyan-300 text-xs rounded">
                          {c}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2.5">
                    <div className="flex flex-wrap gap-1">
                      {(entry.technologies ?? []).slice(0, 3).map((t, j) => (
                        <span key={j} className="px-1.5 py-0.5 bg-amber-500/10 text-amber-300 text-xs rounded">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2.5 text-slate-500 text-xs">
                    {(entry.keywords ?? []).length} keywords
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </motion.div>
  );
}
