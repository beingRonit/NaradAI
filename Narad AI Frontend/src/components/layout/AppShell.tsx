"use client";

import dynamic from "next/dynamic";
import { Sidebar } from "./Sidebar";

const PixelBlast = dynamic(() => import("@/components/ui/PixelBlast"), {
  ssr: false,
});

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen bg-[#080B12] overflow-hidden relative">
      {/* PixelBlast Background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <PixelBlast
          variant="circle"
          pixelSize={3}
          color="#763ce4"
          patternScale={3.75}
          patternDensity={0.3}
          pixelSizeJitter={0.5}
          enableRipples={false}
          rippleSpeed={0.4}
          rippleThickness={0.12}
          rippleIntensityScale={1.5}
          liquid
          liquidStrength={0.12}
          liquidRadius={1.2}
          liquidWobbleSpeed={5}
          speed={0.65}
          edgeFade={0.2}
          transparent
        />
      </div>

      {/* Content */}
      <div className="relative z-10 flex w-full h-screen">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 lg:p-8 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
