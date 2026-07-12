'use client';

import { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useSystemHealth, useServerLogs, useAdminJobs } from '@/hooks/use-admin-api';
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
  MemoryStick,
  LineChart,
  BarChart3,
  AlertCircle,
  Filter,
  Search,
  Bell,
  BellRing,
  TrendingUp,
  TrendingDown,
  Minus,
  Container,
  Box,
  Terminal,
  Eye,
  Download,
  ArrowRight,
  Layers,
  Gauge,
} from 'lucide-react';

// Types for monitoring data
interface MetricPoint {
  timestamp: string;
  value: number;
}

interface Alert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  service: string;
  timestamp: string;
  acknowledged: boolean;
}

interface ContainerHealth {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'unhealthy';
  cpu: number;
  memory: number;
  uptime: string;
}

// Mock data for demonstration
const mockAlerts: Alert[] = [
  {
    id: '1',
    severity: 'warning',
    title: 'High Memory Usage',
    message: 'Redis memory usage is above 80%',
    service: 'redis',
    timestamp: '2024-01-15T10:30:00Z',
    acknowledged: false,
  },
  {
    id: '2',
    severity: 'info',
    title: 'Job Queue Backlog',
    message: '15 jobs waiting in queue for > 5 minutes',
    service: 'celery',
    timestamp: '2024-01-15T10:25:00Z',
    acknowledged: true,
  },
];

const mockContainers: ContainerHealth[] = [
  { id: '1', name: 'api', status: 'running', cpu: 23, memory: 45, uptime: '5d 12h' },
  { id: '2', name: 'celery-worker', status: 'running', cpu: 78, memory: 62, uptime: '5d 12h' },
  { id: '3', name: 'postgres', status: 'running', cpu: 12, memory: 38, uptime: '5d 12h' },
  { id: '4', name: 'redis', status: 'running', cpu: 5, memory: 81, uptime: '5d 12h' },
  { id: '5', name: 'nginx', status: 'running', cpu: 2, memory: 15, uptime: '5d 12h' },
];

// Generate mock metric history for charts
const generateMetricHistory = (base: number, variance: number): MetricPoint[] => {
  const points: MetricPoint[] = [];
  const now = Date.now();
  for (let i = 30; i >= 0; i--) {
    points.push({
      timestamp: new Date(now - i * 60000).toISOString(),
      value: Math.max(0, Math.min(100, base + (Math.random() - 0.5) * variance)),
    });
  }
  return points;
};

export default function MonitoringPage() {
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useSystemHealth();
  const { data: logs } = useServerLogs({ limit: 10 });
  const { data: jobs } = useAdminJobs({ per_page: 10 });
  
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const [containers] = useState<ContainerHealth[]>(mockContainers);
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'alerts' | 'containers' | 'logs'>('overview');
  const [logFilter, setLogFilter] = useState({ level: 'all', search: '' });
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Simulated metrics history
  const [cpuHistory] = useState(() => generateMetricHistory(45, 30));
  const [memoryHistory] = useState(() => generateMetricHistory(60, 20));
  const [requestHistory] = useState(() => generateMetricHistory(75, 40));

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      refetchHealth();
    }, 10000);
    return () => clearInterval(interval);
  }, [autoRefresh, refetchHealth]);

  const acknowledgeAlert = (alertId: string) => {
    setAlerts(alerts.map(a => a.id === alertId ? { ...a, acknowledged: true } : a));
  };

  const unacknowledgedCount = alerts.filter(a => !a.acknowledged).length;

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-medium text-white flex items-center gap-3">
              <Gauge className="w-7 h-7 text-teal-400" />
              System Monitoring
            </h2>
            <p className="text-gray-400 mt-1">Real-time infrastructure metrics and alerts</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
                autoRefresh 
                  ? 'bg-teal-500/10 border-teal-500/30 text-teal-400' 
                  : 'bg-white/5 border-white/10 text-gray-400'
              }`}
            >
              <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              Auto-refresh
            </button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetchHealth()}
              className="border-white/10 hover:bg-white/5"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 p-1 bg-white/5 rounded-xl w-fit">
          {[
            { key: 'overview', label: 'Overview', icon: Activity },
            { key: 'metrics', label: 'Metrics', icon: LineChart },
            { key: 'alerts', label: 'Alerts', icon: Bell, badge: unacknowledgedCount },
            { key: 'containers', label: 'Containers', icon: Container },
            { key: 'logs', label: 'Logs', icon: Terminal },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.key
                  ? 'bg-white/10 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
              {tab.badge ? (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-red-500 text-white rounded-full">
                  {tab.badge}
                </span>
              ) : null}
            </button>
          ))}
        </div>

        {healthLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-teal-500 mb-4" />
            <p className="text-gray-400">Loading monitoring data...</p>
          </div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Quick Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <QuickStatCard
                    title="API Latency"
                    value={health?.api_latency || 45}
                    unit="ms"
                    trend="down"
                    trendValue="-12%"
                    icon={Zap}
                    color="teal"
                  />
                  <QuickStatCard
                    title="Requests/min"
                    value={health?.requests_per_minute || 1234}
                    unit=""
                    trend="up"
                    trendValue="+8%"
                    icon={Activity}
                    color="blue"
                  />
                  <QuickStatCard
                    title="Error Rate"
                    value={health?.error_rate || 0.12}
                    unit="%"
                    trend="down"
                    trendValue="-0.05%"
                    icon={AlertCircle}
                    color="green"
                  />
                  <QuickStatCard
                    title="Queue Depth"
                    value={health?.queue_size || 23}
                    unit=""
                    trend="neutral"
                    trendValue="0"
                    icon={Layers}
                    color="purple"
                  />
                </div>

                {/* Service Status Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <ServiceStatusCard
                    name="API Server"
                    status={health?.api_status || 'healthy'}
                    metrics={{
                      'Response Time': `${health?.api_latency || 45}ms`,
                      'Uptime': '99.99%',
                      'Active Connections': '234',
                    }}
                    icon={Server}
                  />
                  <ServiceStatusCard
                    name="PostgreSQL"
                    status={health?.database_status || 'healthy'}
                    metrics={{
                      'Active Queries': `${health?.db_connections || 15}`,
                      'Connections': '45/100',
                      'Cache Hit': '98.5%',
                    }}
                    icon={Database}
                  />
                  <ServiceStatusCard
                    name="Redis"
                    status={health?.redis_status || 'healthy'}
                    metrics={{
                      'Memory': `${health?.redis_memory || 256}MB`,
                      'Keys': '12,456',
                      'Hit Rate': '94.2%',
                    }}
                    icon={Zap}
                  />
                  <ServiceStatusCard
                    name="Celery"
                    status={health?.celery_status || 'healthy'}
                    metrics={{
                      'Workers': `${health?.active_workers || 4}`,
                      'Queue': `${health?.queue_size || 23}`,
                      'Processed/h': '1,234',
                    }}
                    icon={Activity}
                  />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <MiniChart
                    title="CPU Usage"
                    data={cpuHistory}
                    currentValue={health?.cpu_usage || 45}
                    unit="%"
                    color="teal"
                  />
                  <MiniChart
                    title="Memory Usage"
                    data={memoryHistory}
                    currentValue={health?.memory_usage || 62}
                    unit="%"
                    color="blue"
                  />
                </div>

                {/* Recent Alerts */}
                {alerts.filter(a => !a.acknowledged).length > 0 && (
                  <Card className="admin-card border-amber-500/30">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base font-medium text-white flex items-center gap-2">
                          <BellRing className="w-4 h-4 text-amber-400" />
                          Active Alerts
                        </CardTitle>
                        <button
                          onClick={() => setActiveTab('alerts')}
                          className="text-sm text-teal-400 hover:text-teal-300 flex items-center gap-1"
                        >
                          View all <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {alerts.filter(a => !a.acknowledged).slice(0, 3).map((alert) => (
                          <AlertRow key={alert.id} alert={alert} onAcknowledge={acknowledgeAlert} />
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Metrics Tab */}
            {activeTab === 'metrics' && (
              <div className="space-y-6">
                {/* Resource Gauges */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <ResourceGauge
                    label="CPU Usage"
                    value={health?.cpu_usage || 45}
                    warning={70}
                    critical={90}
                    icon={Cpu}
                  />
                  <ResourceGauge
                    label="Memory Usage"
                    value={health?.memory_usage || 62}
                    warning={75}
                    critical={90}
                    icon={MemoryStick}
                  />
                  <ResourceGauge
                    label="Disk Usage"
                    value={health?.disk_usage || 38}
                    warning={80}
                    critical={95}
                    icon={HardDrive}
                  />
                </div>

                {/* Time Series Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <TimeSeriesChart
                    title="API Response Time"
                    data={cpuHistory.map(p => ({ ...p, value: p.value * 2 }))}
                    unit="ms"
                    color="teal"
                  />
                  <TimeSeriesChart
                    title="Requests per Minute"
                    data={requestHistory.map(p => ({ ...p, value: p.value * 20 }))}
                    unit=""
                    color="blue"
                  />
                </div>

                {/* Additional Metrics */}
                <Card className="admin-card">
                  <CardHeader>
                    <CardTitle className="text-base font-medium text-white flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-purple-400" />
                      Database Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                      <MetricBox label="Active Queries" value="15" trend="up" />
                      <MetricBox label="Connections" value="45/100" trend="neutral" />
                      <MetricBox label="Cache Hit Rate" value="98.5%" trend="up" />
                      <MetricBox label="Avg Query Time" value="12ms" trend="down" />
                    </div>
                  </CardContent>
                </Card>

                {/* Redis Metrics */}
                <Card className="admin-card">
                  <CardHeader>
                    <CardTitle className="text-base font-medium text-white flex items-center gap-2">
                      <Zap className="w-4 h-4 text-amber-400" />
                      Redis Cache Statistics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                      <MetricBox label="Used Memory" value={`${health?.redis_memory || 256}MB`} trend="up" />
                      <MetricBox label="Total Keys" value="12,456" trend="neutral" />
                      <MetricBox label="Hit Rate" value="94.2%" trend="up" />
                      <MetricBox label="Evictions" value="0" trend="neutral" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Alerts Tab */}
            {activeTab === 'alerts' && (
              <div className="space-y-6">
                {/* Alert Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Critical</span>
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    </div>
                    <p className="text-2xl font-medium text-white mt-2">
                      {alerts.filter(a => a.severity === 'critical').length}
                    </p>
                  </div>
                  <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Warning</span>
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    <p className="text-2xl font-medium text-white mt-2">
                      {alerts.filter(a => a.severity === 'warning').length}
                    </p>
                  </div>
                  <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Info</span>
                      <Bell className="w-4 h-4 text-blue-400" />
                    </div>
                    <p className="text-2xl font-medium text-white mt-2">
                      {alerts.filter(a => a.severity === 'info').length}
                    </p>
                  </div>
                </div>

                {/* Alerts List */}
                <Card className="admin-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base font-medium text-white">All Alerts</CardTitle>
                      <button className="text-sm text-gray-400 hover:text-white">
                        Acknowledge All
                      </button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {alerts.length > 0 ? (
                        alerts.map((alert) => (
                          <AlertRow key={alert.id} alert={alert} onAcknowledge={acknowledgeAlert} expanded />
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-400">
                          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-400" />
                          No active alerts
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Containers Tab */}
            {activeTab === 'containers' && (
              <div className="space-y-6">
                <Card className="admin-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base font-medium text-white flex items-center gap-2">
                        <Container className="w-4 h-4 text-teal-400" />
                        Docker Containers
                      </CardTitle>
                      <Badge className="bg-green-500/10 text-green-400 border-green-500/30">
                        {containers.filter(c => c.status === 'running').length}/{containers.length} Running
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-white/10">
                            <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">Container</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">Status</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">CPU</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">Memory</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 uppercase">Uptime</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 uppercase">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {containers.map((container) => (
                            <tr key={container.id} className="border-b border-white/5 hover:bg-white/[0.02]">
                              <td className="py-3 px-4">
                                <div className="flex items-center gap-3">
                                  <div className="p-2 rounded-lg bg-white/5">
                                    <Box className="w-4 h-4 text-gray-400" />
                                  </div>
                                  <span className="text-white font-medium">{container.name}</span>
                                </div>
                              </td>
                              <td className="py-3 px-4">
                                <Badge className={`${
                                  container.status === 'running' 
                                    ? 'bg-green-500/10 text-green-400 border-green-500/30'
                                    : container.status === 'unhealthy'
                                    ? 'bg-red-500/10 text-red-400 border-red-500/30'
                                    : 'bg-gray-500/10 text-gray-400 border-gray-500/30'
                                }`}>
                                  <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                                    container.status === 'running' ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
                                  }`} />
                                  {container.status}
                                </Badge>
                              </td>
                              <td className="py-3 px-4">
                                <div className="flex items-center gap-2">
                                  <div className="w-20 h-2 rounded-full bg-white/5 overflow-hidden">
                                    <div 
                                      className={`h-full rounded-full ${
                                        container.cpu > 80 ? 'bg-red-500' : container.cpu > 50 ? 'bg-amber-500' : 'bg-teal-500'
                                      }`}
                                      style={{ width: `${container.cpu}%` }}
                                    />
                                  </div>
                                  <span className="text-sm text-gray-400">{container.cpu}%</span>
                                </div>
                              </td>
                              <td className="py-3 px-4">
                                <div className="flex items-center gap-2">
                                  <div className="w-20 h-2 rounded-full bg-white/5 overflow-hidden">
                                    <div 
                                      className={`h-full rounded-full ${
                                        container.memory > 80 ? 'bg-red-500' : container.memory > 50 ? 'bg-amber-500' : 'bg-blue-500'
                                      }`}
                                      style={{ width: `${container.memory}%` }}
                                    />
                                  </div>
                                  <span className="text-sm text-gray-400">{container.memory}%</span>
                                </div>
                              </td>
                              <td className="py-3 px-4 text-gray-400">{container.uptime}</td>
                              <td className="py-3 px-4 text-right">
                                <button className="p-2 hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors">
                                  <Eye className="w-4 h-4" />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Logs Tab */}
            {activeTab === 'logs' && (
              <div className="space-y-4">
                {/* Log Filters */}
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="text"
                      placeholder="Search logs..."
                      value={logFilter.search}
                      onChange={(e) => setLogFilter({ ...logFilter, search: e.target.value })}
                      className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
                    />
                  </div>
                  <div className="flex gap-2">
                    {['all', 'error', 'warning', 'info'].map((level) => (
                      <button
                        key={level}
                        onClick={() => setLogFilter({ ...logFilter, level })}
                        className={`px-4 py-2.5 rounded-lg border transition-colors ${
                          logFilter.level === level
                            ? 'bg-white/10 border-white/20 text-white'
                            : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'
                        }`}
                      >
                        {level.charAt(0).toUpperCase() + level.slice(1)}
                      </button>
                    ))}
                  </div>
                  <Button variant="outline" className="border-white/10 hover:bg-white/5">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>

                {/* Log Viewer */}
                <Card className="admin-card">
                  <CardContent className="p-0">
                    <div className="font-mono text-sm max-h-[600px] overflow-y-auto">
                      {logs?.items?.length > 0 ? (
                        logs.items.map((log: any, i: number) => (
                          <LogLine key={i} log={log} />
                        ))
                      ) : (
                        // Mock logs for demo
                        [
                          { level: 'info', timestamp: '2024-01-15T10:30:15Z', message: 'API server started on port 8000', source: 'api' },
                          { level: 'info', timestamp: '2024-01-15T10:30:14Z', message: 'Connected to PostgreSQL database', source: 'api' },
                          { level: 'info', timestamp: '2024-01-15T10:30:13Z', message: 'Redis connection established', source: 'api' },
                          { level: 'warning', timestamp: '2024-01-15T10:29:45Z', message: 'Slow query detected: 2.3s for dataset export', source: 'postgres' },
                          { level: 'info', timestamp: '2024-01-15T10:29:30Z', message: 'Celery worker celery@worker-1 connected', source: 'celery' },
                          { level: 'error', timestamp: '2024-01-15T10:28:00Z', message: 'Failed to send email notification: SMTP timeout', source: 'api' },
                          { level: 'info', timestamp: '2024-01-15T10:27:45Z', message: 'Job generate_dataset completed in 45.2s', source: 'celery' },
                          { level: 'info', timestamp: '2024-01-15T10:27:00Z', message: 'User login: user@example.com', source: 'auth' },
                        ]
                          .filter(log => logFilter.level === 'all' || log.level === logFilter.level)
                          .filter(log => log.message.toLowerCase().includes(logFilter.search.toLowerCase()))
                          .map((log, i) => (
                            <LogLine key={i} log={log} />
                          ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </AdminLayout>
  );
}

// Component helpers
function QuickStatCard({
  title,
  value,
  unit,
  trend,
  trendValue,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  const colorMap: Record<string, string> = {
    teal: 'from-teal-500/20 to-emerald-500/20 text-teal-400',
    blue: 'from-blue-500/20 to-indigo-500/20 text-blue-400',
    green: 'from-green-500/20 to-emerald-500/20 text-green-400',
    purple: 'from-purple-500/20 to-pink-500/20 text-purple-400',
  };

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'down' ? 'text-green-400' : trend === 'up' ? 'text-red-400' : 'text-gray-400';

  return (
    <Card className="admin-card">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-gray-400">{title}</span>
          <div className={`p-2 rounded-lg bg-gradient-to-br ${colorMap[color]}`}>
            <Icon className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-end justify-between">
          <div>
            <span className="text-2xl font-medium text-white">{value}</span>
            <span className="text-sm text-gray-400 ml-1">{unit}</span>
          </div>
          <div className={`flex items-center gap-1 text-xs ${trendColor}`}>
            <TrendIcon className="w-3 h-3" />
            {trendValue}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ServiceStatusCard({
  name,
  status,
  metrics,
  icon: Icon,
}: {
  name: string;
  status: string;
  metrics: Record<string, string>;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const statusColors: Record<string, string> = {
    healthy: 'bg-green-500/10 border-green-500/30 text-green-400',
    degraded: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    critical: 'bg-red-500/10 border-red-500/30 text-red-400',
    unknown: 'bg-gray-500/10 border-gray-500/30 text-gray-400',
  };

  return (
    <Card className="admin-card">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl ${statusColors[status]?.split(' ')[0]}`}>
              <Icon className={`w-5 h-5 ${statusColors[status]?.split(' ')[2]}`} />
            </div>
            <div>
              <h4 className="font-medium text-white">{name}</h4>
              <Badge className={`mt-1 ${statusColors[status]} border`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse" />
                {status}
              </Badge>
            </div>
          </div>
        </div>
        <div className="space-y-2 mt-4 pt-4 border-t border-white/10">
          {Object.entries(metrics).map(([label, value]) => (
            <div key={label} className="flex justify-between text-sm">
              <span className="text-gray-400">{label}</span>
              <span className="text-white">{value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function MiniChart({
  title,
  data,
  currentValue,
  unit,
  color,
}: {
  title: string;
  data: MetricPoint[];
  currentValue: number;
  unit: string;
  color: string;
}) {
  const max = Math.max(...data.map(d => d.value));
  const colorMap: Record<string, string> = {
    teal: 'stroke-teal-500 fill-teal-500/10',
    blue: 'stroke-blue-500 fill-blue-500/10',
  };

  // Generate SVG path for sparkline
  const width = 300;
  const height = 60;
  const points = data.map((d, i) => ({
    x: (i / (data.length - 1)) * width,
    y: height - (d.value / max) * height,
  }));
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = `${pathD} L ${width} ${height} L 0 ${height} Z`;

  return (
    <Card className="admin-card">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-gray-400">{title}</span>
          <span className="text-xl font-medium text-white">
            {currentValue}{unit}
          </span>
        </div>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-16">
          <path d={areaD} className={colorMap[color].split(' ')[1]} />
          <path d={pathD} className={colorMap[color].split(' ')[0]} strokeWidth="2" fill="none" />
        </svg>
      </CardContent>
    </Card>
  );
}

function ResourceGauge({
  label,
  value,
  warning,
  critical,
  icon: Icon,
}: {
  label: string;
  value: number;
  warning: number;
  critical: number;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const color = value >= critical ? 'red' : value >= warning ? 'amber' : 'teal';
  const colorClasses: Record<string, string> = {
    teal: 'text-teal-400 bg-teal-500',
    amber: 'text-amber-400 bg-amber-500',
    red: 'text-red-400 bg-red-500',
  };

  return (
    <Card className="admin-card">
      <CardContent className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <Icon className={`w-5 h-5 ${colorClasses[color].split(' ')[0]}`} />
          <span className="text-white font-medium">{label}</span>
        </div>
        <div className="relative h-4 rounded-full bg-white/5 overflow-hidden">
          <div
            className={`absolute inset-y-0 left-0 rounded-full ${colorClasses[color].split(' ')[1]} transition-all duration-500`}
            style={{ width: `${value}%` }}
          />
          {/* Warning/Critical markers */}
          <div
            className="absolute inset-y-0 w-0.5 bg-amber-500/50"
            style={{ left: `${warning}%` }}
          />
          <div
            className="absolute inset-y-0 w-0.5 bg-red-500/50"
            style={{ left: `${critical}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-3">
          <span className={`text-2xl font-medium ${colorClasses[color].split(' ')[0]}`}>
            {value}%
          </span>
          <div className="text-xs text-gray-500">
            Warning: {warning}% | Critical: {critical}%
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function TimeSeriesChart({
  title,
  data,
  unit,
  color,
}: {
  title: string;
  data: MetricPoint[];
  unit: string;
  color: string;
}) {
  const max = Math.max(...data.map(d => d.value));
  const min = Math.min(...data.map(d => d.value));
  const avg = data.reduce((sum, d) => sum + d.value, 0) / data.length;

  const width = 400;
  const height = 120;
  const points = data.map((d, i) => ({
    x: (i / (data.length - 1)) * width,
    y: height - ((d.value - min) / (max - min || 1)) * height,
  }));
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = `${pathD} L ${width} ${height} L 0 ${height} Z`;

  const colorMap: Record<string, string> = {
    teal: 'stroke-teal-500 fill-teal-500/10',
    blue: 'stroke-blue-500 fill-blue-500/10',
  };

  return (
    <Card className="admin-card">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium text-white">{title}</CardTitle>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-gray-400">Min: <span className="text-white">{Math.round(min)}{unit}</span></span>
            <span className="text-gray-400">Avg: <span className="text-white">{Math.round(avg)}{unit}</span></span>
            <span className="text-gray-400">Max: <span className="text-white">{Math.round(max)}{unit}</span></span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-32">
          <path d={areaD} className={colorMap[color].split(' ')[1]} />
          <path d={pathD} className={colorMap[color].split(' ')[0]} strokeWidth="2" fill="none" />
        </svg>
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>30m ago</span>
          <span>15m ago</span>
          <span>Now</span>
        </div>
      </CardContent>
    </Card>
  );
}

function MetricBox({
  label,
  value,
  trend,
}: {
  label: string;
  value: string;
  trend: 'up' | 'down' | 'neutral';
}) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-teal-400' : 'text-gray-400';

  return (
    <div className="p-4 bg-white/[0.02] rounded-xl">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <div className="flex items-center justify-between">
        <span className="text-lg font-medium text-white">{value}</span>
        <TrendIcon className={`w-4 h-4 ${trendColor}`} />
      </div>
    </div>
  );
}

function AlertRow({
  alert,
  onAcknowledge,
  expanded = false,
}: {
  alert: Alert;
  onAcknowledge: (id: string) => void;
  expanded?: boolean;
}) {
  const severityColors: Record<string, string> = {
    critical: 'border-red-500/30 bg-red-500/5',
    warning: 'border-amber-500/30 bg-amber-500/5',
    info: 'border-blue-500/30 bg-blue-500/5',
  };
  const iconColors: Record<string, string> = {
    critical: 'text-red-400',
    warning: 'text-amber-400',
    info: 'text-blue-400',
  };
  const Icon = alert.severity === 'critical' ? XCircle : alert.severity === 'warning' ? AlertTriangle : Bell;

  return (
    <div className={`p-4 rounded-lg border ${severityColors[alert.severity]} ${alert.acknowledged ? 'opacity-50' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <Icon className={`w-5 h-5 mt-0.5 ${iconColors[alert.severity]}`} />
          <div>
            <p className="text-white font-medium">{alert.title}</p>
            {expanded && <p className="text-sm text-gray-400 mt-1">{alert.message}</p>}
            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
              <span>{alert.service}</span>
              <span>•</span>
              <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
        {!alert.acknowledged && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className="px-3 py-1.5 text-xs bg-white/5 hover:bg-white/10 rounded-lg text-gray-300 transition-colors"
          >
            Acknowledge
          </button>
        )}
      </div>
    </div>
  );
}

function LogLine({ log }: { log: any }) {
  const levelColors: Record<string, string> = {
    error: 'text-red-400',
    warning: 'text-amber-400',
    info: 'text-blue-400',
    debug: 'text-gray-400',
  };

  return (
    <div className="flex items-start gap-4 px-4 py-2 border-b border-white/5 hover:bg-white/[0.02]">
      <span className="text-xs text-gray-600 whitespace-nowrap">
        {new Date(log.timestamp).toLocaleTimeString()}
      </span>
      <span className={`text-xs uppercase w-16 ${levelColors[log.level] || 'text-gray-400'}`}>
        [{log.level}]
      </span>
      <span className="text-xs text-gray-500 w-20">{log.source}</span>
      <span className="text-sm text-gray-300 flex-1">{log.message}</span>
    </div>
  );
}
