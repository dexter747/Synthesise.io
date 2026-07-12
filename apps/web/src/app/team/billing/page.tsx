'use client';

import { useState } from 'react';
import { useOrganizationContext } from '@/providers/organization-provider';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  CreditCard,
  Building2,
  Check,
  Crown,
  Zap,
  Users,
  HardDrive,
  Database,
  Download,
  Receipt,
  Calendar,
  ArrowUpRight,
  ExternalLink,
  AlertTriangle,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface Invoice {
  id: string;
  number: string;
  amount: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed';
  date: string;
  pdf_url?: string;
}

// Mock data
const mockInvoices: Invoice[] = [
  { id: '1', number: 'INV-2024-001', amount: 49, currency: 'USD', status: 'paid', date: '2024-01-01' },
  { id: '2', number: 'INV-2023-012', amount: 49, currency: 'USD', status: 'paid', date: '2023-12-01' },
  { id: '3', number: 'INV-2023-011', amount: 49, currency: 'USD', status: 'paid', date: '2023-11-01' },
];

const plans = [
  {
    name: 'Starter',
    price: 0,
    period: 'forever',
    features: ['3 team members', '10K rows/month', '100MB storage', 'CSV export'],
    current: false,
  },
  {
    name: 'Professional',
    price: 49,
    period: '/month',
    features: ['10 team members', '100K rows/month', '1GB storage', 'All export formats', 'Priority support'],
    current: true,
    popular: true,
  },
  {
    name: 'Business',
    price: 199,
    period: '/month',
    features: ['50 team members', '1M rows/month', '10GB storage', 'All export formats', 'SSO', 'Dedicated support'],
    current: false,
  },
  {
    name: 'Enterprise',
    price: null,
    period: 'custom',
    features: ['Unlimited members', 'Unlimited rows', 'Unlimited storage', 'Custom integrations', 'SLA'],
    current: false,
  },
];

export default function TeamBillingPage() {
  const { currentOrganization } = useOrganizationContext();
  const [invoices] = useState<Invoice[]>(mockInvoices);
  const [isUpgrading, setIsUpgrading] = useState(false);

  const currentPlan = plans.find((p) => p.current) || plans[0];

  // Mock usage data
  const usage = {
    members: { used: 4, limit: 10 },
    rows: { used: 45000, limit: 100000 },
    storage: { used: 256, limit: 1024 }, // MB
  };

  const formatBytes = (mb: number) => {
    if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
    return `${mb} MB`;
  };

  const handleUpgrade = async (planName: string) => {
    setIsUpgrading(true);
    try {
      // Redirect to checkout or show modal
      toast.success(`Upgrading to ${planName}...`);
      await new Promise((r) => setTimeout(r, 1000));
    } finally {
      setIsUpgrading(false);
    }
  };

  const handleManageSubscription = () => {
    // Open customer portal
    window.open('/billing/manage', '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <Card className="bg-gradient-to-br from-teal-500/10 to-emerald-500/10 border-teal-500/30">
        <CardContent className="py-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="p-4 rounded-2xl bg-teal-500/20 border border-teal-500/30">
                <Crown className="w-8 h-8 text-teal-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-2xl font-medium text-white">{currentPlan.name}</h3>
                  <Badge className="bg-teal-500/20 text-teal-400 border-teal-500/30">
                    Current Plan
                  </Badge>
                </div>
                <p className="text-gray-400 mt-1">
                  ${currentPlan.price}/month • Renews on Feb 1, 2024
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleManageSubscription}
                className="flex items-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors"
              >
                <CreditCard className="w-4 h-4" />
                Manage Subscription
              </button>
              <button
                onClick={() => handleUpgrade('Business')}
                disabled={isUpgrading}
                className="flex items-center gap-2 px-4 py-2.5 bg-teal-500 text-black font-medium rounded-lg hover:bg-teal-400 transition-colors disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                Upgrade Plan
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <UsageCard
          icon={Users}
          label="Team Members"
          used={usage.members.used}
          limit={usage.members.limit}
          format={(v) => v.toString()}
          color="purple"
        />
        <UsageCard
          icon={Database}
          label="Rows Generated"
          used={usage.rows.used}
          limit={usage.rows.limit}
          format={(v) => `${(v / 1000).toFixed(0)}K`}
          color="teal"
        />
        <UsageCard
          icon={HardDrive}
          label="Storage"
          used={usage.storage.used}
          limit={usage.storage.limit}
          format={formatBytes}
          color="blue"
        />
      </div>

      {/* Plans Comparison */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" />
            Available Plans
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {plans.map((plan) => (
              <PlanCard
                key={plan.name}
                plan={plan}
                onSelect={() => handleUpgrade(plan.name)}
                isUpgrading={isUpgrading}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Payment Method */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-blue-400" />
            Payment Method
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-white/[0.02] rounded-xl border border-white/10">
            <div className="flex items-center gap-4">
              <div className="w-12 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded flex items-center justify-center">
                <span className="text-white text-xs font-medium">VISA</span>
              </div>
              <div>
                <p className="text-white font-medium">•••• •••• •••• 4242</p>
                <p className="text-sm text-gray-400">Expires 12/2025</p>
              </div>
            </div>
            <button className="text-teal-400 text-sm hover:text-teal-300 transition-colors">
              Update
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Billing History */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Receipt className="w-5 h-5 text-emerald-400" />
              Billing History
            </CardTitle>
            <button className="text-sm text-teal-400 hover:text-teal-300 transition-colors">
              Download All
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {invoices.map((invoice) => (
              <InvoiceRow key={invoice.id} invoice={invoice} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Billing Contact */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-gray-400" />
            Billing Contact
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Company Name</label>
              <input
                type="text"
                defaultValue={currentOrganization?.name}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Tax ID / VAT Number</label>
              <input
                type="text"
                placeholder="Optional"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-gray-400 mb-2">Billing Address</label>
              <textarea
                rows={2}
                placeholder="123 Main St, City, Country"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50 resize-none"
              />
            </div>
          </div>
          <button className="mt-4 px-4 py-2.5 bg-teal-500 text-black font-medium rounded-lg hover:bg-teal-400 transition-colors">
            Save Billing Info
          </button>
        </CardContent>
      </Card>
    </div>
  );
}

function UsageCard({
  icon: Icon,
  label,
  used,
  limit,
  format,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  used: number;
  limit: number;
  format: (v: number) => string;
  color: string;
}) {
  const percentage = Math.min((used / limit) * 100, 100);
  const isWarning = percentage >= 80;
  const isCritical = percentage >= 95;

  const colorClasses: Record<string, string> = {
    purple: 'from-purple-500 to-pink-500',
    teal: 'from-teal-500 to-emerald-500',
    blue: 'from-blue-500 to-cyan-500',
  };

  return (
    <div className="p-4 bg-white/[0.03] rounded-xl border border-white/10">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">{label}</span>
        </div>
        {isWarning && (
          <AlertTriangle className={`w-4 h-4 ${isCritical ? 'text-red-400' : 'text-amber-400'}`} />
        )}
      </div>
      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-2xl font-medium text-white">{format(used)}</span>
        <span className="text-gray-500">/ {format(limit)}</span>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${
            isCritical ? 'from-red-500 to-rose-500' :
            isWarning ? 'from-amber-500 to-orange-500' :
            colorClasses[color]
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function PlanCard({
  plan,
  onSelect,
  isUpgrading,
}: {
  plan: typeof plans[0];
  onSelect: () => void;
  isUpgrading: boolean;
}) {
  return (
    <div
      className={`p-5 rounded-xl border transition-all ${
        plan.current
          ? 'bg-teal-500/10 border-teal-500/30'
          : plan.popular
          ? 'bg-white/[0.03] border-amber-500/30'
          : 'bg-white/[0.03] border-white/10 hover:border-white/20'
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-medium text-white">{plan.name}</h4>
        {plan.popular && !plan.current && (
          <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-xs">
            Popular
          </Badge>
        )}
        {plan.current && (
          <Badge className="bg-teal-500/20 text-teal-400 border-teal-500/30 text-xs">
            Current
          </Badge>
        )}
      </div>

      <div className="mb-4">
        {plan.price === null ? (
          <span className="text-2xl font-medium text-white">Custom</span>
        ) : (
          <>
            <span className="text-3xl font-medium text-white">${plan.price}</span>
            <span className="text-gray-400">{plan.period}</span>
          </>
        )}
      </div>

      <ul className="space-y-2 mb-4">
        {plan.features.map((feature) => (
          <li key={feature} className="flex items-center gap-2 text-sm text-gray-400">
            <Check className="w-4 h-4 text-teal-400" />
            {feature}
          </li>
        ))}
      </ul>

      {plan.current ? (
        <button
          disabled
          className="w-full px-4 py-2.5 bg-white/5 border border-white/10 text-gray-400 rounded-lg cursor-default"
        >
          Current Plan
        </button>
      ) : plan.price === null ? (
        <button className="w-full px-4 py-2.5 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors">
          Contact Sales
        </button>
      ) : (
        <button
          onClick={onSelect}
          disabled={isUpgrading}
          className="w-full px-4 py-2.5 bg-teal-500 text-black font-medium rounded-lg hover:bg-teal-400 transition-colors disabled:opacity-50"
        >
          {isUpgrading ? 'Processing...' : 'Upgrade'}
        </button>
      )}
    </div>
  );
}

function InvoiceRow({ invoice }: { invoice: Invoice }) {
  const statusConfig = {
    paid: { label: 'Paid', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' },
    pending: { label: 'Pending', color: 'bg-amber-500/10 text-amber-400 border-amber-500/30' },
    failed: { label: 'Failed', color: 'bg-red-500/10 text-red-400 border-red-500/30' },
  };

  const config = statusConfig[invoice.status];

  return (
    <div className="flex items-center justify-between p-4 bg-white/[0.02] rounded-lg border border-white/5 hover:border-white/10 transition-colors">
      <div className="flex items-center gap-4">
        <div className="p-2 rounded-lg bg-white/5">
          <Receipt className="w-4 h-4 text-gray-400" />
        </div>
        <div>
          <p className="text-white font-medium">{invoice.number}</p>
          <p className="text-sm text-gray-400">
            {new Date(invoice.date).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-white font-medium">
          ${invoice.amount.toFixed(2)} {invoice.currency}
        </span>
        <Badge className={`${config.color} border`}>{config.label}</Badge>
        <button className="p-2 rounded-lg hover:bg-white/5 transition-colors text-gray-400 hover:text-white">
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
