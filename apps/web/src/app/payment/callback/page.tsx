'use client';

import { Suspense } from 'react';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

function PaymentCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [activating, setActivating] = useState(false);
  
  useEffect(() => {
    const status = searchParams.get('status');
    const planId = searchParams.get('plan');
    const sessionId = searchParams.get('session_id');
    
    // Handle payment status
    if (status === 'success') {
      toast.success('Payment successful! Your subscription is now active.');
      // Redirect to dashboard after short delay
      setTimeout(() => {
        router.push('/dashboard?upgraded=true');
      }, 2000);
    } else if (status === 'cancelled' || status === 'failed') {
      toast.error('Payment was cancelled or failed. Please try again.');
      // Don't auto-redirect on failure, let user decide
    } else {
      // No status, redirect to dashboard
      router.push('/dashboard');
    }
  }, [searchParams, router]);
  
  const handleManualActivation = async () => {
    const planId = searchParams.get('plan');
    if (!planId) {
      toast.error('No plan ID found');
      return;
    }
    
    setActivating(true);
    try {
      const token = localStorage.getItem('access_token');
      
      // Get plan details first to know the tier
      const plansResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/subscriptions/plans`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const plans = await plansResponse.json();
      const plan = plans.find((p: any) => p.id === planId);
      
      if (!plan) {
        throw new Error('Plan not found');
      }
      
      // Activate subscription via test endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/test/activate-subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tier: plan.tier,
          billing_cycle: 'monthly'
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to activate subscription');
      }
      
      toast.success('Subscription activated successfully!');
      setTimeout(() => {
        router.push('/dashboard?upgraded=true');
      }, 1000);
      
    } catch (error: any) {
      toast.error(error.message || 'Failed to activate subscription');
      setActivating(false);
    }
  };
  
  const status = searchParams.get('status');
  
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        {status === 'success' ? (
          <>
            <CheckCircle2 className="w-16 h-16 text-teal-500 mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-white mb-2">Payment Successful!</h1>
            <p className="text-zinc-400">Redirecting to dashboard...</p>
          </>
        ) : status === 'cancelled' || status === 'failed' ? (
          <>
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-white mb-2">Payment {status === 'cancelled' ? 'Cancelled' : 'Failed'}</h1>
            <p className="text-zinc-400 mb-6">
              {status === 'cancelled' 
                ? 'You cancelled the payment process.' 
                : 'The payment could not be processed.'}
            </p>
            
            {/* Test Mode Manual Activation */}
            <div className="space-y-3">
              <Button
                onClick={() => router.push(`/checkout?plan=${searchParams.get('plan')}`)}
                variant="gradient"
                size="lg"
                className="w-full"
              >
                Try Again
              </Button>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-zinc-800"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-black px-2 text-zinc-500">Test Mode Only</span>
                </div>
              </div>
              
              <Button
                onClick={handleManualActivation}
                disabled={activating}
                variant="outline"
                size="lg"
                className="w-full"
              >
                {activating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Activating...
                  </>
                ) : (
                  'Activate Without Payment (Test)'
                )}
              </Button>
            </div>
          </>
        ) : (
          <>
            <Loader2 className="w-16 h-16 text-teal-500 animate-spin mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-white mb-2">Processing...</h1>
            <p className="text-zinc-400">Please wait...</p>
          </>
        )}
      </div>
    </div>
  );
}

export default function PaymentCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-teal-500 animate-spin mx-auto mb-4" />
          <h1 className="text-2xl font-semibold text-white mb-2">Loading...</h1>
        </div>
      </div>
    }>
      <PaymentCallbackContent />
    </Suspense>
  );
}
