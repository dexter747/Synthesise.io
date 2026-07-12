"use client";

import { FeatureHero } from "@/components/features/feature-hero";
import { FeatureDetail } from "@/components/features/feature-detail";
import { Zap, Rocket, Database, Activity, Clock, Server } from "lucide-react";

export default function InstantGenerationPage() {
  return (
    <>
      <FeatureHero
        title="Instant Generation"
        subtitle="Lightning Fast"
        description="Generate millions of realistic records in seconds. Our high-performance infrastructure delivers enterprise-grade speed at scale."
        icon={Zap}
        features={[
          "1M+ rows/min",
          "Real-time API",
          "Batch exports",
          "Parallel processing",
          "Auto-scaling",
          "99.9% uptime",
        ]}
        ctaText="Try Now"
        ctaLink="/auth/login"
      />
      <FeatureDetail
        title="Blazing Fast Data Generation"
        description="Time is money. Our optimized infrastructure generates synthetic data at incredible speeds without compromising on quality or realism."
        stats={[
          { value: "1M+", label: "Rows per Minute" },
          { value: "<3s", label: "API Response" },
          { value: "99.9%", label: "Uptime SLA" },
          { value: "Unlimited", label: "Concurrent Jobs" },
        ]}
        benefits={[
          {
            icon: Rocket,
            title: "High-Performance Infrastructure",
            description: "Built on modern cloud infrastructure with intelligent caching and parallel processing. Generate millions of records in seconds, not hours.",
          },
          {
            icon: Activity,
            title: "Real-time API",
            description: "Stream data directly to your applications with our real-time API. Perfect for CI/CD pipelines, automated testing, and on-demand data needs.",
          },
          {
            icon: Database,
            title: "Batch Processing",
            description: "Need massive datasets? Our batch processing handles billions of records with ease. Queue jobs and download when ready, no waiting required.",
          },
          {
            icon: Server,
            title: "Auto-scaling",
            description: "Infrastructure that grows with your needs. Automatic scaling ensures consistent performance whether you're generating 1,000 or 1 billion records.",
          },
          {
            icon: Zap,
            title: "Parallel Processing",
            description: "Generate multiple datasets simultaneously. Our parallel processing architecture maximizes throughput and minimizes wait times.",
          },
          {
            icon: Clock,
            title: "No Queue Times",
            description: "Forget about waiting in generation queues. Our infrastructure ensures your jobs start immediately, even during peak usage.",
          },
        ]}
      />
    </>
  );
}
