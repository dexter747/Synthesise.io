'use client';

import { useRouter } from 'next/navigation';
import { XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function CheckoutCancelPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <Card className="bg-zinc-900/50 border-white/10 max-w-md w-full">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-6">
            <XCircle className="w-10 h-10 text-red-400" />
          </div>
          
          <h1 className="text-2xl font-medium text-white mb-2">Payment Cancelled</h1>
          <p className="text-gray-400 mb-6">
            Your payment was cancelled. No charges have been made.
          </p>
          
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={() => router.push('/pricing')}
            >
              View Plans
            </Button>
            <Button 
              variant="gradient" 
              className="flex-1"
              onClick={() => router.push('/dashboard')}
            >
              Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
