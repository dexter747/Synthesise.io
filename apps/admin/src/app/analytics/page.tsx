'use client';

import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAdminAnalytics } from '@/hooks/use-admin-api';
import { formatNumber, formatCurrency } from '@/lib/utils';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Database,
  Play,
  DollarSign,
  Loader2,
  Download,
  Calendar,
  BarChart3,
  ArrowUpRight,
  RefreshCw,
  Zap,
  Activity,
} from 'lucide-react';
import { useState } from 'react';

const TIME_RANGES = [
  { label: '7 Days', value: 'week' as const },
  { label: '30 Days', value: 'month' as const },
  { label: '90 Days', value: 'month' as const },
  { label: 'Year', value: 'year' as const },
];

// Helper to calculate percentage change from time series data
function calculateChange(data: Array<{ date: string; value: number }> | undefined): number | undefined {
  if (!data || data.length < 2) return undefined;
  
  const latestValue = data[data.length - 1].value;
  const previousValue = data[data.length - 2].value;
  
  if (previousValue === 0) return latestValue > 0 ? 100 : 0;
  
  return Math.round(((latestValue - previousValue) / previousValue) * 100);
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month' | 'year'>('month');
  const { data: analytics, isLoading, refetch } = useAdminAnalytics(timeRange);

  return (
    <AdminLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium text-white">Analytics Dashboard</h1>
            <p className="text-gray-400 mt-1">Platform metrics and growth insights</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex bg-white/[0.03] rounded-xl p-1 border border-white/10">
              {TIME_RANGES.map((range) => (
                <button
                  key={range.label}
                  onClick={() => setTimeRange(range.value)}
                  className={`px-4 py-2 text-sm rounded-lg transition-all duration-200 ${
                    timeRange === range.value
                      ? 'bg-teal-500 text-white shadow-lg shadow-teal-500/25'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {range.label}
                </button>
              ))}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="border-white/10 hover:bg-white/5"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="border-white/10 hover:bg-white/5"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-teal-500 mb-4" />
            <p className="text-gray-400">Loading analytics...</p>
          </div>
        ) : (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                title="User Growth"
                value={formatNumber(analytics?.user_growth?.[analytics.user_growth.length - 1]?.value || 0)}
                change={calculateChange(analytics?.user_growth)}
                icon={Users}
                color="teal"
              />
              <MetricCard
                title="Jobs Today"
                value={formatNumber(analytics?.jobs_per_day?.[analytics.jobs_per_day.length - 1]?.value || 0)}
                change={calculateChange(analytics?.jobs_per_day)}
                icon={Play}
                color="blue"
              />
              <MetricCard
                title="Rows Generated"
                value={formatNumber(analytics?.rows_generated_per_day?.[analytics.rows_generated_per_day.length - 1]?.value || 0)}
                change={calculateChange(analytics?.rows_generated_per_day)}
                icon={Database}
                color="purple"
              />
              <MetricCard
                title="Revenue"
                value={formatCurrency(analytics?.revenue_trend?.[analytics.revenue_trend.length - 1]?.value || 0)}
                change={calculateChange(analytics?.revenue_trend)}
                icon={DollarSign}
                color="amber"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* User Growth */}
              <Card className="admin-card">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-teal-500/10">
                        <Users className="w-4 h-4 text-teal-400" />
                      </div>
                      <CardTitle className="text-base font-medium text-white">User Growth</CardTitle>
                    </div>
                    {calculateChange(analytics?.user_growth) !== undefined && (
                      <span className="text-xs text-teal-400 flex items-center gap-1">
                        {calculateChange(analytics?.user_growth)! >= 0 ? (
                          <TrendingUp className="w-3 h-3" />
                        ) : (
                          <TrendingDown className="w-3 h-3" />
                        )}
                        {calculateChange(analytics?.user_growth)! >= 0 ? '+' : ''}{calculateChange(analytics?.user_growth)}%
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <SimpleBarChart data={analytics?.user_growth || []} color="teal" />
                  </div>
                </CardContent>
              </Card>

              {/* Revenue Trend */}
              <Card className="admin-card">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-green-500/10">
                        <DollarSign className="w-4 h-4 text-green-400" />
                      </div>
                      <CardTitle className="text-base font-medium text-white">Revenue Trend</CardTitle>
                    </div>
                    <span className="text-xs text-green-400 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" /> +23.8%
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <SimpleBarChart data={analytics?.revenue_trend || []} color="green" format="currency" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Additional Stats & Users */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Platform Stats */}
              <Card className="admin-card">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-purple-500/10">
                      <Activity className="w-4 h-4 text-purple-400" />
                    </div>
                    <CardTitle className="text-base font-medium text-white">Platform Activity</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <StatRow 
                    label="Total Users" 
                    value={formatNumber(analytics?.user_growth?.[analytics.user_growth.length - 1]?.value || 0)} 
                  />
                  <StatRow 
                    label="Jobs Today" 
                    value={formatNumber(analytics?.jobs_per_day?.[analytics.jobs_per_day.length - 1]?.value || 0)} 
                  />
                  <StatRow 
                    label="Rows Generated Today" 
                    value={formatNumber(analytics?.rows_generated_per_day?.[analytics.rows_generated_per_day.length - 1]?.value || 0)} 
                  />
                  <StatRow 
                    label="Revenue Today" 
                    value={formatCurrency(analytics?.revenue_trend?.[analytics.revenue_trend.length - 1]?.value || 0)} 
                  />
                  <StatRow 
                    label="Active Users" 
                    value={formatNumber(analytics?.top_users?.length || 0)} 
                  />
                </CardContent>
              </Card>

              {/* Most Active Users - spans 2 columns */}
              <Card className="admin-card lg:col-span-2">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-blue-500/10">
                        <Zap className="w-4 h-4 text-blue-400" />
                      </div>
                      <CardTitle className="text-base font-medium text-white">Most Active Users</CardTitle>
                    </div>
                    <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                      View All
                      <ArrowUpRight className="w-3 h-3 ml-1" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-white/5">
                    {analytics?.top_users?.slice(0, 5).map((user: any, i: number) => (
                      <div
                        key={user.id}
                        className="flex items-center gap-4 px-6 py-3 hover:bg-white/[0.02] transition-colors"
                      >
                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                          i === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                          i === 1 ? 'bg-gray-400/20 text-gray-400' :
                          i === 2 ? 'bg-amber-600/20 text-amber-500' :
                          'bg-white/5 text-gray-500'
                        }`}>
                          {i + 1}
                        </span>
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-400 to-cyan-500 flex items-center justify-center text-white text-sm font-medium shadow-lg">
                          {user.name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">{user.name}</p>
                          <p className="text-xs text-gray-500 truncate">{user.email}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-white">{formatNumber(user.datasets_count)}</p>
                          <p className="text-xs text-gray-500">datasets</p>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center py-12 text-gray-400">No user data available</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}

function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  color = 'teal',
}: {
  title: string;
  value: string;
  change?: number;
  icon: React.ComponentType<{ className?: string }>;
  color?: 'teal' | 'blue' | 'purple' | 'amber';
}) {
  const isPositive = change !== undefined ? change >= 0 : true;
  
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
            <p className="text-2xl font-medium text-white">{value}</p>
            {change !== undefined && (
              <div
                className={`flex items-center gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}
              >
                {isPositive ? (
                  <TrendingUp className="w-3.5 h-3.5" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5" />
                )}
                <span className="text-xs">{Math.abs(change)}% vs last period</span>
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

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
      <span className="text-sm text-gray-400">{label}</span>
      <span className="text-sm font-medium text-white">{value}</span>
    </div>
  );
}

function SimpleBarChart({
  data,
  color = 'teal',
  format,
}: {
  data: Array<{ date: string; value: number }>;
  color?: 'teal' | 'green' | 'blue' | 'purple';
  format?: 'currency' | 'number';
}) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  const maxValue = Math.max(...data.map((d) => d.value));
  
  const gradientMap = {
    teal: 'from-teal-500 to-cyan-400',
    green: 'from-green-500 to-emerald-400',
    blue: 'from-blue-500 to-indigo-400',
    purple: 'from-purple-500 to-pink-400',
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex-1 flex items-end gap-2 pb-2">
        {data.map((item, i) => {
          const height = maxValue > 0 ? (item.value / maxValue) * 100 : 0;
          return (
            <div key={i} className="flex-1 flex flex-col items-center gap-1 group">
              <div className="relative w-full flex-1 flex items-end">
                {/* Tooltip */}
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity
                  bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                  {format === 'currency' ? formatCurrency(item.value) : formatNumber(item.value)}
                </div>
                <div
                  className={`w-full bg-gradient-to-t ${gradientMap[color]} rounded-t-lg transition-all duration-300
                    group-hover:opacity-80`}
                  style={{ height: `${Math.max(height, 5)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex gap-2 pt-2 border-t border-white/5">
        {data.map((item, i) => (
          <span key={i} className="flex-1 text-center text-[10px] text-gray-500 truncate">
            {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </span>
        ))}
      </div>
    </div>
  );
}
