"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  DollarSign,
  Zap,
  Shield,
  Clock,
  Database,
  FileJson,
  ArrowRight,
} from "lucide-react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const allFeatures = [
  {
    title: "95% Cost Savings",
    description: "Cut synthetic data costs compared to enterprise competitors",
    icon: DollarSign,
    href: "/features/cost-savings",
    color: "teal",
  },
  {
    title: "Instant Generation",
    description: "Generate millions of realistic records in seconds",
    icon: Zap,
    href: "/features/instant-generation",
    color: "emerald",
  },
  {
    title: "Privacy Compliant",
    description: "100% synthetic data. GDPR, HIPAA, and CCPA compliant",
    icon: Shield,
    href: "/features/privacy-compliance",
    color: "cyan",
  },
  {
    title: "5-Minute Setup",
    description: "Self-service platform with no enterprise contracts",
    icon: Clock,
    href: "/features/quick-setup",
    color: "teal",
  },
  {
    title: "Relational Data",
    description: "Complex datasets with foreign keys and referential integrity",
    icon: Database,
    href: "/features/relational-data",
    color: "emerald",
  },
  {
    title: "Multiple Formats",
    description: "Export in CSV, JSON, SQL, Parquet, or Excel",
    icon: FileJson,
    href: "/features/multiple-formats",
    color: "cyan",
  },
];

export default function FeaturesPage() {
  const [isVisible, setIsVisible] = useState(false);
  const cardsRef = useRef<(HTMLAnchorElement | null)[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const ctx = gsap.context(() => {
      cardsRef.current.forEach((card, index) => {
        if (!card) return;

        gsap.from(card, {
          scrollTrigger: {
            trigger: card,
            start: "top 85%",
            toggleActions: "play none none reverse",
          },
          y: 60,
          opacity: 0,
          scale: 0.95,
          duration: 0.6,
          delay: index * 0.1,
          ease: "power3.out",
        });
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <section className="relative min-h-screen bg-black overflow-hidden py-24 px-6">
      {/* Keyframes */}
      <style>{`
        @keyframes aurora-pan {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes triangleGlow {
          0%, 100% { filter: drop-shadow(0 0 20px rgba(20, 184, 166, 0.3)); }
          50% { filter: drop-shadow(0 0 40px rgba(20, 184, 166, 0.6)); }
        }
        @keyframes beamMove {
          0% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-10px) scale(1.02); }
          100% { transform: translateY(0) scale(1); }
        }
        @keyframes beamPulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
        @keyframes slideInFromLeft {
          0% { transform: translateX(-100px) rotate(180deg); opacity: 0; }
          100% { transform: translateX(0) rotate(180deg); opacity: 1; }
        }
        @keyframes slideInFromRight {
          0% { transform: translateX(100px); opacity: 0; }
          100% { transform: translateX(0); opacity: 0.95; }
        }
      `}</style>

      {/* Background */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage:
            "linear-gradient(rgba(20, 184, 166, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(20, 184, 166, 0.03) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <div
        className="absolute inset-0 z-0 pointer-events-none opacity-30"
        style={{
          backgroundImage:
            "linear-gradient(115deg, rgba(20,184,166,0.15), rgba(16,185,129,0.10), rgba(6,182,212,0.12), rgba(45,212,191,0.10))",
          backgroundSize: "200% 200%",
          animation: "aurora-pan 16s ease-in-out infinite",
        }}
      />

      {/* Triangle - single centered upside-down with beam borders only */}
      <div
        className="absolute z-0"
        style={{
          width: "50rem",
          height: "50rem",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          animation: isVisible ? "triangleGlow 4s ease-in-out infinite" : "none",
          opacity: 0.5,
        }}
      >
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full"
          style={{ animation: "beamMove 8s ease-in-out infinite" }}
        >
          {/* Upside-down triangle - only borders */}
          <polygon
            points="50,85 90,15 10,15"
            fill="none"
            stroke="url(#tealGrad1)"
            strokeWidth="0.3"
          />
          {/* Beam lines */}
          <line x1="50" y1="85" x2="50" y2="105" stroke="url(#beamGrad1)" strokeWidth="0.4" style={{ animation: "beamPulse 3s ease-in-out infinite" }} />
          <line x1="90" y1="15" x2="105" y2="5" stroke="url(#beamGrad1)" strokeWidth="0.4" style={{ animation: "beamPulse 3s ease-in-out infinite 1s" }} />
          <line x1="10" y1="15" x2="-5" y2="5" stroke="url(#beamGrad1)" strokeWidth="0.4" style={{ animation: "beamPulse 3s ease-in-out infinite 2s" }} />
          <defs>
            <linearGradient id="tealGrad1" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.7" />
              <stop offset="50%" stopColor="#10b981" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.3" />
            </linearGradient>
            <linearGradient id="beamGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="container mx-auto relative z-10 pt-16">
        {/* Header */}
        <div
          className={`text-center mb-16 transform transition-all duration-1000 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-sm font-medium mb-6">
            All Features
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-light text-white mb-4">
            Powerful Features for{" "}
            <span className="bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
              Modern Data
            </span>
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
            Everything you need to generate, manage, and export synthetic data at scale.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {allFeatures.map((feature, index) => (
            <Link
              key={index}
              href={feature.href}
              ref={(el) => {
                cardsRef.current[index] = el;
              }}
              className="group relative bg-zinc-900/50 border border-white/10 rounded-2xl p-6 hover:border-teal-500/30 transition-all duration-300 hover:bg-zinc-900/80"
            >
              <div className="mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-teal-400" />
                </div>
              </div>

              <h3 className="text-xl font-medium text-white mb-2 group-hover:text-teal-400 transition-colors">
                {feature.title}
              </h3>

              <p className="text-zinc-400 mb-4">{feature.description}</p>

              <div className="flex items-center gap-2 text-teal-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Learn more</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div
          className={`text-center mt-16 transform transition-all duration-1000 delay-500 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <Link
            href="/auth/login"
            className="inline-flex items-center gap-3 px-8 py-4 rounded bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-medium hover:shadow-lg hover:shadow-teal-500/20 transition-all hover:scale-105"
          >
            <span>Get Started Free</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}
