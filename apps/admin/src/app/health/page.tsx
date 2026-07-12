'use client';

import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useSystemHealth } from '@/hooks/use-admin-api';
import { formatRelativeTime } from '@/lib/utils';
import {
  Activity,
  Server,
  Database,
  Cpu,
  HardDrive,
  Wifi,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Loader2,
  Clock,
  Zap,
  Cloud,
  MemoryStick,
  Network,
} from 'lucide-react';

export default function SystemHealthPage() {
  const { data: health, isLoading, refetch, isRefetching } = useSystemHealth();

  const getOverallStatus = () => {
    if (!health) return 'unknown';
    const statuses = [health.api_status, health.database_status, health.redis_status, health.celery_status];
    if (statuses.some(s => s === 'down')) return 'down';
    if (statuses.some(s => s === 'degraded')) return 'degraded';
    return 'healthy';
  };

  const overallStatus = getOverallStatus();

  return (
    <AdminLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-medium text-white">System Health</h2>
            <p className="text-gray-400 mt-1">Monitor platform services and infrastructure</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isRefetching}
            className="border-white/10 hover:bg-white/5"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-teal-500 mb-4" />
            <p className="text-gray-400">Checking system health...</p>
          </div>
        ) : (
          <>
            {/* Overall Status */}
            <Card className="admin-card overflow-hidden">
              <div className={`h-1 ${
                overallStatus === 'healthy' ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                overallStatus === 'degraded' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                'bg-gradient-to-r from-red-500 to-pink-500'
              }`} />
              <CardContent className="py-8">
                <div className="flex items-center justify-center gap-6">
                  <div className={`p-4 rounded-2xl ${
                    overallStatus === 'healthy' ? 'bg-green-500/10' :
                    overallStatus === 'degraded' ? 'bg-yellow-500/10' :
                    'bg-red-500/10'
                  }`}>
                    <HealthIcon status={overallStatus} size="lg" />
                  </div>
                  <div className="text-center">
                    <h3 className="text-3xl font-medium text-white capitalize">
                      System {overallStatus}
                    </h3>
                    <div className="flex items-center justify-center gap-6 mt-3">
                      <div className="text-center">
                        <p className="text-2xl font-medium text-teal-400">
                          {health?.uptime_seconds ? Math.floor(health.uptime_seconds / 3600) : 0}h
                        </p>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Uptime</p>
                      </div>
                      <div className="w-px h-8 bg-white/10" />
                      <div className="text-center">
                        <p className="text-2xl font-medium text-white">
                          {health?.active_workers || 0}
                        </p>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Workers</p>
                      </div>
                      <div className="w-px h-8 bg-white/10" />
                      <div className="text-center">
                        <p className="text-2xl font-medium text-white">
                          {health?.queue_size || 0}
                        </p>
                        <p className="text-xs text-gray-500 uppercase tracking-wide">Queued</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Services Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <ServiceCard
                name="API Server"
                status={health?.api_status || 'unknown'}
                icon={Server}
                metric={health?.api_latency ? `${health.api_latency}ms` : 'N/A'}
                metricLabel="Latency"
              />
              <ServiceCard
                name="PostgreSQL"
                status={health?.database_status || 'unknown'}
                icon={Database}
                metric={health?.db_connections ? `${health.db_connections}` : 'N/A'}
                metricLabel="Connections"
              />
              <ServiceCard
                name="Redis Cache"
                status={health?.redis_status || 'unknown'}
                icon={Zap}
                metric={health?.redis_memory ? `${health.redis_memory}MB` : 'N/A'}
                metricLabel="Memory"
              />
              <ServiceCard
                name="Celery Workers"
                status={health?.celery_status || 'unknown'}
                icon={Activity}
                metric={health?.active_workers ? `${health.active_workers}` : 'N/A'}
                metricLabel="Active"
              />
            </div>

            {/* System Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Resource Usage */}
              <Card className="admin-card">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-purple-500/10">
                      <Cpu className="w-4 h-4 text-purple-400" />
                    </div>
                    <CardTitle className="text-base font-medium text-white">Resource Usage</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ResourceMeter
                    label="CPU Usage"
                    value={health?.cpu_usage || 0}
                    color="teal"
                  />
                  <ResourceMeter
                    label="Memory Usage"
                    value={health?.memory_usage || 0}
                    color="blue"
                  />
                  <ResourceMeter
                    label="Disk Usage"
                    value={health?.disk_usage || 0}
                    color="purple"
                  />
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="admin-card">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-teal-500/10">
                      <Activity className="w-4 h-4 text-teal-400" />
                    </div>
                    <CardTitle className="text-base font-medium text-white">System Logs</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {health?.recent_logs?.slice(0, 5).map((log: any, i: number) => (
                      <div key={i} className="flex items-start gap-3 py-2 border-b border-white/5 last:border-0">
                        <div className={`w-2 h-2 mt-1.5 rounded-full ${
                          log.level === 'error' ? 'bg-red-400' :
                          log.level === 'warning' ? 'bg-yellow-400' :
                          'bg-green-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white truncate">{log.message}</p>
                          <p className="text-xs text-gray-500">{log.timestamp}</p>
                        </div>
                      </div>
                    )) || (
                      <p className="text-gray-500 text-center py-4">No recent logs</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Infrastructure Details */}
            <Card className="admin-card">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-blue-500/10">
                    <Cloud className="w-4 h-4 text-blue-400" />
                  </div>
                  <CardTitle className="text-base font-medium text-white">Infrastructure</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <InfoItem label="Environment" value={health?.environment || 'production'} />
                  <InfoItem label="Version" value={health?.version || 'v1.0.0'} />
                  <InfoItem label="Region" value={health?.region || 'us-east-1'} />
                  <InfoItem label="Last Deploy" value={health?.last_deploy || 'N/A'} />
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AdminLayout>
  );
}

function ServiceCard({
  name,
  status,
  icon: Icon,
  metric,
  metricLabel,
}: {
  name: string;
  status: string;
  icon: React.ComponentType<{ className?: string }>;
  metric: string;
  metricLabel: string;
}) {
  return (
    <Card className="admin-card group hover:scale-[1.02] transition-all duration-300">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-2.5 rounded-xl ${
            status === 'healthy' ? 'bg-green-500/10' :
            status === 'degraded' ? 'bg-yellow-500/10' :
            status === 'critical' ? 'bg-red-500/10' :
            'bg-gray-500/10'
          }`}>
            <Icon className={`w-5 h-5 ${
              status === 'healthy' ? 'text-green-400' :
              status === 'degraded' ? 'text-yellow-400' :
              status === 'critical' ? 'text-red-400' :
              'text-gray-400'
            }`} />
          </div>
          <HealthBadge status={status} />
        </div>
        <h4 className="font-medium text-white mb-1">{name}</h4>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-medium text-white">{metric}</span>
          <span className="text-xs text-gray-500">{metricLabel}</span>
        </div>
      </CardContent>
    </Card>
  );
}

function HealthBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; dot: string }> = {
    healthy: { bg: 'bg-green-500/10', text: 'text-green-400', dot: 'bg-green-400' },
    degraded: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', dot: 'bg-yellow-400' },
    critical: { bg: 'bg-red-500/10', text: 'text-red-400', dot: 'bg-red-400' },
    unknown: { bg: 'bg-gray-500/10', text: 'text-gray-400', dot: 'bg-gray-400' },
  };

  const c = config[status] || config.unknown;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium ${c.bg} ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot} animate-pulse`} />
      {status}
    </span>
  );
}

function HealthIcon({ status, size = 'md' }: { status: string; size?: 'md' | 'lg' }) {
  const sizeClass = size === 'lg' ? 'w-10 h-10' : 'w-5 h-5';
  
  if (status === 'healthy') {
    return <CheckCircle className={`${sizeClass} text-green-400`} />;
  }
  if (status === 'degraded') {
    return <AlertTriangle className={`${sizeClass} text-yellow-400`} />;
  }
  if (status === 'critical') {
    return <XCircle className={`${sizeClass} text-red-400`} />;
  }
  return <Activity className={`${sizeClass} text-gray-400`} />;
}

function ResourceMeter({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: 'teal' | 'blue' | 'purple';
}) {
  const colorMap = {
    teal: 'bg-teal-500',
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        <span className="text-sm font-medium text-white">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/5 overflow-hidden">
        <div
          className={`h-full ${colorMap[color]} rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center p-4 rounded-xl bg-white/[0.02]">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-sm font-medium text-white">{value}</p>
    </div>
  );
}
