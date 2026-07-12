"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Zap, Shield, Database, Clock, FileJson, TrendingUp, Lock, Globe, Star } from "lucide-react";
import { motion, useInView } from "framer-motion";

const floatingBadges = [
  { icon: Zap, title: "Instant Generation", description: "1M rows in seconds", color: "teal" },
  { icon: Shield, title: "GDPR Compliant", description: "100% synthetic data", color: "emerald" },
  { icon: Database, title: "Relational Data", description: "Foreign key support", color: "teal" },
  { icon: Clock, title: "5-Minute Setup", description: "No contracts needed", color: "emerald" },
  { icon: FileJson, title: "Multiple Formats", description: "CSV, JSON, SQL, Parquet", color: "teal" },
  { icon: TrendingUp, title: "AI-Powered", description: "Smart pattern detection", color: "emerald" },
  { icon: Lock, title: "Enterprise Security", description: "Bank-grade encryption", color: "teal" },
  { icon: Globe, title: "Global CDN", description: "Fast worldwide access", color: "emerald" },
];

const trustedUsers = [
  { name: "Sarah Chen", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=80&h=80&fit=crop" },
  { name: "Marcus Rodriguez", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop" },
  { name: "Emily Watson", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop" },
  { name: "James Park", image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&h=80&fit=crop" },
  { name: "Lisa Thompson", image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&h=80&fit=crop" },
];

export function HeroSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  const [isVisible, setIsVisible] = useState(false);
  const [textAnimationState, setTextAnimationState] = useState('initial');

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 300);

    const textTimer = setTimeout(() => {
      setTextAnimationState('popup');
      setTimeout(() => {
        setTextAnimationState('settled');
      }, 800);
    }, 600);
    
    return () => {
      clearTimeout(timer);
      clearTimeout(textTimer);
    };
  }, []);

  return (
    <section
      ref={ref}
      className="relative min-h-screen flex flex-col items-center justify-start overflow-hidden pt-40 pb-16"
    >
      {/* Background Image */}
      <div className="absolute inset-0 -z-20">
        <Image
          src="/herobgss.webp"
          alt="Hero Background"
          fill
          className="object-cover opacity-50"
          priority
          quality={100}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/80" />
      </div>

      {/* Circle element - top left with beam */}
      <div 
        className="absolute z-0 pointer-events-none" 
        style={{ 
          width: '60rem', 
          height: '60rem', 
          top: '-30%', 
          left: '-30%', 
          display: 'flex',
          justifyContent: 'center', 
          alignItems: 'center',
          opacity: 0,
          animation: isVisible ? 'slideInFromLeft 1.2s ease-out 0.5s forwards' : 'none'
        }}
      >
        {/* Outer ring with beam effect */}
        <div 
          className="absolute inset-0 rounded-full"
          style={{ 
            background: 'conic-gradient(from 0deg, transparent 0%, transparent 70%, rgba(20,184,166,0.6) 85%, rgba(16,185,129,0.8) 90%, transparent 100%)',
            animation: 'spin-slow 8s linear infinite'
          }}
        />
        <div 
          style={{ 
            width: 'calc(100% - 4px)', 
            height: 'calc(100% - 4px)', 
            borderRadius: '100%', 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            background: 'linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(10,10,12,0.98) 100%)',
            position: 'relative'
          }}
        >
          {/* Inner circle beam */}
          <div 
            className="absolute rounded-full"
            style={{ 
              width: '70%', 
              height: '70%',
              background: 'conic-gradient(from 180deg, transparent 0%, transparent 70%, rgba(16,185,129,0.5) 85%, rgba(20,184,166,0.7) 90%, transparent 100%)',
              animation: 'spin-slow 6s linear infinite reverse'
            }}
          />
          <div 
            style={{ 
              width: 'calc(70% - 3px)', 
              height: 'calc(70% - 3px)', 
              backgroundColor: '#000', 
              borderRadius: '100%',
              position: 'absolute'
            }}
          />
        </div>
      </div>
      
      {/* Circle element - bottom right with beam */}
      <div 
        className="absolute z-0 pointer-events-none" 
        style={{ 
          width: '60rem', 
          height: '60rem', 
          bottom: '-25%', 
          right: '-25%', 
          display: 'flex',
          justifyContent: 'center', 
          alignItems: 'center',
          opacity: 0,
          animation: isVisible ? 'slideInFromRight 1.2s ease-out 0.7s forwards' : 'none'
        }}
      >
        {/* Outer ring with beam effect */}
        <div 
          className="absolute inset-0 rounded-full"
          style={{ 
            background: 'conic-gradient(from 180deg, transparent 0%, transparent 70%, rgba(16,185,129,0.6) 85%, rgba(20,184,166,0.8) 90%, transparent 100%)',
            animation: 'spin-slow 8s linear infinite reverse'
          }}
        />
        <div 
          style={{ 
            width: 'calc(100% - 4px)', 
            height: 'calc(100% - 4px)', 
            borderRadius: '100%', 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            background: 'linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(10,10,12,0.98) 100%)',
            position: 'relative'
          }}
        >
          {/* Inner circle beam */}
          <div 
            className="absolute rounded-full"
            style={{ 
              width: '70%', 
              height: '70%',
              background: 'conic-gradient(from 0deg, transparent 0%, transparent 70%, rgba(20,184,166,0.5) 85%, rgba(16,185,129,0.7) 90%, transparent 100%)',
              animation: 'spin-slow 6s linear infinite'
            }}
          />
          <div 
            style={{ 
              width: 'calc(70% - 3px)', 
              height: 'calc(70% - 3px)', 
              backgroundColor: '#000', 
              borderRadius: '100%',
              position: 'absolute'
            }}
          />
        </div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-5xl mx-auto text-center mt-16">

          {/* Main Heading with Smooth Fade-in */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1.0, delay: 0.2, ease: "easeOut" }}
          >
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-medium tracking-tight mb-6">
              <span 
                className="block bg-clip-text text-transparent bg-gradient-to-r from-teal-400 via-white to-emerald-400"
              >
                Generate Realistic Synthetic Data
              </span>
              <span 
                className="block mt-2 bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-teal-400"
              >
                In Seconds
              </span>
            </h1>
          </motion.div>

          {/* Subheadline with animated text */}
          <motion.div 
            className="mb-10 space-y-2"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1.0, delay: 0.5, ease: "easeOut" }}
          >
            <p className="text-xl lg:text-2xl max-w-3xl mx-auto leading-relaxed font-light text-white italic">
              <span className="font-medium not-italic">Enterprise-grade</span> synthetic data generation powered by <span className="font-medium not-italic">AI</span>.
            </p>
            <p className="text-lg lg:text-xl max-w-3xl mx-auto leading-relaxed font-light text-zinc-400 italic">
              <span className="font-medium not-italic">No coding required.</span> <span className="font-medium not-italic">GDPR compliant.</span> Production-ready datasets in seconds.
            </p>
          </motion.div>

          {/* CTA Buttons with slide-up animation */}
          <div 
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8"
            style={{
              animation: textAnimationState === 'popup' ? 'buttonSlideUp 0.7s ease-out 0.8s both' : 'none'
            }}
          >
            <Link href="/auth/register">
              <Button size="xl" variant="gradient" className="group min-w-[200px]">
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button size="xl" variant="glass" className="group min-w-[200px]">
              <Play className="w-5 h-5 mr-2" />
              Watch Demo
            </Button>
          </div>

          {/* Trusted by Users Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 1.0 }}
            className="flex flex-col items-center gap-3 mb-8"
          >
            <div className="flex items-center gap-2">
              {/* User Avatars */}
              <div className="flex -space-x-3">
                {trustedUsers.map((user, index) => (
                  <div
                    key={index}
                    className="w-10 h-10 rounded-full border-2 border-black overflow-hidden"
                    title={user.name}
                  >
                    <Image
                      src={user.image}
                      alt={user.name}
                      width={40}
                      height={40}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
              
              {/* Stars */}
              <div className="flex gap-0.5 ml-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                ))}
              </div>
            </div>
            
            <p className="text-sm text-zinc-400">
              Trusted by <span className="text-white font-medium">500+ Monthly Users</span>
            </p>
          </motion.div>
        </div>
      </div>

      {/* Horizontal Parallax Floating Badges Section */}
      <div className="w-full relative overflow-hidden ">
        {/* Common Background Container */}
        <div className="absolute inset-0 bg-black" />
        
        <div className="relative space-y-6">
          {/* Row 1 - Left to Right */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="relative"
          >
            <div className="flex animate-marquee-left gap-6">
              {[...floatingBadges.slice(0, 4), ...floatingBadges.slice(0, 4)].map((badge, index) => (
                <div
                  key={index}
                  className="flex-shrink-0 flex items-center gap-3 px-4 py-3"
                >
                  <div className={`w-10 h-10 rounded-lg ${badge.color === 'teal' ? 'bg-teal-500/20' : 'bg-emerald-500/20'} flex items-center justify-center flex-shrink-0`}>
                    <badge.icon className={`w-5 h-5 ${badge.color === 'teal' ? 'text-teal-400' : 'text-emerald-400'}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white whitespace-nowrap">{badge.title}</p>
                    <p className="text-xs text-zinc-500 whitespace-nowrap">{badge.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Row 2 - Right to Left */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6, delay: 1.0 }}
            className="relative"
          >
            <div className="flex animate-marquee-right gap-6">
              {[...floatingBadges.slice(4, 8), ...floatingBadges.slice(4, 8)].map((badge, index) => (
                <div
                  key={index}
                  className="flex-shrink-0 flex items-center gap-3 px-4 py-3"
                >
                  <div className={`w-10 h-10 rounded-lg ${badge.color === 'teal' ? 'bg-teal-500/20' : 'bg-emerald-500/20'} flex items-center justify-center flex-shrink-0`}>
                    <badge.icon className={`w-5 h-5 ${badge.color === 'teal' ? 'text-teal-400' : 'text-emerald-400'}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white whitespace-nowrap">{badge.title}</p>
                    <p className="text-xs text-zinc-500 whitespace-nowrap">{badge.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Marquee Animation Styles */}
      <style jsx global>{`
        @keyframes marquee-left {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        
        @keyframes marquee-right {
          0% {
            transform: translateX(-50%);
          }
          100% {
            transform: translateX(0);
          }
        }
        
        .animate-marquee-left {
          animation: marquee-left 30s linear infinite;
        }
        
        .animate-marquee-right {
          animation: marquee-right 30s linear infinite;
        }
        
        .animate-marquee-left:hover,
        .animate-marquee-right:hover {
          animation-play-state: paused;
        }
      `}</style>
    </section>
  );
}
