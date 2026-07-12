'use client';

import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  useCurrentSubscription,
  useUsage,
  useSubscriptionPlans,
  useBillingPortal,
  useInvoices,
} from '@/hooks/use-api';
import { formatCurrency, formatDate, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';
import {
  CreditCard,
  Zap,
  TrendingUp,
  Check,
  ExternalLink,
  Download,
  Loader2,
  Calendar,
  AlertCircle,
  Crown,
  Sparkles,
  ArrowRight,
} from 'lucide-react';

export default function BillingPage() {
  const { data: subscription, isLoading: subLoading } = useCurrentSubscription();
  const { data: usage, isLoading: usageLoading } = useUsage();
  const { data: plans } = useSubscriptionPlans();
  const { data: invoicesData, isLoading: invoicesLoading } = useInvoices();
  const billingPortal = useBillingPortal();

  const invoices = invoicesData?.items || [];

  const handleManageBilling = async () => {
    try {
      const { portal_url } = await billingPortal.mutateAsync();
      window.open(portal_url, '_blank');
    } catch (error: any) {
      toast.error(error.message || 'Failed to open billing portal');
    }
  };

  const currentPlan = plans?.find((p) => p.id === subscription?.plan_id);

  // Calculate days remaining
  const getDaysRemaining = () => {
    if (!subscription?.current_period_end) return null;
    const endDate = new Date(subscription.current_period_end);
    const today = new Date();
    const diffTime = endDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysRemaining = getDaysRemaining();

  return (
    <DashboardLayout>
      <div className="max-w-4xl space-y-6">
        <div>
          <h1 className="text-2xl font-medium text-white">Billing</h1>
          <p className="text-zinc-400 mt-1">Manage your subscription and billing</p>
        </div>

        {/* Current Plan Status - Hero Card */}
        <Card className="bg-gradient-to-br from-zinc-900/80 via-zinc-900/50 to-zinc-900/80 border-white/10 overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-transparent to-emerald-500/10" />
          <CardContent className="p-8 relative">
            {subLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
              </div>
            ) : subscription && currentPlan ? (
              <div className="space-y-6">
                {/* Plan Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
                      <Crown className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <div className="flex items-center gap-3">
                        <h2 className="text-2xl font-medium text-white">{currentPlan.name} Plan</h2>
                        <Badge 
                          variant={subscription.status === 'active' ? 'success' : 'warning'}
                          className="uppercase text-xs font-medium"
                        >
                          {subscription.status}
                        </Badge>
                      </div>
                      <p className="text-zinc-400 mt-1">
                        {formatCurrency(currentPlan.price_monthly)} per month
                        {subscription.cancel_at_period_end && (
                          <span className="text-orange-400 ml-2">• Cancels at period end</span>
                        )}
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" onClick={handleManageBilling} loading={billingPortal.isPending}>
                    Manage Subscription
                    <ExternalLink className="w-4 h-4 ml-2" />
                  </Button>
                </div>

                {/* Billing Period */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-2 text-zinc-400 mb-2">
                      <Calendar className="w-4 h-4" />
                      <span className="text-sm">Current Period</span>
                    </div>
                    <p className="text-white font-medium">
                      {formatDate(subscription.current_period_start)} - {formatDate(subscription.current_period_end)}
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-2 text-zinc-400 mb-2">
                      <TrendingUp className="w-4 h-4" />
                      <span className="text-sm">{subscription.cancel_at_period_end ? 'Ends In' : 'Renews In'}</span>
                    </div>
                    <p className="text-white font-medium">
                      {daysRemaining} day{daysRemaining !== 1 ? 's' : ''}
                      {daysRemaining && daysRemaining <= 7 && !subscription.cancel_at_period_end && (
                        <span className="text-teal-400 text-sm ml-2">Auto-renews</span>
                      )}
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-2 text-zinc-400 mb-2">
                      <CreditCard className="w-4 h-4" />
                      <span className="text-sm">Next Invoice</span>
                    </div>
                    <p className="text-white font-medium">
                      {subscription.cancel_at_period_end ? (
                        <span className="text-orange-400">No future charges</span>
                      ) : (
                        formatCurrency(currentPlan.price_monthly)
                      )}
                    </p>
                  </div>
                </div>

                {/* Plan Features Summary */}
                <div className="flex flex-wrap gap-3">
                  <Badge variant="outline" className="border-teal-500/30 text-teal-400">
                    <Check className="w-3 h-3 mr-1" />
                    {formatNumber(currentPlan.features?.rows_per_month || 0)} rows/month
                  </Badge>
                  <Badge variant="outline" className="border-teal-500/30 text-teal-400">
                    <Check className="w-3 h-3 mr-1" />
                    {currentPlan.features?.datasets_limit || 0} datasets
                  </Badge>
                  {currentPlan.features?.api_access && (
                    <Badge variant="outline" className="border-teal-500/30 text-teal-400">
                      <Check className="w-3 h-3 mr-1" />
                      API Access
                    </Badge>
                  )}
                  {currentPlan.features?.priority_support && (
                    <Badge variant="outline" className="border-teal-500/30 text-teal-400">
                      <Check className="w-3 h-3 mr-1" />
                      Priority Support
                    </Badge>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-20 h-20 rounded-2xl bg-zinc-800/50 flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-10 h-10 text-zinc-600" />
                </div>
                <h3 className="text-xl font-medium text-white">Free Plan</h3>
                <p className="text-zinc-500 mt-2 mb-6 max-w-md mx-auto">
                  You&apos;re on the free plan. Upgrade to unlock more features, higher limits, and priority support.
                </p>
                <Button variant="gradient" onClick={() => (window.location.href = '/pricing')}>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Upgrade Now
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Usage */}
        <Card glass>
          <CardHeader>
            <CardTitle>Usage This Month</CardTitle>
          </CardHeader>
          <CardContent>
            {usageLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <UsageStat
                  label="Rows Generated"
                  value={usage?.rows_generated || 0}
                  limit={usage?.rows_limit}
                  icon={TrendingUp}
                />
                <UsageStat
                  label="Datasets"
                  value={usage?.datasets_count || 0}
                  limit={usage?.datasets_limit}
                  icon={Zap}
                />
                <UsageStat
                  label="API Calls"
                  value={usage?.api_calls || 0}
                  icon={CreditCard}
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Available Plans */}
        {plans && plans.length > 0 && (
          <Card glass>
            <CardHeader>
              <CardTitle>Available Plans</CardTitle>
              <CardDescription>Compare plans and upgrade anytime</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {plans.map((plan) => {
                  const isCurrent = subscription?.plan_id === plan.id;
                  return (
                    <div
                      key={plan.id}
                      className={`p-5 rounded-xl border-2 transition-all ${
                        isCurrent
                          ? 'border-teal-500 bg-teal-500/10'
                          : 'border-white/10 hover:border-white/20'
                      }`}
                    >
                      {isCurrent && (
                        <Badge className="mb-3 bg-teal-500 text-white">Current Plan</Badge>
                      )}
                      <h4 className="font-medium text-white text-lg">{plan.name}</h4>
                      <p className="text-3xl font-medium text-white mt-2">
                        {formatCurrency(plan.price_monthly)}
                        <span className="text-sm font-normal text-zinc-500">/mo</span>
                      </p>
                      <ul className="mt-4 space-y-2">
                        <li className="flex items-center gap-2 text-sm text-zinc-400">
                          <Check className="w-4 h-4 text-emerald-400" />
                          {formatNumber(plan.features?.rows_per_month || 0)} rows/month
                        </li>
                        <li className="flex items-center gap-2 text-sm text-zinc-400">
                          <Check className="w-4 h-4 text-emerald-400" />
                          {plan.features?.datasets_limit || 0} datasets
                        </li>
                        <li className="flex items-center gap-2 text-sm text-zinc-400">
                          <Check className="w-4 h-4 text-emerald-400" />
                          {plan.features?.api_access ? 'API Access' : 'No API Access'}
                        </li>
                        {plan.features?.priority_support && (
                          <li className="flex items-center gap-2 text-sm text-zinc-400">
                            <Check className="w-4 h-4 text-emerald-400" />
                            Priority Support
                          </li>
                        )}
                      </ul>
                      {!isCurrent && (
                        <Button
                          className="w-full mt-4"
                          variant={plan.name === 'Pro' ? 'gradient' : 'outline'}
                          onClick={handleManageBilling}
                        >
                          {subscription ? 'Switch Plan' : 'Get Started'}
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Invoices */}
        <Card glass>
          <CardHeader>
            <CardTitle>Invoices</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {invoicesLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
              </div>
            ) : invoices.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-zinc-500">No invoices yet</p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="flex items-center justify-between px-6 py-4">
                    <div>
                      <p className="font-medium text-white">
                        {formatDate(invoice.invoice_date, { dateStyle: 'long' })}
                      </p>
                      <p className="text-sm text-zinc-500">
                        {formatCurrency(invoice.amount_cents / 100)} • 
                        <Badge variant={invoice.status === 'paid' ? 'success' : 'default'} className="ml-2">
                          {invoice.status}
                        </Badge>
                      </p>
                    </div>
                    {invoice.pdf_url && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(invoice.pdf_url, '_blank')}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

function UsageStat({
  label,
  value,
  limit,
  icon: Icon,
}: {
  label: string;
  value: number;
  limit?: number;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const percentage = limit ? Math.min((value / limit) * 100, 100) : 0;
  const isNearLimit = percentage > 80;
  const isOverLimit = percentage >= 100;

  return (
    <div>
      <div className="flex items-center gap-2 text-sm text-zinc-500 mb-2">
        <Icon className="w-4 h-4" />
        {label}
      </div>
      <p className="text-2xl font-medium text-white">
        {formatNumber(value)}
        {limit && <span className="text-sm font-normal text-zinc-500"> / {formatNumber(limit)}</span>}
      </p>
      {limit && (
        <div className="mt-2">
          <div className="w-full bg-zinc-800 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                isOverLimit ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-gradient-to-r from-teal-500 to-emerald-500'
              }`}
              style={{ width: `${percentage}%` }}
            />
          </div>
          {isNearLimit && (
            <p className="text-xs text-orange-400 mt-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {isOverLimit ? 'Limit reached' : 'Approaching limit'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
