'use client';

import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAdminDashboard, useSystemHealth } from '@/hooks/use-admin-api';
import { formatNumber, formatCurrency } from '@/lib/utils';
import {
  Users,
  CreditCard,
  Database,
  Play,
  TrendingUp,
  TrendingDown,
  Activity,
  Loader2,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Zap,
  DollarSign,
  ArrowUpRight,
} from 'lucide-react';

export default function AdminDashboardPage() {
  const { data: dashboard, isLoading } = useAdminDashboard();
  const { data: health } = useSystemHealth();

  return (
    <AdminLayout>
      <div className="space-y-8">
        {/* Welcome Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-medium gradient-teal-text">Dashboard Overview</h2>
            <p className="text-gray-400 mt-2">Monitor your platform's performance and metrics</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 glass rounded-xl border border-teal-500/20">
            <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" />
            <span className="text-sm text-gray-400">Live Data</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={dashboard?.total_users || 0}
            change={12.5}
            icon={Users}
            loading={isLoading}
            color="teal"
          />
          <StatCard
            title="Active Users"
            value={dashboard?.active_users || 0}
            change={8.3}
            icon={Zap}
            loading={isLoading}
            color="emerald"
          />
          <StatCard
            title="Total Datasets"
            value={dashboard?.total_datasets || 0}
            change={15.8}
            icon={Database}
            loading={isLoading}
            color="blue"
          />
          <StatCard
            title="Total Jobs"
            value={dashboard?.total_jobs || 0}
            change={-2.4}
            icon={Play}
            loading={isLoading}
            color="purple"
          />
        </div>

        {/* Revenue & System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue */}
          <Card className="glass border-white/10">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30">
                  <DollarSign className="w-5 h-5 text-teal-400" />
                </div>
                <CardTitle className="text-white">Revenue Overview</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-teal-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-6 glass rounded-xl border border-teal-500/20 bg-gradient-to-br from-teal-500/5 to-transparent">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-gray-400 mb-1">Revenue This Month</p>
                        <p className="text-4xl font-medium gradient-teal-text">
                          {formatCurrency(dashboard?.revenue_this_month || 0)}
                        </p>
                        <div className="flex items-center gap-1 mt-2 text-emerald-400">
                          <TrendingUp className="w-4 h-4" />
                          <span className="text-sm font-medium">+18.2%</span>
                          <span className="text-xs text-gray-500">vs last month</span>
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-teal-500/10">
                        <ArrowUpRight className="w-6 h-6 text-teal-400" />
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 glass rounded-xl border border-white/5">
                      <p className="text-xs text-gray-400 mb-2">Rows Generated Today</p>
                      <p className="text-2xl font-medium text-white">
                        {formatNumber(dashboard?.rows_generated_today || 0)}
                      </p>
                      <div className="flex items-center gap-1 mt-1 text-teal-400 text-xs">
                        <TrendingUp className="w-3 h-3" />
                        <span>+12.5%</span>
                      </div>
                    </div>
                    <div className="p-4 glass rounded-xl border border-white/5">
                      <p className="text-xs text-gray-400 mb-2">New Users This Week</p>
                      <p className="text-2xl font-medium text-white">
                        {formatNumber(dashboard?.new_users_this_week || 0)}
                      </p>
                      <div className="flex items-center gap-1 mt-1 text-emerald-400 text-xs">
                        <TrendingUp className="w-3 h-3" />
                        <span>+8.3%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* System Health */}
          <Card className="glass border-white/10">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30">
                    <Activity className="w-5 h-5 text-emerald-400" />
                  </div>
                  <CardTitle className="text-white">System Health</CardTitle>
                </div>
                <HealthBadge status={health?.api_status || 'unknown'} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <HealthItem 
                  label="API Server"
                  status={health?.api_status || 'unknown'}
                  details="Response time: 45ms"
                />
                <HealthItem 
                  label="Database"
                  status={health?.database_status || 'unknown'}
                  details="PostgreSQL 15.3"
                />
                <HealthItem 
                  label="Celery Workers"
                  status={health?.celery_status || 'unknown'}
                  details="4 workers active"
                />
                <HealthItem 
                  label="Redis Cache"
                  status="healthy"
                  details="Memory: 45MB / 512MB"
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Subscription Breakdown */}
        <Card className="glass border-white/10">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
                <CreditCard className="w-5 h-5 text-blue-400" />
              </div>
              <CardTitle className="text-white">Subscription Breakdown</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-teal-400" />
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {Object.entries(dashboard?.subscription_breakdown || {}).map(([tier, count], index) => (
                  <div key={tier} className="flex items-center justify-between px-6 py-4 hover:bg-white/5 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${
                        tier === 'enterprise' ? 'bg-purple-400' :
                        tier === 'pro' ? 'bg-blue-400' :
                        tier === 'starter' ? 'bg-teal-400' :
                        'bg-gray-400'
                      }`} />
                      <p className="text-sm font-medium text-white capitalize">{tier}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <p className="text-sm text-gray-400">{count} users</p>
                      <Badge variant="secondary" className="bg-white/5 text-gray-400 border-white/10">
                        {((count / (dashboard?.total_users || 1)) * 100).toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}

function StatCard({
  title,
  value,
  change,
  icon: Icon,
  loading,
  color = 'teal',
}: {
  title: string;
  value: number;
  change: number;
  icon: React.ComponentType<{ className?: string }>;
  loading?: boolean;
  color?: 'teal' | 'emerald' | 'blue' | 'purple';
}) {
  const isPositive = change >= 0;
  const colorClasses = {
    teal: 'from-teal-500/20 to-emerald-500/20 border-teal-500/30 text-teal-400',
    emerald: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400',
  };

  return (
    <Card className="glass border-white/10 hover:border-white/20 transition-all duration-300 group">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]} border group-hover:scale-110 transition-transform`}>
            <Icon className="w-5 h-5" />
          </div>
          {!loading && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-lg ${
              isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
            }`}>
              {isPositive ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span className="text-xs font-medium">{Math.abs(change)}%</span>
            </div>
          )}
        </div>
        <p className="text-sm text-gray-400 mb-1">{title}</p>
        {loading ? (
          <div className="h-8 w-24 bg-white/5 animate-pulse rounded mt-1" />
        ) : (
          <p className="text-3xl font-medium text-white">{formatNumber(value)}</p>
        )}
      </CardContent>
    </Card>
  );
}

function HealthBadge({ status }: { status: string }) {
  const variants = {
    healthy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', icon: CheckCircle },
    degraded: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30', icon: AlertTriangle },
    unhealthy: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30', icon: XCircle },
    unknown: { bg: 'bg-gray-500/10', text: 'text-gray-400', border: 'border-gray-500/30', icon: Activity },
  };
  
  const variant = variants[status as keyof typeof variants] || variants.unknown;
  const Icon = variant.icon;

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-xl ${variant.bg} border ${variant.border}`}>
      <Icon className={`w-4 h-4 ${variant.text}`} />
      <span className={`text-xs font-medium ${variant.text} capitalize`}>{status}</span>
    </div>
  );
}

function HealthItem({ label, status, details }: { label: string; status: string; details?: string }) {
  const variants = {
    healthy: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    degraded: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    unhealthy: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
    unknown: { icon: Activity, color: 'text-gray-400', bg: 'bg-gray-500/10' },
  };
  
  const variant = variants[status as keyof typeof variants] || variants.unknown;
  const Icon = variant.icon;

  return (
    <div className="flex items-center gap-3 p-4 glass rounded-xl border border-white/5 hover:border-white/10 transition-all">
      <div className={`p-2 rounded-lg ${variant.bg}`}>
        <Icon className={`w-4 h-4 ${variant.color}`} />
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-white">{label}</p>
        {details && <p className="text-xs text-gray-400 mt-0.5">{details}</p>}
      </div>
      <Badge variant="secondary" className={`${variant.bg} ${variant.color} border-0 capitalize`}>
        {status}
      </Badge>
    </div>
  );
}
