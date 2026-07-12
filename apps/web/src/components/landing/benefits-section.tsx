"use client";

import { useRef, useEffect } from "react";
import { motion, useInView } from "framer-motion";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { 
  Zap, 
  Shield, 
  DollarSign, 
  Clock, 
  Database,
  FileJson,
} from "lucide-react";

// Register GSAP plugins
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const benefitCards = [
  {
    title: '95% Cost Savings',
    description: 'Cut synthetic data costs compared to enterprise competitors',
    label: 'Affordable',
    Icon: DollarSign,
    tags: ['Pay-as-you-go', 'No contracts', 'Free tier']
  },
  {
    title: 'Instant Generation',
    description: 'Generate millions of realistic records in seconds',
    label: 'Fast',
    Icon: Zap,
    tags: ['1M+ rows/min', 'Real-time API', 'Batch exports']
  },
  {
    title: 'Privacy Compliant',
    description: '100% synthetic data. GDPR, HIPAA, and CCPA compliant',
    label: 'Secure',
    Icon: Shield,
    tags: ['GDPR', 'HIPAA', 'CCPA', 'SOC2']
  },
  {
    title: '5-Minute Setup',
    description: 'Self-service platform with no enterprise contracts',
    label: 'Simple',
    Icon: Clock,
    tags: ['No-code UI', 'API ready', 'Templates']
  },
  {
    title: 'Relational Data',
    description: 'Complex datasets with foreign keys and referential integrity',
    label: 'Smart',
    Icon: Database,
    tags: ['Foreign keys', 'Referential integrity', 'Multi-table']
  },
  {
    title: 'Multiple Formats',
    description: 'Export in CSV, JSON, SQL, Parquet, or Excel',
    label: 'Flexible',
    Icon: FileJson,
    tags: ['CSV', 'JSON', 'SQL', 'Parquet', 'Excel']
  }
];

export function BenefitsSection() {
  const ref = useRef(null);
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);
  const headerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (typeof window === "undefined" || !sectionRef.current) return;

    const ctx = gsap.context(() => {
      // Animate section header
      gsap.from(headerRef.current, {
        scrollTrigger: {
          trigger: headerRef.current,
          start: "top 80%",
          end: "top 40%",
          toggleActions: "play none none reverse",
        },
        y: 60,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
      });

      // Animate badge
      const badgeElement = headerRef.current?.querySelector(".badge");
      if (badgeElement) {
        gsap.from(badgeElement, {
          scrollTrigger: {
            trigger: headerRef.current,
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
          scale: 0.8,
          opacity: 0,
          duration: 0.6,
          ease: "back.out(1.7)",
        });
      }

      // Animate cards with stagger
      cardsRef.current.forEach((card, index) => {
        if (!card) return;

        // Main card animation
        gsap.from(card, {
          scrollTrigger: {
            trigger: card,
            start: "top 85%",
            end: "top 50%",
            toggleActions: "play none none reverse",
          },
          y: 80,
          opacity: 0,
          scale: 0.9,
          duration: 0.8,
          delay: index * 0.1,
          ease: "power3.out",
        });

        // Icon animation
        const icon = card.querySelector(".card-icon");
        if (icon) {
          gsap.from(icon, {
            scrollTrigger: {
              trigger: card,
              start: "top 80%",
              toggleActions: "play none none reverse",
            },
            scale: 0,
            rotation: -180,
            duration: 0.8,
            delay: index * 0.1 + 0.2,
            ease: "back.out(2)",
          });
        }

        // Tags animation
        const tags = card.querySelectorAll(".card-tag");
        gsap.from(tags, {
          scrollTrigger: {
            trigger: card,
            start: "top 75%",
            toggleActions: "play none none reverse",
          },
          x: -20,
          opacity: 0,
          duration: 0.5,
          delay: index * 0.1 + 0.4,
          stagger: 0.05,
          ease: "power2.out",
        });

        // Subtle hover effect
        card.addEventListener("mouseenter", () => {
          gsap.to(card, {
            y: -8,
            duration: 0.4,
            ease: "power2.out",
          });
        });

        card.addEventListener("mouseleave", () => {
          gsap.to(card, {
            y: 0,
            duration: 0.4,
            ease: "power2.out",
          });
        });
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className="py-12 relative overflow-hidden">

      <div ref={ref} className="container mx-auto px-4">
        {/* Section Header */}
        <div
          ref={headerRef}
          className="text-center mb-16"
        >
          <span className="badge inline-block px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-sm font-medium mb-4">
            Why Synthesize.io
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-medium text-white mb-4">
            The Smarter Way to{" "}
            <span className="gradient-teal-text">Generate Data</span>
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
            Enterprise-grade synthetic data at a fraction of the cost. 
            Built for developers, QA teams, and data scientists.
          </p>
        </div>

        {/* Benefits Grid with Glowing Effect */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {benefitCards.map((card, index) => (
            <div
              key={index}
              ref={(el) => {
                cardsRef.current[index] = el;
              }}
              className="relative min-h-[16rem] rounded-2xl"
            >
              {/* Glowing Effect Wrapper */}
              <div className="relative h-full rounded-2xl">
                <GlowingEffect
                  spread={50}
                  glow={true}
                  disabled={false}
                  proximity={80}
                  inactiveZone={0.01}
                  movementDuration={2.5}
                />
                
                {/* Card Content */}
                <div className="relative h-full bg-black rounded-2xl border border-white/10 p-6 flex flex-col">
                  {/* Icon */}
                  <div className="mb-4">
                    <div className="card-icon w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30 flex items-center justify-center">
                      <card.Icon className="w-6 h-6 text-teal-400" />
                    </div>
                  </div>
                  
                  {/* Label */}
                  <span className="text-xs font-medium text-teal-400 mb-2">{card.label}</span>
                  
                  {/* Title */}
                  <h3 className="text-xl font-medium text-white mb-2">{card.title}</h3>
                  
                  {/* Description */}
                  <p className="text-sm text-zinc-400 mb-4 flex-grow">{card.description}</p>
                  
                  {/* Tags */}
                  <div className="flex flex-wrap gap-2">
                    {card.tags.map((tag, tagIndex) => (
                      <span 
                        key={tagIndex}
                        className="card-tag px-2.5 py-1 text-xs font-medium bg-white/5 hover:bg-teal-500/10 text-zinc-400 hover:text-teal-400 rounded-lg border border-white/5 hover:border-teal-500/20 transition-all duration-200 cursor-default"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
