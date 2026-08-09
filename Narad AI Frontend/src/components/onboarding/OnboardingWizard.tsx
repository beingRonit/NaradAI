"use client";

import { useState } from "react";
import { OnboardingSidebar } from "./OnboardingSidebar";
import { StepIndicator } from "./StepIndicator";
import { WelcomeStep } from "./steps/WelcomeStep";
import { PersonaSetupStep } from "./steps/PersonaSetupStep";
import { PreferencesStep } from "./steps/PreferencesStep";
import { AwakenStep } from "./steps/AwakenStep";
import type { OnboardingData } from "@/lib/types";

// ── Internal mode constant (not user-facing) ─────────────────────────────────
const onboardingMode = "exact_reference";

const STEPS = ["Welcome", "Persona Setup", "Preferences", "Awaken Narad"] as const;

interface OnboardingWizardProps {
  onComplete: (data: OnboardingData) => void;
  initializing: boolean;
  error: string | null;
}

export function OnboardingWizard({ onComplete, initializing, error }: OnboardingWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    name: "Narad",
    domain: "AI & Technology",
    bio: "An inquisitive AI sage that explores the future of technology and shares meaningful insights.",
    topics: ["AI Agents", "LLMs", "Machine Learning", "Future Tech"],
    frequency: "07:30 AM",
    tone: "Insightful & Thoughtful",
  });

  const updateData = (partial: Partial<OnboardingData>) => {
    setData((prev) => ({ ...prev, ...partial }));
  };

  const goNext = () => setCurrentStep((s) => Math.min(s + 1, STEPS.length - 1));
  const goBack = () => setCurrentStep((s) => Math.max(s - 1, 0));

  if (onboardingMode !== "exact_reference") return null;

  return (
    <div className="flex h-screen bg-[#0A0A0F] overflow-hidden font-[family-name:var(--font-jetbrains-mono)]">
      {/* Left Sidebar */}
      <OnboardingSidebar currentStep={currentStep} steps={STEPS} />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* Top-right step indicator */}
        <div className="flex justify-end p-6 lg:p-8">
          <StepIndicator current={currentStep} total={STEPS.length} />
        </div>

        {/* Step Content */}
        <div className="flex-1 flex items-center justify-center px-6 lg:px-10 pb-10">
          <div className="w-full max-w-3xl">
            {currentStep === 0 && <WelcomeStep onNext={goNext} />}
            {currentStep === 1 && (
              <PersonaSetupStep
                data={data}
                onUpdate={updateData}
                onBack={goBack}
                onNext={goNext}
              />
            )}
            {currentStep === 2 && (
              <PreferencesStep
                data={data}
                onUpdate={updateData}
                onBack={goBack}
                onNext={goNext}
              />
            )}
            {currentStep === 3 && (
              <AwakenStep
                data={data}
                onBack={goBack}
                onComplete={onComplete}
                initializing={initializing}
                error={error}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
