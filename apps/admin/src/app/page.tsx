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
  ArrowDownRight,
  Clock,
  RefreshCw,
  Eye,
  Download,
  UserPlus,
  FileSpreadsheet,
  Server,
  HardDrive,
  Cpu,
  MemoryStick,
  Gauge,
  CircleDot,
} from 'lucide-react';

// Temporary mock data until API provides this
interface ActivityItem {
  id: number;
  type: string;
  user: string;
  time: string;
  icon: any;
  color: string;
}

interface JobQueueItem {
  id: string;
  status: string;
  progress: number;
  rows: number;
  started: string;
}

const recentActivity: ActivityItem[] = [
  { id: 1, type: 'user_signup', user: 'Recent user', time: '2 min ago', icon: UserPlus, color: 'teal' },
  { id: 2, type: 'dataset_created', user: 'New dataset', time: '5 min ago', icon: FileSpreadsheet, color: 'blue' },
];

const jobQueue: JobQueueItem[] = [
  { id: 'JOB-001', status: 'processing', progress: 67, rows: 50000, started: '2 min ago' },
];

export default function AdminDashboardPage() {
  const { data: dashboard, isLoading, refetch } = useAdminDashboard();
  const { data: health } = useSystemHealth();

  return (
    <AdminLayout>
      <div className="space-y-8 animate-fade-in">
        {/* Welcome Header */}
        <div className="page-header">
          <div>
            <h2 className="page-title">
              <span className="gradient-teal-text">Dashboard Overview</span>
            </h2>
            <p className="page-subtitle">Monitor your platform's performance and metrics in real-time</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <div className="flex items-center gap-2 px-4 py-3 glass rounded-xl border border-teal-500/20">
              <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-gray-300">Live Data</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={dashboard?.total_users || 0}
            change={dashboard?.users_change_pct || 0}
            icon={Users}
            loading={isLoading}
            color="teal"
            subtitle="Platform users"
          />
          <StatCard
            title="Active Users"
            value={dashboard?.active_users || 0}
            change={dashboard?.active_users_change_pct || 0}
            icon={Zap}
            loading={isLoading}
            color="emerald"
            subtitle="Last 30 days"
          />
          <StatCard
            title="Total Datasets"
            value={dashboard?.total_datasets || 0}
            change={dashboard?.datasets_change_pct || 0}
            icon={Database}
            loading={isLoading}
            color="blue"
            subtitle="Generated data"
          />
          <StatCard
            title="Total Jobs"
            value={dashboard?.total_jobs || 0}
            change={dashboard?.jobs_change_pct || 0}
            icon={Play}
            loading={isLoading}
            color="purple"
            subtitle="Processed jobs"
          />
        </div>

        {/* Revenue & System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Revenue - Takes 2 columns */}
          <div className="lg:col-span-2">
            <Card className="admin-card-hover h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30">
                      <DollarSign className="w-5 h-5 text-teal-400" />
                    </div>
                    <div>
                      <CardTitle className="text-white">Revenue Overview</CardTitle>
                      <p className="text-xs text-gray-500 mt-0.5">Monthly recurring revenue</p>
                    </div>
                  </div>
                  <select className="appearance-none px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 transition-all duration-200">
                    <option className="bg-gray-900">This Month</option>
                    <option className="bg-gray-900">Last Month</option>
                    <option className="bg-gray-900">Last 3 Months</option>
                  </select>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-teal-400" />
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Main Revenue Card */}
                    <div className="p-6 rounded-2xl bg-gradient-to-br from-teal-500/10 via-emerald-500/5 to-transparent border border-teal-500/20">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-sm text-gray-400 mb-2">Revenue This Month</p>
                          <p className="text-5xl font-medium gradient-teal-text">
                            {formatCurrency(dashboard?.revenue_this_month || 0)}
                          </p>
                          <div className="flex items-center gap-2 mt-3">
                            <div className={`flex items-center gap-1 px-2.5 py-1 rounded-lg ${
                              (dashboard?.revenue_change_pct || 0) >= 0 
                                ? 'bg-emerald-500/10 text-emerald-400' 
                                : 'bg-red-500/10 text-red-400'
                            }`}>
                              <TrendingUp className="w-4 h-4" />
                              <span className="text-sm font-medium">
                                {(dashboard?.revenue_change_pct || 0) >= 0 ? '+' : ''}{(dashboard?.revenue_change_pct || 0).toFixed(1)}%
                              </span>
                            </div>
                            <span className="text-xs text-gray-500">vs last month</span>
                          </div>
                        </div>
                        <div className="p-4 rounded-2xl bg-teal-500/10 border border-teal-500/20">
                          <ArrowUpRight className="w-8 h-8 text-teal-400" />
                        </div>
                      </div>
                    </div>
                    
                    {/* Revenue Stats Grid */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-4 glass rounded-xl border border-white/5 hover:border-white/10 transition-all">
                        <p className="text-xs text-gray-400 mb-2">Rows Generated</p>
                        <p className="text-2xl font-medium text-white">
                          {formatNumber(dashboard?.rows_generated_today || 0)}
                        </p>
                        <div className="flex items-center gap-1 mt-1.5">
                          <TrendingUp className={`w-3 h-3 ${(dashboard?.rows_generated_change_pct || 0) >= 0 ? 'text-teal-400' : 'text-red-400'}`} />
                          <span className={`text-xs ${(dashboard?.rows_generated_change_pct || 0) >= 0 ? 'text-teal-400' : 'text-red-400'}`}>
                            {(dashboard?.rows_generated_change_pct || 0) >= 0 ? '+' : ''}{(dashboard?.rows_generated_change_pct || 0).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="p-4 glass rounded-xl border border-white/5 hover:border-white/10 transition-all">
                        <p className="text-xs text-gray-400 mb-2">New Users This Week</p>
                        <p className="text-2xl font-medium text-white">
                          {formatNumber(dashboard?.new_users_this_week || 0)}
                        </p>
                        <div className="flex items-center gap-1 mt-1.5">
                          <TrendingUp className={`w-3 h-3 ${(dashboard?.new_users_week_change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`} />
                          <span className={`text-xs ${(dashboard?.new_users_week_change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {(dashboard?.new_users_week_change_pct || 0) >= 0 ? '+' : ''}{(dashboard?.new_users_week_change_pct || 0).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="p-4 glass rounded-xl border border-white/5 hover:border-white/10 transition-all">
                        <p className="text-xs text-gray-400 mb-2">Avg Job Size</p>
                        <p className="text-2xl font-medium text-white">
                          {formatNumber(dashboard?.avg_job_size || 0)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1.5">rows per job</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* System Health */}
          <Card className="admin-card-hover">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30">
                    <Activity className="w-5 h-5 text-emerald-400" />
                  </div>
                  <CardTitle className="text-white">System Health</CardTitle>
                </div>
                <HealthBadge status={health?.status || 'unknown'} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <HealthItem 
                  label="API Server"
                  status={health?.status || 'unknown'}
                  details={`Status: ${health?.status || 'unknown'}`}
                  icon={Server}
                />
                <HealthItem 
                  label="Database"
                  status={health?.database || 'unknown'}
                  details={`Status: ${health?.database || 'unknown'}`}
                  icon={Database}
                />
                <HealthItem 
                  label="Celery Workers"
                  status={health?.celery || 'unknown'}
                  details={`${health?.active_workers || 0} workers active`}
                  icon={Cpu}
                />
                <HealthItem 
                  label="Redis Cache"
                  status={health?.redis || 'unknown'}
                  details={`Status: ${health?.redis || 'unknown'}`}
                  icon={HardDrive}
                />
              </div>
              
              {/* Resource Usage */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-4">Resource Usage</p>
                <div className="space-y-4">
                  <ResourceBar label="CPU" value={health?.cpu_usage_percent || 0} />
                  <ResourceBar label="Memory" value={health?.memory_usage_percent || 0} />
                  <ResourceBar label="Storage" value={health?.disk_usage_percent || 0} />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Activity Feed & Job Queue */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activity */}
          <Card className="admin-card-hover">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
                    <Clock className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <CardTitle className="text-white">Recent Activity</CardTitle>
                    <p className="text-xs text-gray-500 mt-0.5">Platform events feed</p>
                  </div>
                </div>
                <button className="text-xs text-teal-400 hover:text-teal-300 transition-colors">
                  View All
                </button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-white/5">
                {recentActivity.map((activity, index) => (
                  <ActivityItem key={activity.id} activity={activity} index={index} />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Job Queue */}
          <Card className="admin-card-hover">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30">
                    <Zap className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <CardTitle className="text-white">Active Jobs</CardTitle>
                    <p className="text-xs text-gray-500 mt-0.5">Processing queue status</p>
                  </div>
                </div>
                <Badge className="badge-teal">
                  {jobQueue.filter(j => j.status === 'processing').length} Active
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-white/5">
                {jobQueue.map((job) => (
                  <JobItem key={job.id} job={job} />
                ))}
              </div>
              <div className="p-4 bg-white/[0.02]">
                <button className="w-full btn-secondary text-sm py-2">
                  View Job Queue
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Subscription Breakdown */}
        <Card className="admin-card-hover">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                  <CreditCard className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <CardTitle className="text-white">Subscription Distribution</CardTitle>
                  <p className="text-xs text-gray-500 mt-0.5">Users by subscription tier</p>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-teal-400" />
              </div>
            ) : dashboard?.subscription_breakdown ? (
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {[
                  { tier: 'free', color: 'gray' },
                  { tier: 'starter', color: 'teal' },
                  { tier: 'professional', color: 'blue' },
                  { tier: 'business', color: 'purple' },
                  { tier: 'enterprise', color: 'amber' },
                ].map((sub) => (
                  <SubscriptionCard 
                    key={sub.tier} 
                    tier={sub.tier}
                    count={dashboard.subscription_breakdown[sub.tier as keyof typeof dashboard.subscription_breakdown] || 0}
                    color={sub.color}
                    totalUsers={dashboard?.total_users || 0} 
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">No subscription data available</div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}

// ============================================
// COMPONENTS
// ============================================

function StatCard({
  title,
  value,
  change,
  icon: Icon,
  loading,
  color = 'teal',
  subtitle,
}: {
  title: string;
  value: number;
  change: number;
  icon: React.ComponentType<{ className?: string }>;
  loading?: boolean;
  color?: 'teal' | 'emerald' | 'blue' | 'purple';
  subtitle?: string;
}) {
  const isPositive = change >= 0;
  const colorClasses = {
    teal: 'from-teal-500/20 to-emerald-500/20 border-teal-500/30 text-teal-400',
    emerald: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400',
  };

  return (
    <Card className="admin-card-hover group">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]} border group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="w-5 h-5" />
          </div>
          {!loading && (
            <div className={`flex items-center gap-1 px-2.5 py-1 rounded-lg ${
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
          <div className="h-9 w-28 bg-white/5 animate-pulse rounded mt-1" />
        ) : (
          <p className="text-3xl font-medium text-white">{formatNumber(value)}</p>
        )}
        {subtitle && <p className="text-xs text-gray-500 mt-2">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}

function HealthBadge({ status }: { status: string }) {
  const variants: Record<string, { bg: string; text: string; border: string; icon: typeof CheckCircle }> = {
    healthy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', icon: CheckCircle },
    degraded: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30', icon: AlertTriangle },
    unhealthy: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30', icon: XCircle },
    unknown: { bg: 'bg-gray-500/10', text: 'text-gray-400', border: 'border-gray-500/30', icon: Activity },
  };
  
  const variant = variants[status] || variants.unknown;
  const Icon = variant.icon;

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl ${variant.bg} border ${variant.border}`}>
      <Icon className={`w-3.5 h-3.5 ${variant.text}`} />
      <span className={`text-xs font-medium ${variant.text} capitalize`}>{status}</span>
    </div>
  );
}

function HealthItem({ 
  label, 
  status, 
  details, 
  icon: Icon 
}: { 
  label: string; 
  status: string; 
  details?: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const variants: Record<string, { iconColor: string; bg: string }> = {
    healthy: { iconColor: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    degraded: { iconColor: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    unhealthy: { iconColor: 'text-red-400', bg: 'bg-red-500/10' },
    unknown: { iconColor: 'text-gray-400', bg: 'bg-gray-500/10' },
  };
  
  const variant = variants[status] || variants.unknown;

  return (
    <div className="flex items-center gap-3 p-3 glass rounded-xl border border-white/5 hover:border-white/10 transition-all group">
      <div className={`p-2 rounded-lg ${variant.bg}`}>
        <Icon className={`w-4 h-4 ${variant.iconColor}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white">{label}</p>
        {details && <p className="text-xs text-gray-500 mt-0.5">{details}</p>}
      </div>
      <div className={`w-2 h-2 rounded-full ${
        status === 'healthy' ? 'bg-emerald-400' :
        status === 'degraded' ? 'bg-yellow-400' :
        status === 'unhealthy' ? 'bg-red-400' : 'bg-gray-400'
      } ${status === 'healthy' ? 'animate-pulse' : ''}`} />
    </div>
  );
}

function ResourceBar({ label, value }: { label: string; value: number }) {
  const getColor = (v: number) => {
    if (v < 50) return 'bg-emerald-500';
    if (v < 80) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-xs font-medium text-white">{value}%</span>
      </div>
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div 
          className={`h-full ${getColor(value)} rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function ActivityItem({ activity, index }: { activity: typeof recentActivity[0]; index: number }) {
  const colorMap: Record<string, string> = {
    teal: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  };
  
  const Icon = activity.icon;
  
  return (
    <div 
      className="flex items-center gap-4 px-6 py-4 hover:bg-white/[0.03] transition-all cursor-pointer"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className={`p-2.5 rounded-xl border ${colorMap[activity.color]}`}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-white truncate">{activity.user}</p>
        <p className="text-xs text-gray-500 mt-0.5 capitalize">{activity.type.replace('_', ' ')}</p>
      </div>
      <span className="text-xs text-gray-500 whitespace-nowrap">{activity.time}</span>
    </div>
  );
}

function JobItem({ job }: { job: typeof jobQueue[0] }) {
  return (
    <div className="px-6 py-4 hover:bg-white/[0.03] transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-sm font-mono text-white">{job.id}</span>
          <Badge className={job.status === 'processing' ? 'badge-emerald' : 'badge-amber'}>
            {job.status}
          </Badge>
        </div>
        <span className="text-xs text-gray-500">{formatNumber(job.rows)} rows</span>
      </div>
      {job.status === 'processing' && (
        <div className="space-y-2">
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-teal-500 to-emerald-500 rounded-full transition-all duration-500"
              style={{ width: `${job.progress}%` }}
            />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Started {job.started}</span>
            <span className="text-xs font-medium text-teal-400">{job.progress}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

function SubscriptionCard({ 
  tier, 
  count, 
  color, 
  totalUsers 
}: { 
  tier: string; 
  count: number; 
  color: string; 
  totalUsers: number;
}) {
  const colorMap: Record<string, { bg: string; border: string; text: string; dot: string }> = {
    gray: { bg: 'from-gray-500/10 to-gray-600/10', border: 'border-gray-500/30', text: 'text-gray-400', dot: 'bg-gray-400' },
    teal: { bg: 'from-teal-500/10 to-emerald-500/10', border: 'border-teal-500/30', text: 'text-teal-400', dot: 'bg-teal-400' },
    blue: { bg: 'from-blue-500/10 to-cyan-500/10', border: 'border-blue-500/30', text: 'text-blue-400', dot: 'bg-blue-400' },
    purple: { bg: 'from-purple-500/10 to-pink-500/10', border: 'border-purple-500/30', text: 'text-purple-400', dot: 'bg-purple-400' },
    amber: { bg: 'from-amber-500/10 to-orange-500/10', border: 'border-amber-500/30', text: 'text-amber-400', dot: 'bg-amber-400' },
  };
  
  const colors = colorMap[color] || colorMap.gray;
  const percentage = totalUsers > 0 ? ((count / totalUsers) * 100).toFixed(1) : '0.0';
  
  return (
    <div className={`p-5 rounded-xl bg-gradient-to-br ${colors.bg} border ${colors.border} hover:scale-[1.02] transition-all duration-300 cursor-default`}>
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-3 h-3 rounded-full ${colors.dot}`} />
        <span className="text-sm font-medium text-white capitalize">{tier}</span>
      </div>
      <p className="text-3xl font-medium text-white">{formatNumber(count)}</p>
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-500">{percentage}% of total</span>
        <span className={`text-xs font-medium ${colors.text}`}>{count} user{count !== 1 ? 's' : ''}</span>
      </div>
    </div>
  );
}
