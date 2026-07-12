"use client";

import { useState, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";

interface FlipWordsProps {
  words: string[];
  duration?: number;
  className?: string;
}

export function FlipWords({ words, duration = 2500, className }: FlipWordsProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const startAnimation = useCallback(() => {
    const nextIndex = (currentIndex + 1) % words.length;
    setCurrentIndex(nextIndex);
    setIsAnimating(true);
  }, [currentIndex, words.length]);

  useEffect(() => {
    if (!isAnimating) {
      const timer = setTimeout(() => {
        startAnimation();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [isAnimating, duration, startAnimation]);

  return (
    <AnimatePresence
      mode="wait"
      onExitComplete={() => {
        setIsAnimating(false);
      }}
    >
      <motion.span
        key={words[currentIndex]}
        initial={{ opacity: 0, y: 8, filter: "blur(4px)" }}
        animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        exit={{ opacity: 0, y: -8, filter: "blur(4px)" }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className={cn(
          "inline-block",
          className
        )}
      >
        {words[currentIndex]}
      </motion.span>
    </AnimatePresence>
  );
}
