'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { CheckCircle2, Loader2, Zap } from 'lucide-react';

export default function TestActivateSubscriptionPage() {
  const router = useRouter();
  const [activating, setActivating] = useState<string | null>(null);

  const activateSubscription = async (tier: string) => {
    setActivating(tier);
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        toast.error('Please log in first');
        router.push('/auth/login');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/test/activate-subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tier: tier,
          billing_cycle: 'monthly',
          return_url: 'http://localhost:3000/dashboard'
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to activate subscription');
      }

      const data = await response.json();
      toast.success(`${tier.charAt(0).toUpperCase() + tier.slice(1)} subscription activated!`);
      
      // Redirect to dashboard after short delay
      setTimeout(() => {
        router.push('/dashboard?upgraded=true');
      }, 1500);
      
    } catch (error: any) {
      console.error('Activation error:', error);
      toast.error(error.message || 'Failed to activate subscription');
    } finally {
      setActivating(null);
    }
  };

  const plans = [
    {
      tier: 'beginner',
      name: 'Beginner',
      price: '$19/month',
      features: [
        '50,000 rows/month',
        '5 datasets max',
        'CSV & JSON export',
        '7-day data retention'
      ]
    },
    {
      tier: 'pro',
      name: 'Pro',
      price: '$49/month',
      features: [
        '500,000 rows/month',
        '50 datasets',
        'API access',
        'Webhooks',
        'Custom schemas',
        '90-day retention'
      ]
    },
    {
      tier: 'business',
      name: 'Business',
      price: '$299/month',
      features: [
        '5M rows/month',
        'Unlimited datasets',
        'Priority support',
        'SSO',
        'Team collaboration',
        '1-year retention'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Zap className="w-4 h-4" />
            TEST MODE ONLY
          </div>
          <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
            Test Subscription Activation
          </h1>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Instantly activate any subscription plan for local testing without payment.
            Choose a plan below to activate it immediately.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {plans.map((plan) => (
            <Card 
              key={plan.tier}
              className="hover:shadow-lg transition-shadow border-2"
            >
              <CardHeader>
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription className="text-xl font-semibold text-slate-900">
                  {plan.price}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => activateSubscription(plan.tier)}
                  disabled={activating !== null}
                  className="w-full"
                  size="lg"
                >
                  {activating === plan.tier ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Activating...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Activate {plan.name}
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="bg-slate-50 border-slate-200">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <div className="bg-blue-100 text-blue-600 p-2 rounded-lg">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold mb-1">How This Works</h3>
                <p className="text-sm text-slate-600">
                  This page uses the test activation endpoint to instantly create a subscription 
                  without requiring payment. In production, subscriptions are created via Dodo 
                  Payments webhooks after successful payment. Any existing active subscriptions 
                  will be cancelled when you activate a new one.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
