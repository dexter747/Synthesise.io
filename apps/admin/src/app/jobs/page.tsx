'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { useAdminJobs } from '@/hooks/use-admin-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Zap,
  Play,
  Pause,
  RefreshCw,
  StopCircle,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Loader2,
  Search,
  Filter,
  MoreVertical,
  Eye,
  Trash2,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Database,
  Users,
  Activity,
  TrendingUp,
  Timer,
  HardDrive,
  Cpu,
} from 'lucide-react';

interface Job {
  id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  rows_requested: number;
  rows_generated: number;
  user_email: string;
  user_id?: string;
  dataset_name: string;
  dataset_id?: string;
  started_at: string | null;
  completed_at?: string | null;
  failed_at?: string | null;
  estimated_completion?: string | null;
  error?: string;
  worker: string;
  priority: string;
  created_at?: string;
}

// Mock jobs data (can be removed when API is fully integrated)
const mockJobs = [
  { 
    id: 'JOB-20240115-001', 
    status: 'processing', 
    progress: 67, 
    rows_requested: 50000,
    rows_generated: 33500,
    user_email: 'john@example.com',
    dataset_name: 'Customer Analytics Data',
    started_at: '2024-01-15T10:30:00Z',
    estimated_completion: '2024-01-15T10:45:00Z',
    worker: 'worker-1',
    priority: 'high',
  },
  { 
    id: 'JOB-20240115-002', 
    status: 'queued', 
    progress: 0, 
    rows_requested: 100000,
    rows_generated: 0,
    user_email: 'sarah@company.io',
    dataset_name: 'E-commerce Transactions',
    started_at: null,
    estimated_completion: null,
    worker: null,
    priority: 'normal',
  },
  { 
    id: 'JOB-20240115-003', 
    status: 'processing', 
    progress: 23, 
    rows_requested: 25000,
    rows_generated: 5750,
    user_email: 'mike@startup.com',
    dataset_name: 'User Behavior Log',
    started_at: '2024-01-15T10:28:00Z',
    estimated_completion: '2024-01-15T10:50:00Z',
    worker: 'worker-2',
    priority: 'normal',
  },
  { 
    id: 'JOB-20240115-004', 
    status: 'completed', 
    progress: 100, 
    rows_requested: 10000,
    rows_generated: 10000,
    user_email: 'alice@data.org',
    dataset_name: 'Financial Records',
    started_at: '2024-01-15T10:15:00Z',
    completed_at: '2024-01-15T10:25:00Z',
    worker: 'worker-3',
    priority: 'high',
  },
  { 
    id: 'JOB-20240115-005', 
    status: 'failed', 
    progress: 45, 
    rows_requested: 75000,
    rows_generated: 33750,
    user_email: 'bob@tech.co',
    dataset_name: 'Product Inventory',
    started_at: '2024-01-15T10:00:00Z',
    failed_at: '2024-01-15T10:12:00Z',
    error: 'Memory limit exceeded',
    worker: 'worker-1',
    priority: 'low',
  },
];

// Worker stats
const workerStats = [
  { id: 'worker-1', status: 'busy', jobs: 1, memory: 78, cpu: 45 },
  { id: 'worker-2', status: 'busy', jobs: 1, memory: 65, cpu: 32 },
  { id: 'worker-3', status: 'idle', jobs: 0, memory: 23, cpu: 5 },
  { id: 'worker-4', status: 'idle', jobs: 0, memory: 18, cpu: 3 },
];

export default function AdminJobsPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selectedJob, setSelectedJob] = useState<string | null>(null);

  const { data, isLoading, refetch } = useAdminJobs({
    status: statusFilter || undefined,
    search: search || undefined,
    per_page: 100,
  });

  const jobs = data?.jobs || [];
  const stats = data?.stats || {
    total: 0,
    processing: 0,
    queued: 0,
    completed: 0,
    failed: 0,
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatDuration = (startTime: string | null, endTime?: string | null) => {
    if (!startTime) return '-';
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diff = Math.floor((end.getTime() - start.getTime()) / 1000);
    const mins = Math.floor(diff / 60);
    const secs = diff % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <AdminLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Page Header */}
        <div className="page-header">
          <div>
            <h2 className="page-title">
              <span className="gradient-teal-text">Jobs Queue</span>
            </h2>
            <p className="page-subtitle">Monitor and manage data generation jobs in real-time</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-4 py-2.5 glass rounded-xl border border-teal-500/20">
              <Activity className="w-4 h-4 text-teal-400 animate-pulse" />
              <span className="text-sm font-medium text-gray-300">Real-time Updates</span>
            </div>
            <button className="btn-secondary flex items-center gap-2" onClick={() => refetch()}>
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard 
            title="Total Jobs" 
            value={stats.total} 
            icon={Database} 
            color="teal" 
          />
          <StatCard 
            title="Processing" 
            value={stats.processing} 
            icon={Loader2} 
            color="blue"
            animated 
          />
          <StatCard 
            title="In Queue" 
            value={stats.queued} 
            icon={Clock} 
            color="amber" 
          />
          <StatCard 
            title="Completed" 
            value={stats.completed} 
            icon={CheckCircle} 
            color="emerald" 
          />
          <StatCard 
            title="Failed" 
            value={stats.failed} 
            icon={XCircle} 
            color="red" 
          />
        </div>

        {/* Workers Status */}
        <Card className="admin-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                  <Cpu className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <CardTitle className="text-white">Worker Nodes</CardTitle>
                  <p className="text-xs text-gray-500 mt-0.5">Celery worker status</p>
                </div>
              </div>
              <Badge className="badge-emerald">
                {workerStats.filter(w => w.status === 'busy').length} Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {workerStats.map((worker) => (
                <WorkerCard key={worker.id} worker={worker} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <Card className="admin-card">
          <CardContent className="py-4">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search by job ID, user, or dataset name..."
                    className="input-search w-full"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-400">Status:</span>
                </div>
                <div className="flex gap-1">
                  {[
                    { value: '', label: 'All', color: 'gray' },
                    { value: 'processing', label: 'Processing', color: 'blue' },
                    { value: 'queued', label: 'Queued', color: 'amber' },
                    { value: 'completed', label: 'Completed', color: 'emerald' },
                    { value: 'failed', label: 'Failed', color: 'red' },
                  ].map((status) => (
                    <button
                      key={status.value}
                      onClick={() => setStatusFilter(status.value)}
                      className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                        statusFilter === status.value
                          ? `bg-${status.color}-500/20 text-${status.color}-400 border border-${status.color}-500/30`
                          : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      {status.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Jobs Table */}
        <Card className="admin-card overflow-hidden">
          <CardContent className="p-0">
            <div className="overflow-x-auto scrollbar-thin">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="table-header">Job ID</th>
                    <th className="table-header">Dataset</th>
                    <th className="table-header">Status</th>
                    <th className="table-header">Progress</th>
                    <th className="table-header">Rows</th>
                    <th className="table-header">Duration</th>
                    <th className="table-header">Worker</th>
                    <th className="table-header text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <tr>
                      <td colSpan={8} className="table-cell text-center py-12">
                        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-teal-400 mb-2" />
                        <p className="text-gray-400">Loading jobs...</p>
                      </td>
                    </tr>
                  ) : jobs.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="table-cell text-center py-12">
                        <Database className="w-12 h-12 mx-auto text-gray-600 mb-3" />
                        <p className="text-gray-400">No jobs found</p>
                      </td>
                    </tr>
                  ) : (
                    jobs.map((job: Job, index: number) => (
                      <JobRow 
                        key={job.id} 
                        job={job} 
                        index={index}
                        formatNumber={formatNumber}
                        formatDuration={formatDuration}
                      />
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {jobs.length === 0 && !isLoading && (
              <div className="text-center py-16">
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
                  <Zap className="w-10 h-10 text-gray-600" />
                </div>
                <h3 className="text-xl font-medium text-white mb-2">No jobs found</h3>
                <p className="text-gray-400">No jobs match your current filters</p>
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
  icon: Icon, 
  color,
  animated 
}: { 
  title: string; 
  value: number; 
  icon: React.ComponentType<{ className?: string }>; 
  color: string;
  animated?: boolean;
}) {
  const colorClasses: Record<string, string> = {
    teal: 'from-teal-500/20 to-emerald-500/20 border-teal-500/30 text-teal-400',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    amber: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400',
    emerald: 'from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-400',
    red: 'from-red-500/20 to-rose-500/20 border-red-500/30 text-red-400',
  };

  return (
    <div className="stat-card group">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{title}</p>
          <p className="text-3xl font-medium text-white">{value}</p>
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]} border group-hover:scale-110 transition-transform`}>
          <Icon className={`w-5 h-5 ${animated ? 'animate-spin' : ''}`} />
        </div>
      </div>
    </div>
  );
}

function WorkerCard({ worker }: { worker: typeof workerStats[0] }) {
  return (
    <div className={`p-4 rounded-xl border transition-all ${
      worker.status === 'busy' 
        ? 'bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/30' 
        : 'bg-white/[0.03] border-white/10'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-mono text-white">{worker.id}</span>
        <span className={`badge ${worker.status === 'busy' ? 'badge-blue' : 'badge-gray'}`}>
          {worker.status === 'busy' && <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mr-1.5 animate-pulse" />}
          {worker.status}
        </span>
      </div>
      <div className="space-y-2">
        <ResourceMeter label="CPU" value={worker.cpu} />
        <ResourceMeter label="Memory" value={worker.memory} />
      </div>
      <p className="text-xs text-gray-500 mt-3">
        {worker.jobs} active job{worker.jobs !== 1 ? 's' : ''}
      </p>
    </div>
  );
}

function ResourceMeter({ label, value }: { label: string; value: number }) {
  const getColor = (v: number) => {
    if (v < 50) return 'bg-emerald-500';
    if (v < 80) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-gray-500 w-12">{label}</span>
      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div 
          className={`h-full ${getColor(value)} rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-[10px] text-gray-400 w-8 text-right">{value}%</span>
    </div>
  );
}

function JobRow({ 
  job, 
  index,
  formatNumber,
  formatDuration,
}: { 
  job: Job; 
  index: number;
  formatNumber: (n: number) => string;
  formatDuration: (start: string | null, end?: string | null) => string;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  const statusConfig: Record<string, { badge: string; icon: typeof CheckCircle; animated?: boolean }> = {
    processing: { badge: 'badge-blue', icon: Loader2, animated: true },
    queued: { badge: 'badge-amber', icon: Clock },
    completed: { badge: 'badge-emerald', icon: CheckCircle },
    failed: { badge: 'badge-red', icon: XCircle },
    cancelled: { badge: 'badge-gray', icon: StopCircle },
  };

  const config = statusConfig[job.status] || statusConfig.queued;
  const StatusIcon = config.icon;

  return (
    <tr 
      className="table-row-interactive animate-fade-in"
      style={{ animationDelay: `${index * 30}ms` }}
    >
      <td className="table-cell">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            job.priority === 'high' ? 'bg-amber-500/10 border border-amber-500/20' : 'bg-white/5'
          }`}>
            <Zap className={`w-4 h-4 ${job.priority === 'high' ? 'text-amber-400' : 'text-gray-400'}`} />
          </div>
          <div>
            <p className="font-mono text-sm text-white">{job.id}</p>
            <p className="text-xs text-gray-500">{job.user_email}</p>
          </div>
        </div>
      </td>
      <td className="table-cell">
        <p className="text-white truncate max-w-[200px]">{job.dataset_name}</p>
      </td>
      <td className="table-cell">
        <span className={`badge ${config.badge}`}>
          <StatusIcon className={`w-3 h-3 mr-1.5 ${config.animated ? 'animate-spin' : ''}`} />
          {job.status}
        </span>
      </td>
      <td className="table-cell">
        <div className="w-32">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">{job.progress}%</span>
          </div>
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                job.status === 'completed' ? 'bg-emerald-500' :
                job.status === 'failed' ? 'bg-red-500' :
                'bg-gradient-to-r from-teal-500 to-emerald-500'
              }`}
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      </td>
      <td className="table-cell">
        <div>
          <p className="text-white">{formatNumber(job.rows_generated)}</p>
          <p className="text-xs text-gray-500">of {formatNumber(job.rows_requested)}</p>
        </div>
      </td>
      <td className="table-cell">
        <span className="text-gray-400">
          {formatDuration(job.started_at, (job as any).completed_at || (job as any).failed_at)}
        </span>
      </td>
      <td className="table-cell">
        {job.worker ? (
          <span className="badge badge-gray font-mono text-xs">{job.worker}</span>
        ) : (
          <span className="text-gray-500">-</span>
        )}
      </td>
      <td className="table-cell text-right">
        <div className="relative inline-flex items-center gap-1">
          <button className="btn-icon" title="View Details">
            <Eye className="w-4 h-4" />
          </button>
          <button 
            onClick={() => setMenuOpen(!menuOpen)}
            className="btn-icon"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-full mt-2 w-48 bg-[#111111] rounded-xl shadow-2xl border border-white/10 py-2 z-50 animate-scale-in">
                <button className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-300 hover:bg-white/5 transition-colors">
                  <Eye className="w-4 h-4 text-gray-400" />
                  View Details
                </button>
                {job.status === 'failed' && (
                  <button className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-teal-400 hover:bg-white/5 transition-colors">
                    <RotateCcw className="w-4 h-4" />
                    Retry Job
                  </button>
                )}
                {(job.status === 'processing' || job.status === 'queued') && (
                  <button className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-amber-400 hover:bg-white/5 transition-colors">
                    <StopCircle className="w-4 h-4" />
                    Cancel Job
                  </button>
                )}
                <div className="border-t border-white/10 mt-2 pt-2">
                  <button className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors">
                    <Trash2 className="w-4 h-4" />
                    Delete Job
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </td>
    </tr>
  );
}
