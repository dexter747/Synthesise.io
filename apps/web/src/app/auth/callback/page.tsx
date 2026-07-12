'use client';

import { useEffect, Suspense, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { toast } from 'sonner';
import { getAPI } from '@synthesize/api-client';

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const handleCallback = async () => {
      if (processing) return;
      
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const error = searchParams.get('error');

      if (error) {
        toast.error(`Authentication failed: ${error}`);
        router.push('/auth/login');
        return;
      }

      if (accessToken && refreshToken) {
        setProcessing(true);
        
        try {
          // Store tokens directly in localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
          }
          
          // Initialize API with tokens and fetch user
          const api = getAPI();
          api.setTokens({
            access_token: accessToken,
            refresh_token: refreshToken,
            token_type: 'bearer',
            expires_in: 3600,
          });
          
          // Wait for user data to be fetched
          const userData = await refreshUser();
          
          toast.success('Successfully signed in with Google!');
          
          // Check if user has an active subscription
          // If they have an active subscription, go to dashboard; otherwise show pricing
          try {
            const subscription = await api.getCurrentSubscription();
            
            // If subscription exists and is active, go to dashboard
            const hasActiveSub = subscription?.status?.toLowerCase() === 'active';
            
            setTimeout(() => {
              router.push(hasActiveSub ? '/dashboard' : '/pricing');
            }, 200);
          } catch (err) {
            // If subscription check fails (404 = no subscription), default to pricing page
            setTimeout(() => {
              router.push('/pricing');
            }, 200);
          }
        } catch (err) {
          console.error('OAuth callback error:', err);
          toast.error('Authentication completed but failed to fetch user data');
          // Clear any partial tokens
          if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
          setTimeout(() => {
            router.push('/auth/login');
          }, 1500);
        }
      } else {
        toast.error('Invalid authentication response');
        router.push('/auth/login');
      }
    };

    handleCallback();
  }, [searchParams, router, refreshUser, processing]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
        <p className="mt-4 text-zinc-400">Completing sign in...</p>
      </div>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
            <p className="mt-4 text-zinc-400">Loading...</p>
          </div>
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
