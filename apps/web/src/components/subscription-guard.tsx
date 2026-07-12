'use client';

import { useAuth } from '@/providers/auth-provider';
import { useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';
import { Loader2, Lock, CreditCard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface SubscriptionGuardProps {
  children: ReactNode;
  requiredTiers?: string[];
  feature?: string;
}

/**
 * Guard component that ensures user has an active subscription
 * before accessing protected content.
 * 
 * @param children - Content to render if subscription is active
 * @param requiredTiers - Optional list of tiers required for this content
 * @param feature - Optional feature name for upgrade messaging
 */
export function SubscriptionGuard({ 
  children, 
  requiredTiers,
  feature 
}: SubscriptionGuardProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
      </div>
    );
  }

  // No user - redirect to login
  if (!user) {
    router.push('/auth/login');
    return null;
  }

  // No subscription or expired
  if (!user.subscription_tier) {
    return <SubscriptionRequired />;
  }

  // Check if user's tier is sufficient
  if (requiredTiers && requiredTiers.length > 0) {
    if (!requiredTiers.includes(user.subscription_tier)) {
      return <UpgradeRequired currentTier={user.subscription_tier} requiredTiers={requiredTiers} feature={feature} />;
    }
  }

  return <>{children}</>;
}

/**
 * Component shown when user has no active subscription
 */
function SubscriptionRequired() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
      <div className="p-4 rounded-full bg-amber-500/10 border border-amber-500/20 mb-6">
        <CreditCard className="w-12 h-12 text-amber-500" />
      </div>
      <h2 className="text-2xl font-medium text-white mb-3">Subscription Required</h2>
      <p className="text-zinc-400 max-w-md mb-6">
        You need an active subscription to access this feature. 
        Choose a plan that fits your needs to get started.
      </p>
      <Link href="/pricing">
        <Button variant="gradient" size="lg">
          View Plans
        </Button>
      </Link>
    </div>
  );
}

/**
 * Component shown when user needs to upgrade their plan
 */
function UpgradeRequired({ 
  currentTier, 
  requiredTiers,
  feature 
}: { 
  currentTier: string; 
  requiredTiers: string[];
  feature?: string;
}) {
  const tierLabels: Record<string, string> = {
    beginner: 'Beginner',
    pro: 'Pro',
    business: 'Business',
    enterprise: 'Enterprise',
  };

  const recommendedTier = requiredTiers[0];

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
      <div className="p-4 rounded-full bg-teal-500/10 border border-teal-500/20 mb-6">
        <Lock className="w-12 h-12 text-teal-500" />
      </div>
      <h2 className="text-2xl font-medium text-white mb-3">
        {feature ? `${feature} Requires Upgrade` : 'Upgrade Required'}
      </h2>
      <p className="text-zinc-400 max-w-md mb-2">
        Your current plan ({tierLabels[currentTier] || currentTier}) doesn't include this feature.
      </p>
      <p className="text-zinc-500 text-sm mb-6">
        Upgrade to {tierLabels[recommendedTier] || recommendedTier} or higher to unlock this feature.
      </p>
      <Link href="/pricing">
        <Button variant="gradient" size="lg">
          Upgrade Plan
        </Button>
      </Link>
    </div>
  );
}

/**
 * Hook to check if user has access to a specific feature
 */
export function useFeatureAccess() {
  const { user } = useAuth();

  const hasFeature = (feature: string): boolean => {
    if (!user?.subscription_tier) return false;
    
    const tier = user.subscription_tier.toLowerCase();
    
    // Feature access matrix
    const featureMatrix: Record<string, string[]> = {
      // API Access
      'api_access': ['pro', 'business', 'enterprise'],
      'api_keys': ['pro', 'business', 'enterprise'],
      
      // Team features
      'team_collaboration': ['business', 'enterprise'],
      'team_members': ['business', 'enterprise'],
      
      // Advanced features
      'webhooks': ['pro', 'business', 'enterprise'],
      'custom_schemas': ['pro', 'business', 'enterprise'],
      'advanced_templates': ['pro', 'business', 'enterprise'],
      'priority_processing': ['business', 'enterprise'],
      
      // Export formats
      'export_sql': ['pro', 'business', 'enterprise'],
      'export_parquet': ['business', 'enterprise'],
      'export_excel': ['business', 'enterprise'],
      
      // Enterprise features
      'sso': ['business', 'enterprise'],
      'on_premise': ['enterprise'],
      'custom_sla': ['enterprise'],
      'dedicated_support': ['enterprise'],
    };

    const allowedTiers = featureMatrix[feature];
    if (!allowedTiers) return true; // Unknown features are allowed by default
    
    return allowedTiers.includes(tier);
  };

  const getTierLimits = () => {
    if (!user?.subscription_tier) return null;
    
    const tier = user.subscription_tier.toLowerCase();
    
    const limits: Record<string, {
      rows_per_month: number;
      rows_per_dataset: number;
      datasets: number;
      retention_days: number;
      team_members: number;
    }> = {
      beginner: {
        rows_per_month: 50000,
        rows_per_dataset: 5000,
        datasets: 10,
        retention_days: 7,
        team_members: 1,
      },
      pro: {
        rows_per_month: 1000000,
        rows_per_dataset: 100000,
        datasets: 100,
        retention_days: 30,
        team_members: 1,
      },
      business: {
        rows_per_month: 10000000,
        rows_per_dataset: 1000000,
        datasets: -1, // Unlimited
        retention_days: 90,
        team_members: 10,
      },
      enterprise: {
        rows_per_month: -1, // Unlimited
        rows_per_dataset: -1,
        datasets: -1,
        retention_days: 365,
        team_members: -1,
      },
    };

    return limits[tier] || limits.beginner;
  };

  return {
    hasFeature,
    getTierLimits,
    tier: user?.subscription_tier,
    isActive: !!user?.subscription_tier && user.subscription_tier !== 'free',
  };
}

/**
 * Component wrapper that hides content based on feature access
 */
export function FeatureGate({ 
  feature, 
  children,
  fallback = null,
}: { 
  feature: string; 
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const { hasFeature } = useFeatureAccess();

  if (!hasFeature(feature)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
