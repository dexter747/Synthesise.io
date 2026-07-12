"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { motion, useInView } from "framer-motion";
import { Check, Sparkles, Zap, Loader2, Crown, Rocket, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useSubscriptionPlans } from "@/hooks/use-api";

export function PricingSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const { data: apiPlans, isLoading } = useSubscriptionPlans();

  const handleSelectPlan = (plan: any) => {
    setSelectedPlan(plan.id);
    
    // Handle enterprise separately
    if (plan.tier === 'enterprise') {
      window.location.href = 'mailto:sales@synthesize.io?subject=Enterprise%20Plan%20Inquiry';
      return;
    }
    
    // All paid plans go to checkout (no free tier)
    router.push(`/checkout?plan=${plan.id}`);
  };

  // Map API plans to display format with comprehensive features
  const displayPlans = apiPlans?.map((plan: any) => {
    let icon = Sparkles;
    let recommended = false;
    const tier = plan.tier || plan.slug;
    
    if (tier === 'pro' || tier === 'professional') {
      icon = Zap;
      recommended = true;
    } else if (tier === 'business') {
      icon = Rocket;
    } else if (tier === 'enterprise') {
      icon = Crown;
    }
    
    // Build comprehensive feature list matching the exact offerings
    const features: string[] = [];
    const negativeFeatures: string[] = [];
    
    // Tier-specific features (NO FREE TIER - Beginner is $19/month)
    // Matching exact quotas from QUOTA_AND_PRICING.md
    if (tier === 'beginner') {
      features.push('50,000 rows per month');
      features.push('5,000 rows per dataset');
      features.push('10 datasets');
      features.push('50 jobs per month');
      features.push('CSV & JSON export');
      features.push('7-day data retention');
      features.push('Basic data types');
      features.push('Email support');
      negativeFeatures.push('No team collaboration');
      negativeFeatures.push('No API access');
    } else if (tier === 'pro' || tier === 'professional') {
      features.push('1M rows per month');
      features.push('100K rows per dataset');
      features.push('100 datasets');
      features.push('500 jobs per month');
      features.push('All export formats');
      features.push('30-day data retention');
      features.push('API access (10K calls/month)');
      features.push('Priority support');
      features.push('Custom schemas');
      features.push('Advanced templates');
      features.push('3 concurrent jobs');
    } else if (tier === 'business') {
      features.push('10M rows per month');
      features.push('1M rows per dataset');
      features.push('Unlimited datasets');
      features.push('2,000 jobs per month');
      features.push('All export formats + SQL');
      features.push('90-day data retention');
      features.push('API access (100K calls/month)');
      features.push('Team collaboration (10 members)');
      features.push('Dedicated support');
      features.push('Advanced API features');
      features.push('10 concurrent jobs');
      features.push('SSO (coming soon)');
    } else if (tier === 'enterprise') {
      features.push('Unlimited rows');
      features.push('Unlimited datasets');
      features.push('Unlimited jobs');
      features.push('All formats + Avro');
      features.push('365-day retention');
      features.push('Unlimited API calls');
      features.push('Unlimited team members');
      features.push('White-glove support');
      features.push('Custom SLA');
      features.push('On-premise deployment');
      features.push('Advanced security');
      features.push('Dedicated account manager');
    }

    const priceMonthly = plan.price_monthly ?? (plan.monthly_price_cents ? plan.monthly_price_cents / 100 : 0);

    return {
      ...plan,
      icon,
      recommended,
      features,
      negativeFeatures,
      tier,
      color: 'from-teal-400 to-emerald-500',
      price: tier === 'enterprise' ? 'Custom' : `$${priceMonthly}`,
      period: tier === 'enterprise' ? 'contact sales' : 'per month',
      description: plan.description || plan.name,
      cta: tier === 'enterprise' ? 'Contact Sales' : `Get ${plan.name}`,
    };
  }) || [];

  return (
    <section id="pricing" ref={ref} className="py-12 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-teal-500/5 rounded-full blur-[150px]" />
      </div>

      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-sm font-medium mb-4">
            Pricing
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-medium text-white mb-4">
            Simple,{" "}
            <span className="gradient-teal-text">Transparent</span>{" "}
            Pricing
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto mb-8">
            Save 95% compared to enterprise competitors. No hidden fees, no surprises.
          </p>
        </motion.div>

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
          </div>
        ) : (
          <>
            {/* Pricing Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
              {displayPlans.map((plan, index) => {
                const Icon = plan.icon;
                return (
                  <motion.div
                    key={plan.id}
                    initial={{ opacity: 0, y: 30 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="relative"
                  >
                    {plan.recommended && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                        <Badge className="bg-gradient-to-r from-teal-400 to-emerald-500 text-white border-0 font-medium px-4 py-1">
                          Most Popular
                        </Badge>
                      </div>
                    )}
                    <Card className={cn(
                      "h-full p-6 bg-zinc-900/50 border rounded-2xl transition-all duration-300 flex flex-col",
                      plan.recommended 
                        ? "border-teal-500/50" 
                        : "border-white/10 hover:border-white/20"
                    )}>
                      {/* Plan Header */}
                      <div className="flex items-center gap-3 mb-4">
                        <div className={cn(
                          'p-2 rounded-lg bg-gradient-to-br',
                          plan.color
                        )}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-xl font-medium text-white">
                          {plan.name}
                        </h3>
                      </div>
                      
                      <p className="text-sm text-zinc-400 mb-4">
                        {plan.description}
                      </p>

                      {/* Price */}
                      <div className="mb-6">
                        <div className="flex items-baseline gap-1">
                          <span className="text-4xl font-medium text-white">
                            {plan.price}
                          </span>
                          <span className="text-zinc-500">/{plan.period}</span>
                        </div>
                      </div>

                      {/* CTA */}
                      <Button
                        onClick={() => handleSelectPlan(plan)}
                        disabled={selectedPlan === plan.id}
                        variant={plan.recommended ? "gradient" : "outline"}
                        size="lg"
                        className="w-full mb-6"
                      >
                        {selectedPlan === plan.id ? 'Loading...' : plan.cta}
                      </Button>

                      {/* Features */}
                      <ul className="space-y-3 flex-1">
                        {plan.features.map((feature: string, featureIndex: number) => (
                          <li key={featureIndex} className="flex items-start gap-3">
                            <Check className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-zinc-300 leading-relaxed">{feature}</span>
                          </li>
                        ))}
                        {plan.negativeFeatures?.map((feature: string, featureIndex: number) => (
                          <li key={`neg-${featureIndex}`} className="flex items-start gap-3">
                            <X className="w-5 h-5 text-zinc-600 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-zinc-500 leading-relaxed">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            {/* Comparison Note */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-12 text-center"
            >
              <div className="inline-flex flex-col sm:flex-row items-center gap-4 px-6 py-4 rounded-2xl bg-zinc-900/50 border border-white/5">
                <div className="text-left">
                  <p className="text-sm text-zinc-400">
                    Competitors charge <span className="text-white font-medium">$2,000-$20,000/month</span> for similar features
                  </p>
                </div>
                <div className="h-8 w-px bg-white/10 hidden sm:block" />
                <div className="text-left">
                  <p className="text-sm text-teal-400 font-medium">
                    You save up to 95%
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Payment Provider */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="mt-8 flex items-center justify-center gap-2"
            >
              <span className="text-xs text-white">Secure payments by</span>
              <Image
                src="/dodo.svg"
                alt="Dodo Payments"
                width={160}
                height={48}
          
              />
            </motion.div>
          </>
        )}
      </div>
    </section>
  );
}
