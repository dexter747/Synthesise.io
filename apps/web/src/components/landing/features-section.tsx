"use client";

import { useRef, useState, useEffect } from "react";
import { useInView } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const features = [
  {
    id: "ai-generation",
    label: "AI-Powered",
    title: "Intelligent Data Generation",
    description: "Describe your data needs in natural language. Our LLM understands context, relationships, and creates samples that our factory replicates at scale.",
    items: [
      "Natural language data requests",
      "Automatic schema detection",
      "Smart pattern recognition",
      "Edge case generation"
    ]
  },
  {
    id: "data-types",
    label: "Data Types",
    title: "Comprehensive Data Types",
    description: "Generate any type of data from simple fields to complex relational datasets. Support for customers, transactions, events, and more.",
    items: [
      "Customer profiles & demographics",
      "Transaction and order logs",
      "User activity and events",
      "Relational multi-table datasets"
    ]
  },
  {
    id: "formats",
    label: "Formats",
    title: "Export in Any Format",
    description: "Download your generated data in the format that works best for your workflow. Direct database import ready.",
    items: [
      "CSV for spreadsheets",
      "JSON for APIs",
      "SQL insert statements",
      "Parquet for big data"
    ]
  },
  {
    id: "api",
    label: "API Access",
    title: "Powerful REST API",
    description: "Integrate synthetic data generation directly into your CI/CD pipelines, testing frameworks, or applications.",
    items: [
      "RESTful API endpoints",
      "API key authentication",
      "Webhook notifications",
      "Rate limiting & quotas"
    ]
  }
];

export function FeaturesSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [activeTab, setActiveTab] = useState("ai-generation");
  const contentRef = useRef<HTMLDivElement>(null);
  const tabsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const ctx = gsap.context(() => {
      // Animate header elements
      gsap.from(".feature-tag", {
        scrollTrigger: {
          trigger: ref.current,
          start: "top 80%",
          end: "top 50%",
          toggleActions: "play none none reverse"
        },
        opacity: 0,
        y: 30,
        duration: 0.6,
        ease: "power2.out"
      });

      gsap.from(".feature-title", {
        scrollTrigger: {
          trigger: ref.current,
          start: "top 80%",
          end: "top 50%",
          toggleActions: "play none none reverse"
        },
        opacity: 0,
        y: 30,
        duration: 0.6,
        delay: 0.2,
        ease: "power2.out"
      });

      gsap.from(".feature-subtitle", {
        scrollTrigger: {
          trigger: ref.current,
          start: "top 80%",
          end: "top 50%",
          toggleActions: "play none none reverse"
        },
        opacity: 0,
        y: 30,
        duration: 0.6,
        delay: 0.4,
        ease: "power2.out"
      });

      // Animate tabs
      gsap.from(tabsRef.current, {
        scrollTrigger: {
          trigger: ref.current,
          start: "top 70%",
          end: "top 40%",
          toggleActions: "play none none reverse"
        },
        opacity: 0,
        y: 30,
        duration: 0.6,
        delay: 0.6,
        ease: "power2.out"
      });
    }, ref);

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    if (!contentRef.current) return;

    const ctx = gsap.context(() => {
      gsap.from(".feature-content-item", {
        opacity: 0,
        y: 20,
        duration: 0.4,
        stagger: 0.1,
        ease: "power2.out"
      });
    }, contentRef);

    return () => ctx.revert();
  }, [activeTab]);

  const activeFeature = features.find(f => f.id === activeTab);

  return (
    <section id="features" ref={ref} className="py-12 relative overflow-hidden">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <span className="feature-tag inline-block px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-sm font-medium mb-4">
            Features
          </span>
          <h2 className="feature-title text-3xl sm:text-4xl lg:text-5xl font-medium text-white mb-4">
            Everything You Need for{" "}
            <span className="gradient-teal-text">Synthetic Data</span>
          </h2>
          <p className="feature-subtitle text-lg text-zinc-400 max-w-2xl mx-auto">
            A complete toolkit for generating, managing, and exporting 
            high-quality synthetic datasets.
          </p>
        </div>

        {/* Feature Tabs */}
        <div ref={tabsRef}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full max-w-2xl mx-auto grid grid-cols-2 md:grid-cols-4 bg-zinc-900/50 border border-teal-500/10 p-1 rounded-xl mb-12">
              {features.map((feature) => (
                <TabsTrigger
                  key={feature.id}
                  value={feature.id}
                  className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-teal-500/20 data-[state=active]:to-emerald-500/20 data-[state=active]:text-teal-400 data-[state=active]:border data-[state=active]:border-teal-500/30 rounded-lg text-zinc-400 hover:text-zinc-200 transition-all"
                >
                  {feature.label}
                </TabsTrigger>
              ))}
            </TabsList>

            {features.map((feature) => (
              <TabsContent key={feature.id} value={feature.id}>
                <div ref={contentRef} className="max-w-4xl mx-auto">
                  {/* Centered Content */}
                  <div className="text-center mb-12 feature-content-item">
                    <h3 className="text-3xl sm:text-4xl font-medium text-white mb-6">
                      {feature.title}
                    </h3>
                    <p className="text-lg text-zinc-400 mb-8 leading-relaxed max-w-3xl mx-auto">
                      {feature.description}
                    </p>
                  </div>
                  
                  {/* Centered Items Grid */}
                  <div className="grid sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
                    {feature.items.map((item, index) => (
                      <div
                        key={index}
                        className="feature-content-item flex items-center justify-center gap-3 p-4 rounded-lg bg-zinc-900/50 border border-teal-500/10 hover:border-teal-500/30 transition-all group"
                      >
                        <div className="w-2 h-2 rounded-full bg-teal-500 flex-shrink-0 group-hover:scale-125 transition-transform" />
                        <span className="text-zinc-300 text-center">{item}</span>
                      </div>
                    ))}
                  </div>

                  {/* Code Preview */}
                  <div className="feature-content-item mt-12 relative max-w-3xl mx-auto">
                    <div className="rounded-2xl overflow-hidden border border-teal-500/20 bg-zinc-900/50 shadow-2xl">
                      <div className="p-4 border-b border-teal-500/10">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-teal-500/60" />
                          <div className="w-3 h-3 rounded-full bg-emerald-500/60" />
                          <div className="w-3 h-3 rounded-full bg-cyan-500/60" />
                        </div>
                      </div>
                      <div className="p-6 font-mono text-sm">
                        <pre className="text-zinc-400">
                          <code>
                            <span className="text-teal-400">{"// Generate 10,000 customer records"}</span>
                            {"\n"}
                            <span className="text-cyan-400">const</span> dataset = <span className="text-emerald-400">await</span> synthesize.
                            <span className="text-teal-400">generate</span>({"{"}
                            {"\n"}  type: <span className="text-teal-300">&quot;customers&quot;</span>,
                            {"\n"}  count: <span className="text-cyan-400">10000</span>,
                            {"\n"}  format: <span className="text-teal-300">&quot;json&quot;</span>,
                            {"\n"}  schema: {"{"}
                            {"\n"}    name: <span className="text-teal-300">&quot;fullName&quot;</span>,
                            {"\n"}    email: <span className="text-teal-300">&quot;email&quot;</span>,
                            {"\n"}    phone: <span className="text-teal-300">&quot;phone&quot;</span>,
                            {"\n"}    address: <span className="text-teal-300">&quot;address&quot;</span>
                            {"\n"}  {"}"}
                            {"\n"}{"}"});
                          </code>
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>
    </section>
  );
}
