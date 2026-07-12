"use client";

import { FeatureHero } from "@/components/features/feature-hero";
import { FeatureDetail } from "@/components/features/feature-detail";
import { DollarSign, TrendingDown, CreditCard, Target, Zap, Shield } from "lucide-react";

export default function CostSavingsPage() {
  return (
    <>
      <FeatureHero
        title="95% Cost Savings"
        subtitle="Affordable Pricing"
        description="Cut synthetic data costs compared to enterprise competitors. Pay only for what you use with transparent, developer-friendly pricing."
        icon={DollarSign}
        features={[
          "Pay-as-you-go",
          "No contracts",
          "Free tier included",
          "Volume discounts",
          "No hidden fees",
          "Cancel anytime",
        ]}
        ctaText="Start Free"
        ctaLink="/auth/login"
      />
      <FeatureDetail
        title="Revolutionary Pricing That Makes Sense"
        description="Traditional enterprise synthetic data solutions charge thousands per month with complex licensing. We've rebuilt pricing from the ground up to be simple, transparent, and affordable for teams of all sizes."
        stats={[
          { value: "95%", label: "Cost Savings" },
          { value: "$0", label: "Setup Fees" },
          { value: "Pay-as-you-go", label: "Billing Model" },
          { value: "No Lock-in", label: "Contracts" },
        ]}
        benefits={[
          {
            icon: TrendingDown,
            title: "Dramatically Lower Costs",
            description: "Save up to 95% compared to enterprise competitors like Tonic.ai or Mostly AI. Our efficient infrastructure and smart pricing mean you only pay for what you actually use.",
          },
          {
            icon: CreditCard,
            title: "Transparent Pricing",
            description: "No hidden fees, no surprise charges. See exactly what you'll pay before you generate data. All costs are clearly displayed in your dashboard.",
          },
          {
            icon: Target,
            title: "Free Tier Included",
            description: "Start generating synthetic data immediately with our generous free tier. Perfect for testing, development, and small projects without any commitment.",
          },
          {
            icon: Zap,
            title: "Volume Discounts",
            description: "The more you use, the less you pay per GB. Automatic volume discounts kick in as your usage grows, with custom enterprise pricing for large-scale deployments.",
          },
          {
            icon: Shield,
            title: "No Long-term Contracts",
            description: "Cancel anytime with no penalties. We earn your business every month with great service and fair pricing, not by locking you into multi-year contracts.",
          },
          {
            icon: DollarSign,
            title: "Predictable Budgeting",
            description: "Set spending limits and receive alerts. Our usage-based pricing is predictable and scalable, growing with your needs without breaking your budget.",
          },
        ]}
      />
    </>
  );
}
