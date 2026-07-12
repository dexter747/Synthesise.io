"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRight, ArrowLeft, LucideIcon } from "lucide-react";

interface FeatureHeroProps {
  title: string;
  subtitle: string;
  description: string;
  icon: LucideIcon;
  features: string[];
  ctaText?: string;
  ctaLink?: string;
  gradient?: string;
}

export function FeatureHero({
  title,
  subtitle,
  description,
  icon: Icon,
  features,
  ctaText = "Get Started",
  ctaLink = "/auth/login",
  gradient = "from-teal-500 to-emerald-500",
}: FeatureHeroProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [textAnimationState, setTextAnimationState] = useState("initial");

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 300);

    const textTimer = setTimeout(() => {
      setTextAnimationState("popup");
      setTimeout(() => {
        setTextAnimationState("settled");
      }, 800);
    }, 600);

    return () => {
      clearTimeout(timer);
      clearTimeout(textTimer);
    };
  }, []);

  return (
    <section className="relative py-24 px-6 min-h-screen bg-black overflow-hidden">
      {/* Keyframes for animations */}
      <style>{`
        @keyframes beamPulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
        @keyframes beamMove {
          0% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-10px) scale(1.02); }
          100% { transform: translateY(0) scale(1); }
        }
        @keyframes triangleGlow {
          0%, 100% { 
            filter: drop-shadow(0 0 20px rgba(20, 184, 166, 0.3));
          }
          50% { 
            filter: drop-shadow(0 0 40px rgba(20, 184, 166, 0.6));
          }
        }
        @keyframes aurora-pan {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes textPopUp {
          0% { 
            transform: translateY(60px) scale(0.8); 
            opacity: 0; 
          }
          60% { 
            transform: translateY(-8px) scale(1.05); 
            opacity: 0.9; 
          }
          100% { 
            transform: translateY(0) scale(1); 
            opacity: 1; 
          }
        }
        @keyframes subtitleSlideUp {
          0% { 
            transform: translateY(40px); 
            opacity: 0; 
          }
          100% { 
            transform: translateY(0); 
            opacity: 1; 
          }
        }
        @keyframes pillsFadeIn {
          0% { 
            transform: translateY(30px) scale(0.9); 
            opacity: 0; 
          }
          100% { 
            transform: translateY(0) scale(1); 
            opacity: 1; 
          }
        }
        @keyframes buttonSlideUp {
          0% { 
            transform: translateY(50px); 
            opacity: 0; 
          }
          100% { 
            transform: translateY(0); 
            opacity: 1; 
          }
        }
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes slideInFromLeft {
          0% { 
            transform: translateX(-100px) rotate(180deg);
            opacity: 0;
          }
          100% { 
            transform: translateX(0) rotate(180deg);
            opacity: 1;
          }
        }
        @keyframes slideInFromRight {
          0% { 
            transform: translateX(100px);
            opacity: 0;
          }
          100% { 
            transform: translateX(0);
            opacity: 0.95;
          }
        }
        @keyframes float-diag {
          0% { transform: translate(-20%, 20%) scale(1); opacity: 0; }
          20% { opacity: 0.35; }
          100% { transform: translate(140%, -120%) scale(1.6); opacity: 0; }
        }
        @keyframes ripple {
          0% { transform: translate(-50%, -50%) scale(0.2); opacity: 0.35; }
          80% { opacity: 0.15; }
          100% { transform: translate(-50%, -50%) scale(2.6); opacity: 0; }
        }
        @keyframes glassShine {
          0% { transform: translateX(-100%) rotate(45deg); }
          100% { transform: translateX(300%) rotate(45deg); }
        }
      `}</style>

      {/* Background grid overlay */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage:
            "linear-gradient(rgba(20, 184, 166, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(20, 184, 166, 0.03) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      {/* Aurora color veil - teal themed */}
      <div
        className="absolute inset-0 z-0 pointer-events-none opacity-30"
        style={{
          backgroundImage:
            "linear-gradient(115deg, rgba(20,184,166,0.15), rgba(16,185,129,0.10), rgba(6,182,212,0.12), rgba(45,212,191,0.10))",
          backgroundSize: "200% 200%",
          mixBlendMode: "screen",
          animation: "aurora-pan 16s ease-in-out infinite",
        }}
      />

      {/* Background gradient with teal accents */}
      <div className="absolute inset-0 z-0">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "radial-gradient(60% 50% at 20% 85%, rgba(20,184,166,0.08) 0%, rgba(0,0,0,0) 55%), " +
              "radial-gradient(55% 45% at 82% 18%, rgba(16,185,129,0.10) 0%, rgba(0,0,0,0) 50%), " +
              "radial-gradient(50% 40% at 50% 12%, rgba(6,182,212,0.08) 0%, rgba(0,0,0,0) 60%), " +
              "radial-gradient(45% 40% at 10% 20%, rgba(45,212,191,0.08) 0%, rgba(0,0,0,0) 55%), " +
              "linear-gradient(135deg, #0a0a0c 0%, #000000 80%)",
          }}
        />
      </div>

      {/* Triangle element - single centered upside-down with beam borders only */}
      <div
        className="absolute z-0"
        style={{
          width: "50rem",
          height: "50rem",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          animation: isVisible ? "triangleGlow 4s ease-in-out infinite" : "none",
          opacity: 0.6,
        }}
      >
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full"
          style={{
            animation: "beamMove 8s ease-in-out infinite",
          }}
        >
          {/* Upside-down triangle - only borders, no fill */}
          <polygon
            points="50,85 90,15 10,15"
            fill="none"
            stroke="url(#tealGradient)"
            strokeWidth="0.3"
            style={{ filter: "drop-shadow(0 0 15px rgba(20, 184, 166, 0.4))" }}
          />
          
          {/* Beam lines on each corner */}
          <line
            x1="50"
            y1="85"
            x2="50"
            y2="105"
            stroke="url(#beamGradient)"
            strokeWidth="0.4"
            style={{ animation: "beamPulse 3s ease-in-out infinite" }}
          />
          <line
            x1="90"
            y1="15"
            x2="105"
            y2="5"
            stroke="url(#beamGradient)"
            strokeWidth="0.4"
            style={{ animation: "beamPulse 3s ease-in-out infinite 1s" }}
          />
          <line
            x1="10"
            y1="15"
            x2="-5"
            y2="5"
            stroke="url(#beamGradient)"
            strokeWidth="0.4"
            style={{ animation: "beamPulse 3s ease-in-out infinite 2s" }}
          />
          <defs>
            <linearGradient id="tealGradient" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.7" />
              <stop offset="50%" stopColor="#10b981" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.3" />
            </linearGradient>
            <linearGradient id="beamGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="container mx-auto relative z-10">
        {/* Back to Home Link */}
        <div
          className={`mb-8 pt-16 transform transition-all duration-1000 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <Link
            href="/#features"
            className="inline-flex items-center gap-2 text-zinc-400 hover:text-teal-400 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Back to Home</span>
          </Link>
        </div>

        {/* Hero Content */}
        <div className="text-center pt-8">
          {/* Main Heading with Pop-up Animation */}
          <div
            className={`transform transition-all duration-1000 delay-200 ${
              isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            }`}
          >
            {/* Icon Badge */}
            <div
              className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30 mb-6"
              style={{
                animation: textAnimationState === "popup" ? "pillsFadeIn 0.6s ease-out both" : "none",
              }}
            >
              <Icon className="w-10 h-10 text-teal-400" />
            </div>

            {/* Subtitle badge */}
            <div
              className="mb-4"
              style={{
                animation: textAnimationState === "popup" ? "pillsFadeIn 0.6s ease-out 0.2s both" : "none",
              }}
            >
              <span className="inline-block px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-sm font-medium">
                {subtitle}
              </span>
            </div>

            <h1
              className={`relative z-10 text-4xl sm:text-5xl lg:text-6xl xl:text-7xl mb-4 leading-tight font-light tracking-tight text-white ${
                textAnimationState === "popup" ? "animate-pulse" : ""
              }`}
              style={{
                fontFamily: "Inter, sans-serif",
                animation:
                  textAnimationState === "popup"
                    ? "textPopUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards"
                    : "none",
              }}
            >
              <span
                className="bg-clip-text text-transparent relative"
                style={{
                  backgroundImage:
                    "linear-gradient(135deg, #14b8a6 0%, #E0E0E0 15%, #FFFFFF 30%, #C0C0C0 45%, #F5F5F5 60%, #A0A0A0 75%, #10b981 100%)",
                  backgroundSize: "300% 300%",
                  animation:
                    textAnimationState === "settled" ? "gradientShift 6s ease-in-out infinite" : "none",
                }}
              >
                {title}
              </span>
            </h1>

            {/* Description with slide-up animation */}
            <div
              className="mb-8"
              style={{
                animation: textAnimationState === "popup" ? "subtitleSlideUp 0.8s ease-out 0.3s both" : "none",
              }}
            >
              <p className="text-xl lg:text-2xl max-w-3xl mx-auto leading-relaxed font-light text-zinc-300">
                {description}
              </p>
            </div>

            {/* Feature Pills with staggered fade-in */}
            <div
              className="flex flex-wrap items-center justify-center gap-3 mb-10"
              style={{
                animation: textAnimationState === "popup" ? "pillsFadeIn 0.6s ease-out 0.6s both" : "none",
              }}
            >
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-2 rounded-full px-4 py-2 border border-teal-500/30 bg-teal-500/10"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                  <span className="text-sm font-light text-zinc-200">{feature}</span>
                </div>
              ))}
            </div>

            {/* CTA Buttons with slide-up animation */}
            <div
              className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-8"
              style={{
                animation: textAnimationState === "popup" ? "buttonSlideUp 0.7s ease-out 0.8s both" : "none",
              }}
            >
              <Link
                href={ctaLink}
                className="group relative flex items-center space-x-3 px-8 py-4 rounded transition-all duration-300 overflow-hidden font-light text-white hover:shadow-lg hover:shadow-teal-900/30 transform hover:scale-105 bg-gradient-to-r from-teal-500 to-emerald-500"
              >
                <span className="relative z-10">{ctaText}</span>
                <ArrowRight className="w-5 h-5 relative z-10 group-hover:translate-x-1 transition-transform duration-300" />
              </Link>

              <Link
                href="/pricing"
                className="group relative flex items-center space-x-3 px-8 py-4 rounded overflow-hidden font-light border border-zinc-600 text-zinc-200 transition-all duration-500 hover:border-teal-400/60 hover:shadow-lg hover:shadow-teal-900/20 transform hover:scale-105 backdrop-blur-sm bg-white/5"
              >
                <span className="relative z-10 transition-colors duration-300 group-hover:text-white">
                  View Pricing
                </span>
              </Link>
            </div>

            {/* Footer text */}
            <p
              className="text-sm font-light text-zinc-500"
              style={{
                animation: textAnimationState === "popup" ? "subtitleSlideUp 0.6s ease-out 1s both" : "none",
              }}
            >
              No credit card required • Free tier available • Cancel anytime
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
