'use client';

import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { useAdminDashboard, useSystemHealth } from '@/hooks/use-admin-api';
import { formatNumber, formatCurrency, formatRelativeTime } from '@/lib/utils';
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
} from 'lucide-react';

export default function AdminDashboardPage() {
  const { data: dashboard, isLoading } = useAdminDashboard();
  const { data: health } = useSystemHealth();

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Users"
            value={dashboard?.total_users || 0}
            change={0}
            icon={Users}
            loading={isLoading}
          />
          <StatCard
            title="Active Users"
            value={dashboard?.active_users || 0}
            change={0}
            icon={Users}
            loading={isLoading}
          />
          <StatCard
            title="Total Datasets"
            value={dashboard?.total_datasets || 0}
            change={0}
            icon={Database}
            loading={isLoading}
          />
          <StatCard
            title="Total Jobs"
            value={dashboard?.total_jobs || 0}
            change={0}
            icon={Play}
            loading={isLoading}
          />
        </div>

        {/* Revenue & System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Overview</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-400">Revenue This Month</p>
                      <p className="text-2xl font-medium text-white">
                        {formatCurrency(dashboard?.revenue_this_month || 0)}
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-gray-700/30 rounded-lg">
                      <p className="text-sm text-gray-400">Rows Generated Today</p>
                      <p className="text-lg font-medium text-white">
                        {formatNumber(dashboard?.rows_generated_today || 0)}
                      </p>
                    </div>
                    <div className="p-3 bg-gray-700/30 rounded-lg">
                      <p className="text-sm text-gray-400">New Users This Week</p>
                      <p className="text-lg font-medium text-white">
                        {formatNumber(dashboard?.new_users_this_week || 0)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* System Health */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>System Health</CardTitle>
              <HealthBadge status={health?.api_status || 'unknown'} />
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <HealthIcon status={health?.api_status || 'unknown'} />
                    <div>
                      <p className="text-sm font-medium text-white">API</p>
                      <p className="text-xs text-gray-400 capitalize">{health?.api_status || 'Unknown'}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <HealthIcon status={health?.database_status || 'unknown'} />
                    <div>
                      <p className="text-sm font-medium text-white">Database</p>
                      <p className="text-xs text-gray-400 capitalize">{health?.database_status || 'Unknown'}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <HealthIcon status={health?.celery_status || 'unknown'} />
                    <div>
                      <p className="text-sm font-medium text-white">Celery</p>
                      <p className="text-xs text-gray-400 capitalize">{health?.celery_status || 'Unknown'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Subscription Breakdown */}
        <div className="grid grid-cols-1 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Subscription Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="divide-y divide-gray-700">
                  {Object.entries(dashboard?.subscription_breakdown || {}).map(([tier, count]) => (
                    <div key={tier} className="flex items-center justify-between px-6 py-3">
                      <p className="text-sm font-medium text-white capitalize">{tier}</p>
                      <p className="text-sm text-gray-400">{count} users</p>
                    </div>
                  ))}\n                </div>
              )}
            </CardContent>
          </Card>
        </div>
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
}: {
  title: string;
  value: number;
  change: number;
  icon: React.ComponentType<{ className?: string }>;
  loading?: boolean;
}) {
  const isPositive = change >= 0;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-400">{title}</p>
            {loading ? (
              <div className="h-8 w-16 bg-gray-700 animate-pulse rounded mt-1" />
            ) : (
              <>
                <p className="text-2xl font-medium text-white mt-1">{formatNumber(value)}</p>
                <div className={`flex items-center gap-1 mt-1 ${
                  isPositive ? 'text-green-400' : 'text-red-400'
                }`}>
                  {isPositive ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span className="text-xs">{Math.abs(change)}% from last month</span>
                </div>
              </>
            )}
          </div>
          <div className="p-2 rounded-lg bg-gray-700">
            <Icon className="w-5 h-5 text-gray-400" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function HealthBadge({ status }: { status: string }) {
  const variants: Record<string, string> = {
    healthy: 'bg-green-500/20 text-green-400',
    degraded: 'bg-yellow-500/20 text-yellow-400',
    down: 'bg-red-500/20 text-red-400',
    unknown: 'bg-gray-500/20 text-gray-400',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded ${variants[status] || variants.unknown}`}>
      {status.toUpperCase()}
    </span>
  );
}

function HealthIcon({ status }: { status: string }) {
  switch (status) {
    case 'healthy':
      return <CheckCircle className="w-4 h-4 text-green-400" />;
    case 'degraded':
      return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
    case 'down':
      return <XCircle className="w-4 h-4 text-red-400" />;
    default:
      return <Activity className="w-4 h-4 text-gray-400" />;
  }
}
