"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { MessageSquare, Sparkles, Download, CheckCircle } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: MessageSquare,
    title: "Describe Your Data",
    description: "Tell us what you need in plain English. 'Generate 10,000 customer records with names, emails, and purchase history.' Our AI understands context and relationships.",
    color: "teal"
  },
  {
    number: "02",
    icon: Sparkles,
    title: "AI Generates Samples",
    description: "Our LLM creates a small, realistic sample set. You review and refine. The system learns patterns, distributions, and edge cases from this sample.",
    color: "emerald"
  },
  {
    number: "03",
    icon: Download,
    title: "Scale & Export",
    description: "Our data factory replicates the patterns at scale—millions of unique records in seconds. Download in your preferred format: CSV, JSON, SQL, or Parquet.",
    color: "cyan"
  }
];

export function HowItWorksSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="how-it-works" ref={ref} className="py-12 relative overflow-hidden">

      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium mb-4">
            How It Works
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-medium text-white mb-4">
            Three Steps to{" "}
            <span className="gradient-teal-text">Perfect Data</span>
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
            From natural language request to millions of records in minutes.
            No coding required.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative max-w-5xl mx-auto">
          {/* Connection Line */}
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-teal-500/50 via-emerald-500/50 to-cyan-500/50 hidden lg:block -translate-y-1/2" />

          <div className="grid lg:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                className="relative"
              >
                <div className="relative z-10 bg-zinc-900/80 border border-white/10 rounded-2xl p-8 backdrop-blur-sm hover:border-white/20 transition-all duration-300 h-full">
                  {/* Step Number */}
                  <div className="absolute -top-4 -left-4 w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center text-white font-medium text-sm">
                    {step.number}
                  </div>

                  {/* Icon */}
                  <div className={`w-14 h-14 rounded-2xl bg-${step.color}-500/10 flex items-center justify-center mb-6`}>
                    <step.icon className={`w-7 h-7 text-${step.color}-400`} />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-medium text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-zinc-400 leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Arrow for desktop */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 z-20 transform -translate-y-1/2">
                    <div className="w-8 h-8 rounded-full bg-zinc-900 border border-white/10 flex items-center justify-center">
                      <svg className="w-4 h-4 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Bottom Feature Grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto"
        >
          {[
            "Unique identifiers guaranteed",
            "Referential integrity maintained",
            "Statistical realism ensured",
            "Format compliance validated"
          ].map((feature, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-4 py-3 rounded-xl bg-white/5 border border-white/5"
            >
              <CheckCircle className="w-4 h-4 text-teal-400 flex-shrink-0" />
              <span className="text-sm text-zinc-300">{feature}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
