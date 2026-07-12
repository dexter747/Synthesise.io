'use client';

import { useState, useMemo } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useUsage, useDatasets, useJobs } from '@/hooks/use-api';
import { formatNumber, formatDate } from '@/lib/utils';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Zap,
  Database,
  Clock,
  Activity,
  Calendar,
  FileText,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowUpRight,
  BarChart2,
} from 'lucide-react';

type TimeRange = '7d' | '30d' | '90d' | 'all';

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  const { data: usage, isLoading: usageLoading } = useUsage();
  const { data: datasetsData, isLoading: datasetsLoading } = useDatasets();
  const { data: jobsData, isLoading: jobsLoading } = useJobs();
  
  const datasets = datasetsData?.items || [];
  const jobs = jobsData?.items || [];

  // Calculate analytics from real data
  const analytics = useMemo(() => {
    const now = new Date();
    const cutoffDate = new Date();
    
    switch (timeRange) {
      case '7d':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case '30d':
        cutoffDate.setDate(now.getDate() - 30);
        break;
      case '90d':
        cutoffDate.setDate(now.getDate() - 90);
        break;
      default:
        cutoffDate.setFullYear(2000);
    }

    const filteredDatasets = datasets.filter(d => new Date(d.created_at) >= cutoffDate);
    const filteredJobs = jobs.filter(j => new Date(j.created_at) >= cutoffDate);
    
    const completedJobs = filteredJobs.filter(j => j.status === 'completed');
    const failedJobs = filteredJobs.filter(j => j.status === 'failed');
    const pendingJobs = filteredJobs.filter(j => j.status === 'queued' || j.status === 'processing');
    
    const totalRowsGenerated = completedJobs.reduce((sum, j) => sum + (j.rows_generated || 0), 0);
    const avgRowsPerJob = completedJobs.length > 0 ? totalRowsGenerated / completedJobs.length : 0;
    const successRate = filteredJobs.length > 0 
      ? (completedJobs.length / filteredJobs.length) * 100 
      : 100;

    // Group jobs by day for chart data
    const jobsByDay: Record<string, number> = {};
    filteredJobs.forEach(job => {
      const date = new Date(job.created_at).toLocaleDateString();
      jobsByDay[date] = (jobsByDay[date] || 0) + 1;
    });

    return {
      totalDatasets: filteredDatasets.length,
      totalJobs: filteredJobs.length,
      completedJobs: completedJobs.length,
      failedJobs: failedJobs.length,
      pendingJobs: pendingJobs.length,
      totalRowsGenerated,
      avgRowsPerJob: Math.round(avgRowsPerJob),
      successRate: Math.round(successRate),
      jobsByDay,
    };
  }, [datasets, jobs, timeRange]);

  const isLoading = usageLoading || datasetsLoading || jobsLoading;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-medium text-white">Analytics</h1>
            <p className="text-zinc-400 mt-1">Track your data generation activity and usage</p>
          </div>
          <div className="flex items-center gap-2">
            {(['7d', '30d', '90d', 'all'] as TimeRange[]).map((range) => (
              <Button
                key={range}
                variant={timeRange === range ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange(range)}
                className={timeRange === range ? 'bg-teal-500 text-white' : ''}
              >
                {range === 'all' ? 'All Time' : range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
              </Button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
          </div>
        ) : (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                title="Rows Generated"
                value={formatNumber(analytics.totalRowsGenerated)}
                subtitle={`${formatNumber(analytics.avgRowsPerJob)} avg per job`}
                icon={TrendingUp}
                iconColor="text-emerald-400"
                bgColor="from-emerald-500/10 to-teal-500/10"
              />
              <MetricCard
                title="Datasets Created"
                value={analytics.totalDatasets}
                subtitle={`${analytics.pendingJobs} pending`}
                icon={Database}
                iconColor="text-blue-400"
                bgColor="from-blue-500/10 to-cyan-500/10"
              />
              <MetricCard
                title="Jobs Completed"
                value={analytics.completedJobs}
                subtitle={`of ${analytics.totalJobs} total`}
                icon={CheckCircle2}
                iconColor="text-teal-400"
                bgColor="from-teal-500/10 to-emerald-500/10"
              />
              <MetricCard
                title="Success Rate"
                value={`${analytics.successRate}%`}
                subtitle={`${analytics.failedJobs} failed`}
                icon={analytics.successRate >= 90 ? TrendingUp : TrendingDown}
                iconColor={analytics.successRate >= 90 ? 'text-emerald-400' : 'text-orange-400'}
                bgColor={analytics.successRate >= 90 ? 'from-emerald-500/10 to-green-500/10' : 'from-orange-500/10 to-red-500/10'}
              />
            </div>

            {/* Usage Stats */}
            {usage && (
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Activity className="w-5 h-5 text-teal-400" />
                    Monthly Usage
                  </CardTitle>
                  <CardDescription>Your current billing period usage</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <UsageBar
                      label="Rows Generated"
                      current={usage.rows_generated || 0}
                      limit={usage.rows_limit}
                    />
                    <UsageBar
                      label="Datasets"
                      current={usage.datasets_count || 0}
                      limit={usage.datasets_limit}
                    />
                    <UsageBar
                      label="API Calls"
                      current={usage.api_calls || 0}
                      limit={999999}
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Activity Chart (Simple visual) */}
            <Card className="bg-zinc-900/50 border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <BarChart2 className="w-5 h-5 text-teal-400" />
                  Generation Activity
                </CardTitle>
                <CardDescription>Jobs created over time</CardDescription>
              </CardHeader>
              <CardContent>
                {Object.keys(analytics.jobsByDay).length === 0 ? (
                  <div className="text-center py-8 text-zinc-500">
                    No activity in the selected time period
                  </div>
                ) : (
                  <div className="flex items-end gap-1 h-40">
                    {Object.entries(analytics.jobsByDay)
                      .sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
                      .slice(-14)
                      .map(([date, count]) => {
                        const maxCount = Math.max(...Object.values(analytics.jobsByDay));
                        const height = maxCount > 0 ? (count / maxCount) * 100 : 0;
                        return (
                          <div key={date} className="flex-1 flex flex-col items-center group">
                            <div className="relative w-full">
                              <div
                                className="w-full bg-gradient-to-t from-teal-500 to-emerald-500 rounded-t transition-all group-hover:from-teal-400 group-hover:to-emerald-400"
                                style={{ height: `${Math.max(height, 4)}%`, minHeight: '4px' }}
                              />
                              <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-zinc-800 px-2 py-1 rounded text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                {count} jobs
                              </div>
                            </div>
                            <span className="text-[10px] text-zinc-600 mt-1 rotate-45 origin-left">
                              {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            </span>
                          </div>
                        );
                      })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Jobs */}
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Clock className="w-5 h-5 text-teal-400" />
                    Recent Jobs
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {jobs.slice(0, 5).map((job) => (
                    <div key={job.id} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                      <div className={`w-2 h-2 rounded-full ${
                        job.status === 'completed' ? 'bg-emerald-400' :
                        job.status === 'failed' ? 'bg-red-400' :
                        job.status === 'processing' ? 'bg-blue-400 animate-pulse' :
                        'bg-yellow-400'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white truncate">
                          {job.dataset?.name || 'Unnamed Dataset'}
                        </p>
                        <p className="text-xs text-zinc-500">
                          {formatNumber(job.rows_generated || 0)} rows • {formatDate(job.created_at)}
                        </p>
                      </div>
                      <Badge variant={
                        job.status === 'completed' ? 'success' :
                        job.status === 'failed' ? 'error' :
                        'default'
                      } className="text-xs">
                        {job.status}
                      </Badge>
                    </div>
                  ))}
                  {jobs.length === 0 && (
                    <p className="text-center text-zinc-500 py-4">No jobs yet</p>
                  )}
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Zap className="w-5 h-5 text-teal-400" />
                    Quick Stats
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <StatRow
                    label="Most Active Day"
                    value={Object.entries(analytics.jobsByDay)
                      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'}
                    icon={Calendar}
                  />
                  <StatRow
                    label="Average Job Size"
                    value={`${formatNumber(analytics.avgRowsPerJob)} rows`}
                    icon={FileText}
                  />
                  <StatRow
                    label="Total Datasets"
                    value={formatNumber(datasets.length)}
                    icon={Database}
                  />
                  <StatRow
                    label="Jobs in Queue"
                    value={formatNumber(analytics.pendingJobs)}
                    icon={Clock}
                  />
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconColor,
  bgColor,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
  bgColor: string;
}) {
  return (
    <Card className="bg-zinc-900/50 border-white/10 overflow-hidden">
      <CardContent className="p-6 relative">
        <div className={`absolute inset-0 bg-gradient-to-br ${bgColor} opacity-50`} />
        <div className="relative">
          <div className="flex items-center justify-between">
            <Icon className={`w-8 h-8 ${iconColor}`} />
            <ArrowUpRight className="w-4 h-4 text-zinc-500" />
          </div>
          <div className="mt-4">
            <p className="text-3xl font-medium text-white">{value}</p>
            <p className="text-sm text-zinc-400 mt-1">{title}</p>
            <p className="text-xs text-zinc-500 mt-1">{subtitle}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function UsageBar({
  label,
  current,
  limit,
}: {
  label: string;
  current: number;
  limit?: number;
}) {
  const percentage = limit ? Math.min((current / limit) * 100, 100) : 0;
  const isNearLimit = percentage > 80;
  const isOverLimit = percentage >= 100;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-zinc-400">{label}</span>
        <span className="text-sm text-white">
          {formatNumber(current)}
          {limit && <span className="text-zinc-500"> / {formatNumber(limit)}</span>}
        </span>
      </div>
      {limit && (
        <div className="w-full bg-zinc-800 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              isOverLimit ? 'bg-red-500' :
              isNearLimit ? 'bg-yellow-500' :
              'bg-gradient-to-r from-teal-500 to-emerald-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
    </div>
  );
}

function StatRow({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
      <div className="flex items-center gap-3">
        <Icon className="w-4 h-4 text-zinc-500" />
        <span className="text-sm text-zinc-400">{label}</span>
      </div>
      <span className="text-sm font-medium text-white">{value}</span>
    </div>
  );
}
