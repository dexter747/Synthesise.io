"use client";

import { FeatureHero } from "@/components/features/feature-hero";
import { FeatureDetail } from "@/components/features/feature-detail";
import { Clock, MousePointer, Code, FileText, Headphones, Sparkles } from "lucide-react";

export default function QuickSetupPage() {
  return (
    <>
      <FeatureHero
        title="5-Minute Setup"
        subtitle="Simple & Fast"
        description="Self-service platform with no enterprise contracts. Get started in minutes with our intuitive interface and ready-to-use templates."
        icon={Clock}
        features={[
          "No-code UI",
          "API ready",
          "Pre-built templates",
          "Quick onboarding",
          "Instant access",
          "24/7 support",
        ]}
        ctaText="Get Started"
        ctaLink="/auth/login"
      />
      <FeatureDetail
        title="Get Up and Running in Minutes"
        description="Skip the lengthy enterprise onboarding. Sign up, choose a template, and start generating synthetic data in under 5 minutes."
        stats={[
          { value: "<5 min", label: "Setup Time" },
          { value: "Zero", label: "Sales Calls" },
          { value: "50+", label: "Templates" },
          { value: "24/7", label: "Support" },
        ]}
        benefits={[
          {
            icon: MousePointer,
            title: "No-Code Interface",
            description: "Intuitive drag-and-drop UI for creating synthetic data schemas. No programming required - define your data structure visually and generate instantly.",
          },
          {
            icon: Code,
            title: "API-First Design",
            description: "Full REST API access from day one. Integrate synthetic data generation into your CI/CD pipeline, testing frameworks, or custom applications.",
          },
          {
            icon: FileText,
            title: "50+ Pre-built Templates",
            description: "Start with battle-tested templates for common use cases: e-commerce, healthcare, finance, SaaS, and more. Customize to fit your exact needs.",
          },
          {
            icon: Clock,
            title: "Instant Access",
            description: "No waiting for sales calls or approval processes. Sign up with your email and start generating data immediately with our free tier.",
          },
          {
            icon: Sparkles,
            title: "Smart Onboarding",
            description: "Interactive tutorials and contextual help guide you through your first data generation. Get productive in minutes, not days.",
          },
          {
            icon: Headphones,
            title: "24/7 Support",
            description: "Get help when you need it. Comprehensive documentation, video tutorials, and responsive support team available around the clock.",
          },
        ]}
      />
    </>
  );
}
