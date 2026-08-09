"use client";

import { motion, useMotionValue, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

interface BentoCardProps {
  children: React.ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" as const },
  },
};

export function BentoCard({ children, className, size = "md" }: BentoCardProps) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-100, 100], [2, -2]);
  const rotateY = useTransform(x, [-100, 100], [-2, 2]);

  function handleMouseMove(event: React.MouseEvent<HTMLDivElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct * 100);
    y.set(yPct * 100);
  }

  function handleMouseLeave() {
    x.set(0);
    y.set(0);
  }

  return (
    <motion.div
      className="h-full"
      onHoverEnd={handleMouseLeave}
      onMouseMove={handleMouseMove}
      style={{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      variants={fadeInUp}
      whileHover={{ y: -3 }}
    >
      <div
        className={cn(
          "group relative flex h-full flex-col rounded-xl border border-violet-500/10 bg-gradient-to-b from-[#0b101f]/80 via-[#0b101f]/60 to-[#0b101f]/40 p-5 shadow-[0_4px_20px_rgb(0,0,0,0.2)] backdrop-blur-[4px] transition-all duration-500 ease-out",
          "hover:border-violet-500/20 hover:shadow-[0_8px_30px_rgb(139,92,246,0.08)]",
          className
        )}
      >
        <div
          className="relative z-10 flex h-full flex-col"
          style={{ transform: "translateZ(20px)" }}
        >
          {children}
        </div>
      </div>
    </motion.div>
  );
}

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};
