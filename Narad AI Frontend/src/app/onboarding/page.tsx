"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { initializeAgent } from "@/lib/api";
import type { OnboardingData } from "@/lib/types";

export default function OnboardingPage() {
  const router = useRouter();
  const [initializing, setInitializing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleComplete = async (data: OnboardingData) => {
    setInitializing(true);
    setError(null);

    try {
      const { agentId } = await initializeAgent(data);
      localStorage.setItem("narad-agent-id", agentId);
      localStorage.setItem("narad-onboarding-complete", "true");
      router.push("/dashboard");
    } catch {
      setInitializing(false);
      setError("Failed to initialize Narad. Please try again.");
    }
  };

  return (
    <OnboardingWizard
      onComplete={handleComplete}
      initializing={initializing}
      error={error}
    />
  );
}
