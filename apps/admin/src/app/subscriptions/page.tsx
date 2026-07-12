'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAPI } from '@synthesize/api-client';
import { formatDate, formatCurrency, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Search,
  CreditCard,
  Loader2,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
  DollarSign,
  Users,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Download,
  Filter,
  Eye,
  Mail,
  Pause,
  Play,
  Ban,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Zap,
  ArrowUpRight,
  BarChart3,
  Calendar,
  Percent,
} from 'lucide-react';

export default function AdminSubscriptionsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  const [showActions, setShowActions] = useState<string | null>(null);

  const queryClient = useQueryClient();

  const { data: subscriptions, isLoading, refetch } = useQuery({
    queryKey: ['admin', 'subscriptions', page, search, statusFilter, planFilter],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/subscriptions', {
        params: {
          page,
          per_page: 20,
          search: search || undefined,
          status: statusFilter || undefined,
          plan: planFilter || undefined,
        },
      });
      return response.data;
    },
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin', 'subscription-stats'],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/subscriptions/stats');
      return response.data;
    },
  });

  const items = subscriptions?.items || [];
  const totalPages = Math.ceil((subscriptions?.total || 0) / 20);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return CheckCircle;
      case 'trialing':
        return Clock;
      case 'past_due':
        return AlertTriangle;
      case 'canceled':
        return XCircle;
      case 'paused':
        return Pause;
      default:
        return CreditCard;
    }
  };

  const getPlanTierColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'enterprise':
        return 'from-purple-500 to-pink-500';
      case 'pro':
        return 'from-teal-400 to-cyan-500';
      case 'starter':
        return 'from-blue-500 to-indigo-500';
      case 'free':
        return 'from-gray-500 to-gray-600';
      default:
        return 'from-teal-400 to-teal-600';
    }
  };

  return (
    <AdminLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium text-white">Subscription Management</h1>
            <p className="text-gray-400 mt-1">Monitor and manage all subscription plans and billing</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="border-gray-700 hover:bg-white/5"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="border-gray-700 hover:bg-white/5"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Monthly Recurring Revenue"
            value={formatCurrency(stats?.mrr || 0)}
            change="+12.5%"
            trend="up"
            icon={DollarSign}
            loading={statsLoading}
            color="teal"
          />
          <StatCard
            title="Active Subscriptions"
            value={formatNumber(stats?.active_count || 0)}
            change="+8"
            trend="up"
            icon={CreditCard}
            loading={statsLoading}
            color="blue"
          />
          <StatCard
            title="Trial Users"
            value={formatNumber(stats?.trial_count || 0)}
            change="+15"
            trend="up"
            icon={Users}
            loading={statsLoading}
            color="purple"
          />
          <StatCard
            title="Churn Rate"
            value={`${stats?.churn_rate || 0}%`}
            change="-0.3%"
            trend="down"
            icon={Percent}
            loading={statsLoading}
            color="amber"
          />
        </div>

        {/* Revenue Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <RevenueCard
            title="Annual Recurring Revenue"
            value={formatCurrency((stats?.mrr || 0) * 12)}
            subtitle="Projected based on MRR"
            icon={BarChart3}
          />
          <RevenueCard
            title="Average Revenue Per User"
            value={formatCurrency(stats?.arpu || 45)}
            subtitle="Across all paid plans"
            icon={TrendingUp}
          />
          <RevenueCard
            title="Lifetime Value"
            value={formatCurrency(stats?.ltv || 540)}
            subtitle="Based on avg. subscription length"
            icon={Zap}
          />
        </div>

        {/* Filters */}
        <Card className="admin-card">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <Input
                  placeholder="Search by name or email..."
                  className="pl-10 input-dark"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setPage(1);
                  }}
                />
              </div>
              <div className="flex gap-3">
                <select
                  className="px-4 py-2 bg-white/[0.03] border border-white/10 rounded-xl text-sm text-white
                    focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50
                    hover:bg-white/[0.05] transition-colors cursor-pointer min-w-[140px]"
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="trialing">Trialing</option>
                  <option value="past_due">Past Due</option>
                  <option value="canceled">Canceled</option>
                  <option value="paused">Paused</option>
                </select>
                <select
                  className="px-4 py-2 bg-white/[0.03] border border-white/10 rounded-xl text-sm text-white
                    focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50
                    hover:bg-white/[0.05] transition-colors cursor-pointer min-w-[140px]"
                  value={planFilter}
                  onChange={(e) => {
                    setPlanFilter(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All Plans</option>
                  <option value="free">Free</option>
                  <option value="starter">Starter</option>
                  <option value="pro">Pro</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subscriptions Table */}
        <Card className="admin-card overflow-hidden">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 animate-spin text-teal-500 mb-4" />
                <p className="text-gray-400">Loading subscriptions...</p>
              </div>
            ) : items.length === 0 ? (
              <div className="text-center py-20">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-teal-500/20 to-cyan-500/20 flex items-center justify-center">
                  <CreditCard className="w-8 h-8 text-teal-400" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">No subscriptions found</h3>
                <p className="text-gray-400 max-w-sm mx-auto">
                  Try adjusting your search or filter criteria
                </p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="table-header">
                        <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Subscriber
                        </th>
                        <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Plan
                        </th>
                        <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Started
                        </th>
                        <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Next Billing
                        </th>
                        <th className="text-right py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {items.map((sub: any, index: number) => (
                        <tr
                          key={sub.id}
                          className="table-row group animate-fade-in"
                          style={{ animationDelay: `${index * 50}ms` }}
                        >
                          <td className="table-cell py-4 px-6">
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getPlanTierColor(sub.plan?.tier)} 
                                flex items-center justify-center text-white text-sm font-medium shadow-lg`}>
                                {sub.user?.name?.charAt(0).toUpperCase() || 'U'}
                              </div>
                              <div>
                                <p className="text-sm font-medium text-white group-hover:text-teal-400 transition-colors">
                                  {sub.user?.name || 'Unknown User'}
                                </p>
                                <p className="text-xs text-gray-500">{sub.user?.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="table-cell py-4 px-6">
                            <PlanBadge plan={sub.plan?.name} tier={sub.plan?.tier} />
                          </td>
                          <td className="table-cell py-4 px-6">
                            <SubscriptionBadge status={sub.status} />
                          </td>
                          <td className="table-cell py-4 px-6">
                            <div>
                              <p className="text-sm font-medium text-white">
                                {formatCurrency(sub.amount / 100)}
                              </p>
                              <p className="text-xs text-gray-500">per {sub.interval}</p>
                            </div>
                          </td>
                          <td className="table-cell py-4 px-6">
                            <div className="flex items-center gap-2">
                              <Calendar className="w-3.5 h-3.5 text-gray-500" />
                              <span className="text-sm text-gray-400">{formatDate(sub.created_at)}</span>
                            </div>
                          </td>
                          <td className="table-cell py-4 px-6">
                            {sub.current_period_end ? (
                              <div className="flex items-center gap-2">
                                <Clock className="w-3.5 h-3.5 text-gray-500" />
                                <span className="text-sm text-gray-400">
                                  {formatDate(sub.current_period_end)}
                                </span>
                              </div>
                            ) : (
                              <span className="text-sm text-gray-600">—</span>
                            )}
                          </td>
                          <td className="table-cell py-4 px-6 text-right">
                            <div className="relative">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="hover:bg-white/5"
                                onClick={() => setShowActions(showActions === sub.id ? null : sub.id)}
                              >
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                              {showActions === sub.id && (
                                <div className="absolute right-0 mt-2 w-48 glass rounded-xl py-1 z-10 border border-white/10
                                  shadow-2xl shadow-black/50 animate-fade-in">
                                  <ActionItem icon={Eye} label="View Details" onClick={() => setShowActions(null)} />
                                  <ActionItem icon={Mail} label="Send Email" onClick={() => setShowActions(null)} />
                                  <div className="h-px bg-white/5 my-1" />
                                  {sub.status === 'active' && (
                                    <ActionItem icon={Pause} label="Pause Subscription" onClick={() => setShowActions(null)} />
                                  )}
                                  {sub.status === 'paused' && (
                                    <ActionItem icon={Play} label="Resume Subscription" onClick={() => setShowActions(null)} />
                                  )}
                                  <ActionItem
                                    icon={Ban}
                                    label="Cancel Subscription"
                                    onClick={() => setShowActions(null)}
                                    danger
                                  />
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
                    <p className="text-sm text-gray-400">
                      Showing <span className="text-white font-medium">{(page - 1) * 20 + 1}</span> to{' '}
                      <span className="text-white font-medium">
                        {Math.min(page * 20, subscriptions?.total || 0)}
                      </span>{' '}
                      of <span className="text-white font-medium">{subscriptions?.total || 0}</span> subscriptions
                    </p>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="border-white/10 hover:bg-white/5 disabled:opacity-30"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum;
                        if (totalPages <= 5) {
                          pageNum = i + 1;
                        } else if (page <= 3) {
                          pageNum = i + 1;
                        } else if (page >= totalPages - 2) {
                          pageNum = totalPages - 4 + i;
                        } else {
                          pageNum = page - 2 + i;
                        }
                        return (
                          <Button
                            key={pageNum}
                            variant={page === pageNum ? 'primary' : 'outline'}
                            size="sm"
                            onClick={() => setPage(pageNum)}
                            className={
                              page === pageNum
                                ? 'bg-teal-500 hover:bg-teal-600'
                                : 'border-white/10 hover:bg-white/5'
                            }
                          >
                            {pageNum}
                          </Button>
                        );
                      })}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="border-white/10 hover:bg-white/5 disabled:opacity-30"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Plan Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <PlanDistributionCard plan="Free" count={stats?.free_count || 124} percentage={35} color="gray" />
          <PlanDistributionCard plan="Starter" count={stats?.starter_count || 89} percentage={25} color="blue" />
          <PlanDistributionCard plan="Pro" count={stats?.pro_count || 98} percentage={28} color="teal" />
          <PlanDistributionCard plan="Enterprise" count={stats?.enterprise_count || 42} percentage={12} color="purple" />
        </div>
      </div>
    </AdminLayout>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  change,
  trend,
  icon: Icon,
  loading,
  color = 'teal',
}: {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down';
  icon: React.ComponentType<{ className?: string }>;
  loading?: boolean;
  color?: 'teal' | 'blue' | 'purple' | 'amber';
}) {
  const colorMap = {
    teal: 'from-teal-500/20 to-cyan-500/20 text-teal-400',
    blue: 'from-blue-500/20 to-indigo-500/20 text-blue-400',
    purple: 'from-purple-500/20 to-pink-500/20 text-purple-400',
    amber: 'from-amber-500/20 to-orange-500/20 text-amber-400',
  };

  return (
    <Card className="admin-card group hover:scale-[1.02] transition-all duration-300">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-3">
            <p className="text-sm font-medium text-gray-400">{title}</p>
            {loading ? (
              <div className="h-8 w-24 bg-white/5 animate-pulse rounded-lg" />
            ) : (
              <p className="text-2xl font-medium text-white">{value}</p>
            )}
            {change && !loading && (
              <div className="flex items-center gap-1">
                {trend === 'up' ? (
                  <TrendingUp className="w-3.5 h-3.5 text-green-400" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5 text-green-400" />
                )}
                <span className="text-xs text-green-400">{change}</span>
                <span className="text-xs text-gray-500">vs last month</span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colorMap[color]} transition-transform group-hover:scale-110`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Revenue Card Component
function RevenueCard({
  title,
  value,
  subtitle,
  icon: Icon,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card className="admin-card">
      <CardContent className="p-5">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-teal-500/10 to-cyan-500/10">
            <Icon className="w-6 h-6 text-teal-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">{title}</p>
            <p className="text-xl font-medium text-white mt-0.5">{value}</p>
            <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Plan Badge Component
function PlanBadge({ plan, tier }: { plan: string; tier?: string }) {
  const tierColors: Record<string, string> = {
    enterprise: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    pro: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
    starter: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    free: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium border
        ${tierColors[tier?.toLowerCase() || 'free'] || tierColors.free}`}
    >
      {plan || 'Free'}
    </span>
  );
}

// Subscription Badge Component
function SubscriptionBadge({ status }: { status: string }) {
  const variants: Record<string, { bg: string; text: string; icon: any; dot: string }> = {
    active: {
      bg: 'bg-green-500/10',
      text: 'text-green-400',
      icon: CheckCircle,
      dot: 'bg-green-400',
    },
    trialing: {
      bg: 'bg-blue-500/10',
      text: 'text-blue-400',
      icon: Clock,
      dot: 'bg-blue-400',
    },
    past_due: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      icon: AlertTriangle,
      dot: 'bg-amber-400',
    },
    canceled: {
      bg: 'bg-gray-500/10',
      text: 'text-gray-400',
      icon: XCircle,
      dot: 'bg-gray-400',
    },
    paused: {
      bg: 'bg-orange-500/10',
      text: 'text-orange-400',
      icon: Pause,
      dot: 'bg-orange-400',
    },
    incomplete: {
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      icon: AlertTriangle,
      dot: 'bg-red-400',
    },
  };

  const variant = variants[status] || variants.canceled;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${variant.bg} ${variant.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${variant.dot} animate-pulse`} />
      {status.replace('_', ' ')}
    </span>
  );
}

// Action Item Component
function ActionItem({
  icon: Icon,
  label,
  onClick,
  danger = false,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick: () => void;
  danger?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-2 px-4 py-2 text-sm transition-colors
        ${danger ? 'text-red-400 hover:bg-red-500/10' : 'text-gray-300 hover:bg-white/5'}`}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  );
}

// Plan Distribution Card Component
function PlanDistributionCard({
  plan,
  count,
  percentage,
  color,
}: {
  plan: string;
  count: number;
  percentage: number;
  color: 'gray' | 'blue' | 'teal' | 'purple';
}) {
  const colorMap = {
    gray: {
      gradient: 'from-gray-500/20 to-gray-600/20',
      bar: 'bg-gray-500',
      text: 'text-gray-400',
    },
    blue: {
      gradient: 'from-blue-500/20 to-indigo-500/20',
      bar: 'bg-blue-500',
      text: 'text-blue-400',
    },
    teal: {
      gradient: 'from-teal-500/20 to-cyan-500/20',
      bar: 'bg-teal-500',
      text: 'text-teal-400',
    },
    purple: {
      gradient: 'from-purple-500/20 to-pink-500/20',
      bar: 'bg-purple-500',
      text: 'text-purple-400',
    },
  };

  const colors = colorMap[color];

  return (
    <Card className="admin-card">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className={`text-sm font-medium ${colors.text}`}>{plan}</span>
          <span className="text-lg font-medium text-white">{count}</span>
        </div>
        <div className="h-2 rounded-full bg-white/5 overflow-hidden">
          <div
            className={`h-full ${colors.bar} rounded-full transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">{percentage}% of total subscribers</p>
      </CardContent>
    </Card>
  );
}
