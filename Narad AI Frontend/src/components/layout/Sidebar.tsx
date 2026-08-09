"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Rss, Brain, Database, Globe, Circle } from "lucide-react";
import { cn } from "@/lib/utils";
import { SystemStatus } from "./SystemStatus";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/feed", label: "Feed", icon: Rss },
  { href: "/intelligence", label: "Intelligence", icon: Brain },
  { href: "/memory", label: "Memory", icon: Database },
  { href: "/sources", label: "Sources", icon: Globe },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-[#0A0E1A] border-r border-slate-800/50 h-screen">
      {/* Logo / Avatar */}
      <div className="p-6 flex flex-col items-center gap-3">
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-violet-500 to-violet-700 flex items-center justify-center logo-glow overflow-hidden">
          <img src="/Logo.png" alt="Narad AI" className="w-full h-full object-cover" />
        </div>
        <div className="text-center">
          <h1 className="text-lg font-bold text-white tracking-tight">NARAD AI</h1>
          <p className="text-xs text-slate-400">Autonomous Creator</p>
          <p className="text-xs text-slate-500/80 italic mt-2">Developed by Nadaan Parindey</p>
        </div>
      </div>

      <div className="px-3">
        <div className="h-px bg-slate-800" />
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-violet-500/10 text-violet-400 border border-violet-500/20"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  )}
                >
                  <Icon className={cn("w-4 h-4", isActive && "text-violet-400")} />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* System Status */}
      <div className="px-3 pb-4">
        <div className="h-px bg-slate-800 mb-4" />
        <SystemStatus />
      </div>
    </aside>
  );
}
