'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { useJobs, useCancelJob, useDeleteJob } from '@/hooks/use-api';
import { formatNumber, formatRelativeTime, debounce } from '@/lib/utils';
import Link from 'next/link';
import { toast } from 'sonner';
import {
  Search,
  Play,
  Download,
  MoreVertical,
  XCircle,
  Trash2,
  RefreshCw,
  Eye,
  Loader2,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  Clock,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { getAPI } from '@synthesize/api-client';

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const { data, isLoading } = useJobs({
    page,
    per_page: 10,
    status: statusFilter || undefined,
  });

  const cancelJob = useCancelJob();
  const deleteJob = useDeleteJob();

  const jobs = data?.items || [];
  const totalPages = Math.ceil((data?.total || 0) / (data?.per_page || 10));

  const handleCancel = async (id: string) => {
    try {
      await cancelJob.mutateAsync(id);
      toast.success('Job cancelled');
    } catch (error: any) {
      toast.error(error.message || 'Failed to cancel job');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this job?')) return;

    try {
      await deleteJob.mutateAsync(id);
      toast.success('Job deleted');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete job');
    }
  };

  const handleDownload = (id: string) => {
    const url = getAPI().getJobDownloadUrl(id);
    window.open(url, '_blank');
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-medium text-white">Generation Jobs</h1>
            <p className="text-zinc-400 mt-1">Track and manage your data generation jobs</p>
          </div>
        </div>

        {/* Filters */}
        <Card glass>
          <CardContent className="py-4">
            <div className="flex flex-wrap gap-2">
              {[
                { value: '', label: 'All' },
                { value: 'pending', label: 'Pending' },
                { value: 'queued', label: 'Queued' },
                { value: 'processing', label: 'Processing' },
                { value: 'completed', label: 'Completed' },
                { value: 'failed', label: 'Failed' },
                { value: 'canceled', label: 'Cancelled' },
              ].map((status) => (
                <Button
                  key={status.value}
                  variant={statusFilter === status.value ? 'gradient' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setStatusFilter(status.value);
                    setPage(1);
                  }}
                >
                  {status.label}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Jobs List */}
        <Card glass>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-16">
                <Play className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No jobs found</h3>
                <p className="text-zinc-400 mb-6">
                  {statusFilter
                    ? 'Try adjusting your filters'
                    : 'Generate data from a dataset to create jobs'}
                </p>
                <Link href="/datasets">
                  <Button variant="gradient">Browse Datasets</Button>
                </Link>
              </div>
            ) : (
              <>
                <div className="divide-y divide-white/5">
                  {jobs.map((job) => (
                    <JobRow
                      key={job.id}
                      job={job}
                      onCancel={() => handleCancel(job.id)}
                      onDelete={() => handleDelete(job.id)}
                      onDownload={() => handleDownload(job.id)}
                    />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
                    <p className="text-sm text-zinc-500">
                      Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, data?.total || 0)} of{' '}
                      {data?.total || 0} jobs
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
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
      </div>
    </DashboardLayout>
  );
}

function JobRow({
  job,
  onCancel,
  onDelete,
  onDownload,
}: {
  job: any;
  onCancel: () => void;
  onDelete: () => void;
  onDownload: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="flex items-center gap-4 px-6 py-4 hover:bg-white/5 transition-colors">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
        <JobStatusIcon status={job.status} />
      </div>

      <div className="flex-1 min-w-0">
        <Link href={`/jobs/${job.id}`} className="block">
          <h3 className="font-medium text-white truncate hover:text-teal-400 transition-colors">
            {job.dataset?.name || job.dataset_name || 'Untitled Dataset'}
          </h3>
        </Link>
        <p className="text-sm font-medium text-zinc-500">
          {formatNumber(job.row_count || 0)} rows • {job.format?.toUpperCase() || 'JSON'} •{' '}
          {formatRelativeTime(job.created_at)}
        </p>
        {(job.status === 'running' || job.status === 'processing') && (
          <div className="mt-2 w-full max-w-xs">
            <div className="w-full bg-zinc-800 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-teal-500 to-emerald-500 h-1.5 rounded-full transition-all"
                style={{ width: `${job.progress || 0}%` }}
              />
            </div>
            <p className="text-xs font-medium text-zinc-500 mt-1">{job.progress || 0}% complete</p>
          </div>
        )}
      </div>

      <StatusBadge status={job.status} />

      <div className="flex items-center gap-2">
        {/* Prominent Download Button for completed jobs */}
        {job.status === 'completed' && (
          <Button 
            variant="gradient" 
            size="sm" 
            onClick={onDownload}
            className="px-4 py-2 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-medium rounded-lg shadow-lg shadow-teal-500/20"
          >
            <Download className="w-4 h-4 mr-1.5" />
            Download
          </Button>
        )}
        
        {/* Cancel button for running jobs */}
        {(job.status === 'pending' || job.status === 'running' || job.status === 'processing' || job.status === 'queued') && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onCancel}
            className="text-yellow-400 border-yellow-400/30 hover:bg-yellow-400/10"
          >
            <XCircle className="w-4 h-4 mr-1.5" />
            Cancel
          </Button>
        )}

        <div className="relative">
          <Button variant="ghost" size="sm" onClick={() => setMenuOpen(!menuOpen)} className="p-2">
            <MoreVertical className="w-4 h-4" />
          </Button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 mt-1 w-48 bg-zinc-900 rounded-lg shadow-lg border border-white/10 py-1 z-50">
                <Link
                  href={`/jobs/${job.id}`}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-zinc-300 hover:bg-white/5"
                  onClick={() => setMenuOpen(false)}
                >
                  <Eye className="w-4 h-4" />
                  View Details
                </Link>
                {job.status === 'completed' && (
                  <button
                    className="flex items-center gap-2 w-full px-4 py-2 text-sm text-zinc-300 hover:bg-white/5"
                    onClick={() => {
                      setMenuOpen(false);
                      onDownload();
                    }}
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                )}
                <hr className="my-1 border-white/5" />
                <button
                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-400 hover:bg-white/5"
                  onClick={() => {
                    setMenuOpen(false);
                    onDelete();
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function JobStatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-white" />;
    case 'failed':
    case 'error':
      return <XCircle className="w-5 h-5 text-white" />;
    case 'running':
    case 'processing':
      return <Loader2 className="w-5 h-5 text-white animate-spin" />;
    case 'cancelled':
    case 'canceled':
      return <XCircle className="w-5 h-5 text-white/70" />;
    case 'queued':
    case 'pending':
    default:
      return <Clock className="w-5 h-5 text-white" />;
  }
}
