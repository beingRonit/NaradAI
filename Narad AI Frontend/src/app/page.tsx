"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const onboardingComplete = localStorage.getItem("narad-onboarding-complete");
    if (onboardingComplete) {
      router.replace("/dashboard");
    } else {
      router.replace("/onboarding");
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0B0F19]">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Loading Narad AI...</p>
      </div>
    </div>
  );
}
