'use client';

import { ReactNode, useEffect, useState } from 'react';
import { useAuth } from '@/providers/auth-provider';
import { PricingModal } from '@/components/pricing-modal';
import { usePathname } from 'next/navigation';

interface PricingGateProps {
  children: ReactNode;
}

export function PricingGate({ children }: PricingGateProps) {
  const { user, isLoading } = useAuth();
  const pathname = usePathname();
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [hasSeenModal, setHasSeenModal] = useState(false);

  useEffect(() => {
    if (isLoading || hasSeenModal) return;

    // Check if user is on free tier and just logged in
    const isFreeTier = user?.subscription_tier === 'free';
    const isDashboardPath = pathname.startsWith('/dashboard') || 
                           pathname.startsWith('/datasets') || 
                           pathname.startsWith('/jobs') ||
                           pathname.startsWith('/analytics');

    // Get from localStorage if user has dismissed the modal before
    const dismissed = localStorage.getItem('pricing_modal_dismissed');
    
    if (isFreeTier && isDashboardPath && !dismissed) {
      // Show modal after a brief delay for better UX
      const timer = setTimeout(() => {
        setShowPricingModal(true);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [user, isLoading, pathname, hasSeenModal]);

  const handleDismiss = () => {
    setShowPricingModal(false);
    setHasSeenModal(true);
    // Store dismissal in localStorage (don't show again for 7 days)
    const dismissedUntil = Date.now() + (7 * 24 * 60 * 60 * 1000);
    localStorage.setItem('pricing_modal_dismissed', dismissedUntil.toString());
  };

  const handleClose = () => {
    setShowPricingModal(false);
    setHasSeenModal(true);
  };

  return (
    <>
      {children}
      <PricingModal 
        isOpen={showPricingModal} 
        onClose={handleClose}
        onDismiss={handleDismiss}
      />
    </>
  );
}
