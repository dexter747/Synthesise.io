'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

function CheckoutSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const paymentId = searchParams.get('paymentId');
  const token = searchParams.get('token');

  useEffect(() => {
    // Verify payment if token is present
    if (token) {
      verifyPayment(token);
    }
  }, [token]);

  const verifyPayment = async (paymentToken: string) => {
    try {
      // Payment verification is handled by the callback endpoint
      console.log('Payment completed:', paymentToken);
    } catch (error) {
      console.error('Payment verification failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <Card className="bg-zinc-900/50 border-white/10 max-w-md w-full">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-teal-500/20 flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-teal-400" />
          </div>
          
          <h1 className="text-2xl font-medium text-white mb-2">Payment Successful!</h1>
          <p className="text-gray-400 mb-6">
            Your subscription has been activated. Welcome to Synthesize.io!
          </p>
          
          {paymentId && (
            <p className="text-xs text-gray-500 mb-6">
              Payment ID: {paymentId}
            </p>
          )}
          
          <Button 
            variant="gradient" 
            className="w-full"
            onClick={() => router.push('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
      </div>
    }>
      <CheckoutSuccessContent />
    </Suspense>
  );
}
