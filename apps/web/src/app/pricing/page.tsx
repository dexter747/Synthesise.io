'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, useInView } from 'framer-motion';
import { Check, Zap, Building2, Sparkles, Loader2, Star, Crown, Rocket } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import Image from 'next/image';
import { useSubscriptionPlans } from '@/hooks/use-api';
import { TestimonialsSection } from '@/components/landing/testimonials-section';
import { useAuth } from '@/providers/auth-provider';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.23, 1, 0.32, 1] as const } },
};

export default function PricingPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const { data: apiPlans, isLoading } = useSubscriptionPlans();

  // Don't redirect users with existing subscriptions - they may want to upgrade/change plans
  // The auth-provider already handles blocking dashboard access for invalid tiers

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

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
      </div>
    );
  }

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
    
    // Build comprehensive feature list matching exact quotas from QUOTA_AND_PRICING.md
    const features: string[] = [];
    
    // Tier-specific features (matching documentation exactly)
    if (tier === 'beginner') {
      features.push('50,000 rows per month');
      features.push('5,000 rows per dataset');
      features.push('10 datasets');
      features.push('50 jobs per month');
      features.push('CSV & JSON export');
      features.push('7-day data retention');
      features.push('Basic data types');
      features.push('Email support');
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

    const priceMonthly = plan.price_monthly ?? (plan.monthly_price_cents / 100);

    return {
      ...plan,
      icon,
      recommended,
      features,
      tier,
      color: 'from-teal-400 to-emerald-500',
      price: tier === 'enterprise' ? 'Custom' : `$${priceMonthly}`,
      period: tier === 'enterprise' ? 'contact sales' : 'per month',
      description: plan.description || plan.name,
    };
  }) || [];

  return (
    <div className="min-h-screen bg-black">
      {/* Development Mode Banner */}
      {(typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) && (
        <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-black py-3 px-4 text-center">
          <div className="max-w-4xl mx-auto flex items-center justify-center gap-4 flex-wrap">
            <span className="text-sm font-semibold">🧪 Development Mode</span>
            <span className="hidden sm:inline text-sm">|</span>
            <a 
              href="/test/activate-subscription" 
              className="text-sm font-medium underline hover:no-underline"
            >
              Quick Activate Any Plan →
            </a>
          </div>
        </div>
      )}
      
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl lg:text-6xl font-medium text-white mb-4">
            Choose Your
            <span className="bg-gradient-to-r from-teal-400 to-emerald-500 bg-clip-text text-transparent"> Plan</span>
          </h1>
          <p className="text-lg lg:text-xl text-zinc-400 max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include our core features.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto"
        >
          {displayPlans.map((plan) => {
            const Icon = plan.icon;
            return (
              <motion.div
                key={plan.id}
                variants={item}
                className="relative"
              >
                {plan.recommended && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                    <Badge className="bg-gradient-to-r from-teal-400 to-emerald-500 text-white border-0 font-medium px-4 py-1">
                      Most Popular
                    </Badge>
                  </div>
                )}
                <Card
                  className={cn(
                    'relative overflow-hidden bg-zinc-900/50 border-white/10 backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:shadow-2xl h-full flex flex-col',
                    plan.recommended && 'border-teal-500/30 hover:border-teal-500/50'
                  )}
                >
                  <div className="p-6 flex flex-col h-full">
                    {/* Header */}
                    <div className="flex items-center gap-3 mb-4">
                      <div className={cn(
                        'p-2 rounded-lg bg-gradient-to-br',
                        plan.color
                      )}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-medium text-white">{plan.name}</h3>
                      </div>
                    </div>

                    <p className="text-zinc-400 text-sm mb-4">{plan.description}</p>

                    {/* Price */}
                    <div className="mb-6">
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-medium text-white">{plan.price}</span>
                        <span className="text-zinc-400 text-xs">/ {plan.period}</span>
                      </div>
                    </div>

                    {/* CTA Button */}
                    <Button
                      onClick={() => handleSelectPlan(plan)}
                      disabled={selectedPlan === plan.id}
                      className={cn(
                        'w-full mb-6 h-10 font-medium transition-all text-sm',
                        plan.recommended
                          ? 'bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white border-0'
                          : 'bg-white/5 hover:bg-white/10 text-white border border-white/10'
                      )}
                    >
                      {selectedPlan === plan.id ? 'Processing...' : plan.tier === 'enterprise' ? 'Contact Sales' : `Get ${plan.name}`}
                    </Button>

                    {/* Features */}
                    <div className="space-y-2.5 flex-1">
                      {plan.features.map((feature: string, i: number) => (
                        <div key={i} className="flex items-start gap-2.5">
                          <div className="mt-0.5 flex-shrink-0">
                            <div className="p-0.5 rounded-full bg-teal-500/10">
                              <Check className="w-3.5 h-3.5 text-teal-400" />
                            </div>
                          </div>
                          <span className="text-xs text-zinc-300 leading-relaxed">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Competitor Comparison */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
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
          animate={{ opacity: 1 }}
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
      </div>

      {/* Testimonials Section */}
      <TestimonialsSection />
    </div>
  );
}
