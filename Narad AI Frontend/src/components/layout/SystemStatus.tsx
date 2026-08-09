"use client";

export function SystemStatus() {
  return (
    <div className="space-y-3">
      {/* Live Status */}
      <div className="flex items-center gap-2">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
        </span>
        <span className="text-xs font-semibold text-emerald-400 tracking-wide">
          NARAD IS LIVE
        </span>
      </div>

      {/* Status Details */}
      <div className="space-y-2 text-xs">
        <div className="flex justify-between">
          <span className="text-slate-500">Last scan</span>
          <span className="text-slate-300">42 sec ago</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Next scan</span>
          <span className="text-slate-300">08 min</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Uptime</span>
          <span className="text-slate-300 font-mono">04:32:18</span>
        </div>
      </div>
    </div>
  );
}
