"use client";

import { useRef, useState, type RefObject } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ParticleButtonProps extends Omit<React.ComponentProps<typeof Button>, "onClick"> {
  onSuccess?: () => void;
  successDuration?: number;
  onClick?: () => void;
}

function SuccessParticles({
  buttonRef,
}: {
  buttonRef: RefObject<HTMLButtonElement>;
}) {
  const rect = buttonRef.current?.getBoundingClientRect();
  if (!rect) return null;

  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;

  return (
    <AnimatePresence>
      {[...Array(6)].map((_, i) => (
        <motion.div
          animate={{
            scale: [0, 1, 0],
            x: [0, (i % 2 ? 1 : -1) * (Math.random() * 50 + 20)],
            y: [0, -Math.random() * 50 - 20],
          }}
          className="fixed h-1 w-1 rounded-full bg-violet-400"
          initial={{ scale: 0, x: 0, y: 0 }}
          key={i}
          style={{ left: centerX, top: centerY }}
          transition={{ duration: 0.6, delay: i * 0.1, ease: "easeOut" }}
        />
      ))}
    </AnimatePresence>
  );
}

export function ParticleButton({
  children,
  onClick,
  onSuccess,
  successDuration = 1000,
  className,
  ...props
}: ParticleButtonProps) {
  const [showParticles, setShowParticles] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleClick = () => {
    setShowParticles(true);
    onClick?.();

    setTimeout(() => {
      setShowParticles(false);
      onSuccess?.();
    }, successDuration);
  };

  return (
    <>
      {showParticles && (
        <SuccessParticles buttonRef={buttonRef as RefObject<HTMLButtonElement>} />
      )}
      <Button
        className={cn(
          "relative",
          showParticles && "scale-95",
          "transition-transform duration-100",
          className
        )}
        onClick={handleClick}
        ref={buttonRef}
        {...props}
      >
        {children}
        <ArrowRight className="h-4 w-4 ml-1" />
      </Button>
    </>
  );
}
