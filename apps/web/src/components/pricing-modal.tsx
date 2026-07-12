'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, Zap, Building2, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for getting started',
    features: [
      '10,000 rows per month',
      '1,000 rows per dataset',
      'Basic data types',
      'CSV & JSON export',
      '7-day data retention',
      'Community support',
    ],
    limitations: [
      'No team collaboration',
      'No API access',
      'Limited templates',
    ],
    icon: Sparkles,
    color: 'from-zinc-400 to-zinc-600',
    recommended: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$49',
    period: 'per month',
    description: 'For professional developers',
    features: [
      '1M rows per month',
      '100K rows per dataset',
      'All data types',
      'All export formats',
      '30-day data retention',
      'Priority support',
      'API access',
      'Advanced templates',
      'Custom schemas',
    ],
    limitations: [],
    icon: Zap,
    color: 'from-teal-400 to-emerald-500',
    recommended: true,
  },
  {
    id: 'business',
    name: 'Business',
    price: '$299',
    period: 'per month',
    description: 'For teams and growing businesses',
    features: [
      '10M rows per month',
      'Unlimited rows per dataset',
      'All Pro features',
      '90-day data retention',
      'Team collaboration (10 members)',
      'Dedicated support',
      'Advanced API features',
      'Custom integrations',
      'SSO (coming soon)',
    ],
    limitations: [],
    icon: Building2,
    color: 'from-purple-400 to-pink-500',
    recommended: false,
  },
];

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDismiss?: () => void;
}

export function PricingModal({ isOpen, onClose, onDismiss }: PricingModalProps) {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const handleSelectPlan = (planId: string) => {
    setSelectedPlan(planId);
    if (planId === 'free' && onDismiss) {
      // User chose to stay on free plan
      onDismiss();
    } else {
      // Redirect to checkout page to complete payment
      router.push(`/checkout?plan=${planId}`);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onDismiss || onClose}>
      <DialogContent className="max-w-6xl bg-zinc-950 border-white/10 p-0 overflow-hidden">
        {/* Close button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="absolute top-4 right-4 z-10 p-2 rounded-lg hover:bg-white/5 text-zinc-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        <DialogHeader className="p-8 pb-0">
          <DialogTitle className="text-3xl font-medium text-white text-center">
            Choose Your Plan
          </DialogTitle>
          <p className="text-zinc-400 text-center mt-2">
            Select the perfect plan for your data generation needs
          </p>
        </DialogHeader>

        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => {
              const Icon = plan.icon;
              const isRecommended = plan.recommended;

              return (
                <div
                  key={plan.id}
                  className={cn(
                    'relative p-6 rounded-xl border transition-all',
                    isRecommended
                      ? 'border-teal-500/50 bg-teal-500/5 scale-105'
                      : 'border-white/10 bg-zinc-900/50 hover:border-white/20'
                  )}
                >
                  {isRecommended && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-teal-400 to-emerald-500 text-white border-0 font-medium">
                      Most Popular
                    </Badge>
                  )}

                  <div className="flex flex-col h-full">
                    {/* Plan Icon */}
                    <div className={cn(
                      'w-12 h-12 rounded-lg flex items-center justify-center mb-4 bg-gradient-to-br',
                      plan.color
                    )}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>

                    {/* Plan Name & Price */}
                    <h3 className="text-xl font-medium text-white mb-2">{plan.name}</h3>
                    <div className="mb-2">
                      <span className="text-3xl font-medium text-white">{plan.price}</span>
                      <span className="text-zinc-400 ml-2">{plan.period}</span>
                    </div>
                    <p className="text-sm text-zinc-400 mb-6">{plan.description}</p>

                    {/* Features */}
                    <div className="flex-1 space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <Check className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-zinc-300">{feature}</span>
                        </div>
                      ))}
                      {plan.limitations.map((limitation, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <X className="w-5 h-5 text-zinc-600 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-zinc-500">{limitation}</span>
                        </div>
                      ))}
                    </div>

                    {/* CTA Button */}
                    <Button
                      onClick={() => handleSelectPlan(plan.id)}
                      variant={isRecommended ? 'gradient' : plan.id === 'free' ? 'outline' : 'default'}
                      className="w-full"
                      disabled={selectedPlan === plan.id}
                    >
                      {plan.id === 'free' ? 'Continue with Free' : `Get ${plan.name}`}
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Enterprise CTA */}
          <div className="mt-8 p-6 rounded-xl border border-white/10 bg-gradient-to-r from-zinc-900 to-zinc-800">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-white mb-1">Enterprise</h3>
                <p className="text-sm text-zinc-400">
                  Custom solutions for large-scale operations with unlimited everything
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => {
                  router.push('/contact?plan=enterprise');
                  onClose();
                }}
              >
                Talk to Sales
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
