'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useSubscriptionPlans } from '@/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Check, Loader2, ArrowLeft, Shield, CreditCard, Clock, Sparkles, Tag, Lock, Gift, BadgeCheck } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';

function CheckoutContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const planId = searchParams.get('plan');
  const { data: plans, isLoading } = useSubscriptionPlans();
  const [processing, setProcessing] = useState(false);
  const [referralCode, setReferralCode] = useState('');
  const [applyingReferral, setApplyingReferral] = useState(false);
  const [referralApplied, setReferralApplied] = useState(false);
  const [discount, setDiscount] = useState(0);

  const selectedPlan = plans?.find((p: any) => p.id === planId) as any;

  useEffect(() => {
    if (!planId) {
      router.push('/pricing');
    }
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please log in to continue with payment');
      router.push(`/login?redirect=/checkout?plan=${planId}`);
    }
  }, [planId, router]);

  const applyReferralCode = async () => {
    if (!referralCode.trim()) {
      toast.error('Please enter a referral code');
      return;
    }

    setApplyingReferral(true);
    try {
      // TODO: Implement referral code validation API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulated delay
      
      // For now, accept any code and give 10% discount
      setReferralApplied(true);
      setDiscount(10);
      toast.success('Referral code applied! 10% discount added');
    } catch (error) {
      toast.error('Invalid referral code');
    } finally {
      setApplyingReferral(false);
    }
  };

  const handleCheckout = async () => {
    if (!selectedPlan) return;
    
    setProcessing(true);
    
    // In development (localhost), use test activation instead of Dodo
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    if (isDevelopment) {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/test/activate-subscription`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            tier: selectedPlan.tier,
            billing_cycle: 'monthly',
            return_url: `${window.location.origin}/dashboard`
          })
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to activate subscription');
        }

        toast.success('Subscription activated successfully!');
        setTimeout(() => {
          router.push('/dashboard?upgraded=true');
        }, 1000);
        
      } catch (error: any) {
        console.error('Activation error:', error);
        toast.error(error.message || 'Failed to activate subscription');
        setProcessing(false);
      }
      return;
    }
    
    // Production: Use Dodo Payments
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tier: selectedPlan.tier,
          billing_cycle: 'monthly',
          referral_code: referralApplied ? referralCode : undefined,
          return_url: `${window.location.origin}/payment/callback?plan=${selectedPlan.id}`
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Dodo Payments checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error: any) {
      console.error('Checkout error:', error);
      toast.error(error.message || 'Failed to start checkout');
      setProcessing(false);
    }
  };

  if (isLoading || !selectedPlan) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
      </div>
    );
  }

  // Get price - handle different field names from API
  const monthlyPrice = selectedPlan.price_monthly ?? (selectedPlan.monthly_price_cents ? selectedPlan.monthly_price_cents / 100 : 0);
  const discountAmount = (monthlyPrice * discount) / 100;
  const finalPrice = monthlyPrice - discountAmount;

  // Build comprehensive feature list matching exact quotas from QUOTA_AND_PRICING.md
  const features: string[] = [];
  const tier = selectedPlan.tier || selectedPlan.slug;
  
  // Tier-specific features based on plan
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

  return (
    <div className="min-h-screen bg-black">
      {/* Development Mode Banner */}
      {(typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) && (
        <div className="bg-yellow-500 text-black py-2 px-4 text-center text-sm font-medium">
          🧪 Development Mode - No payment required. Subscription will activate instantly.
        </div>
      )}
      
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="border-b border-white/5 backdrop-blur-sm sticky top-0 z-40 bg-black/80"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link 
              href="/pricing"
              className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm font-medium">Back to Plans</span>
            </Link>
            <div className="flex items-center gap-6">
              <div className="hidden sm:flex items-center gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center">
                    <span className="text-xs font-medium text-teal-400">1</span>
                  </div>
                  <span className="text-xs text-teal-400 font-medium">Review</span>
                </div>
                <div className="w-8 h-px bg-white/10" />
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                    <span className="text-xs font-medium text-zinc-500">2</span>
                  </div>
                  <span className="text-xs text-zinc-500">Payment</span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-zinc-400">
                <Lock className="w-4 h-4 text-teal-400" />
                <span className="text-xs">Secure Checkout</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="max-w-7xl mx-auto px-4 py-8 lg:py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Side - Order Summary & Referral */}
          <div className="lg:col-span-1">
            {/* Order Summary (Sticky) */}
            <div className="sticky top-24 space-y-6">
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader className="pb-4">
                  <CardTitle className="text-white text-lg">Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Plan Info */}
                  <div className="space-y-4">
                    <div className="flex items-start gap-3 p-4 bg-gradient-to-r from-teal-500/10 to-emerald-500/10 rounded-lg border border-teal-500/20">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-white">{selectedPlan.name} Plan</h3>
                        <p className="text-xs text-zinc-400 mt-1">{selectedPlan.description}</p>
                      </div>
                    </div>

                    {/* Features */}
                    <div>
                      <p className="text-xs font-medium text-zinc-400 mb-3">Includes:</p>
                      <div className="space-y-2">
                        {features.map((feature, index) => (
                          <div key={index} className="flex items-start gap-2 text-xs">
                            <Check className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                            <span className="text-zinc-300">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Pricing Breakdown */}
                  <div className="space-y-3 pt-4 border-t border-white/10">
                    <div className="flex justify-between text-sm">
                      <span className="text-zinc-400">Plan ({selectedPlan.name})</span>
                      <span className="text-white font-medium">${monthlyPrice.toFixed(2)}</span>
                    </div>
                    {referralApplied && (
                      <div className="flex justify-between text-sm">
                        <span className="text-teal-400 flex items-center gap-1">
                          <Tag className="w-3 h-3" />
                          Referral Discount ({discount}%)
                        </span>
                        <span className="text-teal-400">-${discountAmount.toFixed(2)}</span>
                      </div>
                    )}
                    <div className="flex justify-between items-baseline pt-3 border-t border-white/10">
                      <span className="text-zinc-300 font-medium">Total Due Today</span>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-white">${finalPrice.toFixed(2)}</div>
                        <div className="text-xs text-zinc-500">per month</div>
                      </div>
                    </div>
                  </div>

                  {/* Trust Badges */}
                  <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/10">
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                      <Shield className="w-4 h-4 text-teal-400 flex-shrink-0" />
                      <span>256-bit SSL encrypted</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                      <Clock className="w-4 h-4 text-teal-400 flex-shrink-0" />
                      <span>Cancel anytime</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                      <CreditCard className="w-4 h-4 text-teal-400 flex-shrink-0" />
                      <span>All major cards accepted</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                      <BadgeCheck className="w-4 h-4 text-teal-400 flex-shrink-0" />
                      <span>PCI DSS compliant</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Right Side - Payment */}
          <div className="lg:col-span-2 space-y-6">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-3xl font-semibold text-white mb-2">Complete Your Purchase</h1>
              <p className="text-zinc-400">You're one step away from unlocking {selectedPlan.name}</p>
            </motion.div>

            {/* Referral Code Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2 text-lg">
                    <Gift className="w-5 h-5 text-teal-400" />
                    Have a Referral Code?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-3">
                    <div className="flex-1">
                      <Input
                        placeholder="Enter referral code"
                        value={referralCode}
                        onChange={(e) => setReferralCode(e.target.value)}
                        disabled={referralApplied}
                        className="bg-black/40 border-white/10 text-white placeholder:text-zinc-500 h-11"
                      />
                    </div>
                    <Button
                      onClick={applyReferralCode}
                      disabled={applyingReferral || referralApplied || !referralCode.trim()}
                      variant="outline"
                      className="border-white/10 hover:bg-white/5 text-white px-6"
                    >
                      {applyingReferral ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : referralApplied ? (
                        <Check className="w-4 h-4 text-teal-400" />
                      ) : (
                        'Apply'
                      )}
                    </Button>
                  </div>
                  {referralApplied && (
                    <div className="mt-3 flex items-center gap-2 text-sm text-teal-400">
                      <BadgeCheck className="w-4 h-4" />
                      <span>Referral code applied! {discount}% discount added</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Payment Method Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2 text-lg">
                    <CreditCard className="w-5 h-5 text-teal-400" />
                    Secure Payment
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Terms Checkbox */}
                  <div className="flex items-start gap-3 p-4 bg-zinc-900/50 border border-white/10 rounded-lg">
                    <input 
                      type="checkbox" 
                      id="terms" 
                      className="mt-1 h-5 w-5 rounded border-2 border-white/20 bg-black/40 text-teal-500 focus:ring-2 focus:ring-teal-400 focus:ring-offset-2 focus:ring-offset-black cursor-pointer" 
                      defaultChecked 
                    />
                    <label htmlFor="terms" className="text-sm text-zinc-300 leading-relaxed cursor-pointer">
                      I agree to the <Link href="/legal/terms" className="text-teal-400 hover:underline">Terms of Service</Link> and <Link href="/legal/privacy" className="text-teal-400 hover:underline">Privacy Policy</Link>
                    </label>
                  </div>

                  {/* Checkout Button */}
                  <Button
                    onClick={handleCheckout}
                    disabled={processing}
                    size="lg"
                    className="w-full h-14 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-semibold text-base shadow-lg shadow-teal-500/25"
                  >
                    {processing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        Redirecting to secure payment...
                      </>
                    ) : (
                      <>
                        <Lock className="w-5 h-5 mr-2" />
                        Continue to Secure Payment
                      </>
                    )}
                  </Button>

                  {/* Dodo Payments Logo */}
                  <div className="flex items-center justify-center gap-2 pt-4 border-t border-white/10">
                    <span className="text-xs text-white">Secure payments by</span>
                    <Image
                      src="/dodo.svg"
                      alt="Dodo Payments"
                      width={160}
                      height={48}
                      
                    />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-black">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
      </div>
    }>
      <CheckoutContent />
    </Suspense>
  );
}
