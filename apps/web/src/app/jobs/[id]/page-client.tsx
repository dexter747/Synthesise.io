'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { useJob, useJobStatus, useCancelJob } from '@/hooks/use-api';
import { formatDate, formatNumber, formatBytes } from '@/lib/utils';
import { toast } from 'sonner';
import type { GenerationJob } from '@synthesize/types';
import {
  ArrowLeft,
  Download,
  RefreshCw,
  X,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Database,
  FileText,
  Loader2,
  PlayCircle,
  Copy,
  ExternalLink,
} from 'lucide-react';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { data: job, isLoading } = useJob(jobId);
  const { data: statusData } = useJobStatus(jobId, autoRefresh && (job?.status === 'processing' || job?.status === 'pending'));
  const cancelJob = useCancelJob();

  // Stop auto-refresh when job is complete or failed
  useEffect(() => {
    if (job && ['completed', 'failed', 'cancelled'].includes(job.status)) {
      setAutoRefresh(false);
    }
  }, [job?.status]);

  // Merge status updates with full job data
  const currentJob: GenerationJob | undefined = job ? {
    ...job,
    ...(statusData ? { status: statusData.status as GenerationJob['status'], progress: statusData.progress } : {}),
  } : undefined;

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this generation job?')) {
      return;
    }

    try {
      await cancelJob.mutateAsync(jobId);
      toast.success('Job canceled successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to cancel job');
    }
  };

  const handleRetry = () => {
    if (!currentJob?.dataset_id) {
      toast.error('Cannot retry - dataset information missing');
      return;
    }
    router.push(`/datasets/${currentJob.dataset_id}?generate=true`);
  };

  const handleDownload = () => {
    if (!currentJob?.download_url && currentJob?.status !== 'completed') {
      toast.error('No file available for download');
      return;
    }

    // FIX: NEXT_PUBLIC_API_URL already includes /api/v1
    const token = localStorage.getItem('access_token');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const downloadUrl = currentJob.download_url || `${apiUrl}/jobs/${jobId}/download`;
    
    fetch(downloadUrl.startsWith('http') ? downloadUrl : `${apiUrl}${downloadUrl}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
      .then(response => {
        if (!response.ok) throw new Error('Download failed');
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = `dataset_${jobId}.${currentJob?.output_format || 'csv'}`;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        toast.success('Download started');
      })
      .catch(error => {
        console.error('Download error:', error);
        toast.error('Download failed');
      });
  };

  const copyJobId = () => {
    navigator.clipboard.writeText(jobId);
    toast.success('Job ID copied to clipboard');
  };

  const getStatusIcon = () => {
    switch (currentJob?.status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-400" />;
      case 'cancelled':
        return <X className="w-6 h-6 text-zinc-400" />;
      case 'processing':
      case 'pending':
        return <Loader2 className="w-6 h-6 text-teal-400 animate-spin" />;
      default:
        return <Clock className="w-6 h-6 text-yellow-400" />;
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  if (!currentJob) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto">
          <Card className="text-center py-12">
            <p className="text-zinc-400">Job not found</p>
            <Button
              variant="outline"
              onClick={() => router.push('/jobs')}
              className="mt-4"
            >
              Back to Jobs
            </Button>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  const progress = currentJob?.progress ?? currentJob?.progress_percent ?? 0;
  const isComplete = currentJob?.status === 'completed';
  const isFailed = currentJob?.status === 'failed';
  const isRunning = currentJob?.status === 'processing' || currentJob?.status === 'pending' || currentJob?.status === 'queued';
  const canCancel = isRunning;
  const canRetry = isFailed;
  const canDownload = isComplete;

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <Button
              variant="ghost"
              onClick={() => router.push('/jobs')}
              className="mt-1"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <div className="flex items-center gap-3 mb-2">
                {getStatusIcon()}
                <h1 className="text-2xl font-semibold text-white">
                  Generation Job
                </h1>
                <StatusBadge status={currentJob.status} />
              </div>
              <div className="flex items-center gap-2 text-sm text-zinc-400">
                <code className="text-xs bg-white/5 px-2 py-1 rounded">{jobId.slice(0, 8)}</code>
                <button onClick={copyJobId} className="hover:text-white transition-colors">
                  <Copy className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            {canDownload && (
              <Button variant="gradient" onClick={handleDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            )}
            {canRetry && (
              <Button variant="outline" onClick={handleRetry}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            )}
            {canCancel && (
              <Button
                variant="outline"
                onClick={handleCancel}
                disabled={cancelJob.isPending}
                className="text-red-400 hover:bg-red-500/10"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            )}
          </div>
        </div>

        {/* Progress Bar (for running jobs) */}
        {isRunning && (
          <Card className="bg-gradient-to-br from-teal-500/10 to-emerald-500/10 border-teal-500/20">
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white font-medium">
                    {currentJob.rows_generated
                      ? `${formatNumber(currentJob.rows_generated)} rows generated`
                      : 'Processing...'}
                  </span>
                  <span className="text-teal-400 font-semibold">{progress.toFixed(0)}%</span>
                </div>
                <div className="h-2.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-teal-500 to-emerald-400 transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="flex items-center gap-2 text-xs text-zinc-400">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Started {formatDate(currentJob.started_at || currentJob.created_at)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {isFailed && currentJob.error_message && (
          <Card className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <AlertTriangle className="w-5 h-5" />
                Error Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm text-zinc-300 bg-black/30 p-4 rounded-lg overflow-x-auto">
                {currentJob.error_message}
              </pre>
              <p className="text-xs text-zinc-500 mt-3">
                If this error persists, please contact support with the job ID above.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Job Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-teal-400" />
              Job Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  Dataset
                </label>
                <div className="mt-1">
                  {currentJob.dataset_id ? (
                    <Link
                      href={`/datasets/${currentJob.dataset_id}`}
                      className="text-white hover:text-teal-400 transition-colors flex items-center gap-1"
                    >
                      <Database className="w-4 h-4" />
                      {currentJob.dataset?.name || 'View Dataset'}
                      <ExternalLink className="w-3 h-3" />
                    </Link>
                  ) : (
                    <span className="text-zinc-400">N/A</span>
                  )}
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  Rows Requested
                </label>
                <p className="text-white mt-1 font-medium">
                  {formatNumber(currentJob.row_count || 0)}
                </p>
              </div>

              <div>
                <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  Rows Generated
                </label>
                <p className="text-white mt-1 font-medium">
                  {formatNumber(currentJob.rows_generated || 0)}
                </p>
              </div>

              <div>
                <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  Output Format
                </label>
                <p className="text-white mt-1">
                  <Badge variant="outline">
                    {(currentJob.output_format || 'csv').toUpperCase()}
                  </Badge>
                </p>
              </div>

              {currentJob.file_size_bytes && (
                <div>
                  <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    File Size
                  </label>
                  <p className="text-white mt-1 font-medium">
                    {formatBytes(currentJob.file_size_bytes)}
                  </p>
                </div>
              )}

              <div>
                <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  Priority
                </label>
                <p className="text-white mt-1">
                  <Badge variant="outline">
                    {currentJob.priority || 'Normal'}
                  </Badge>
                </p>
              </div>

              <div>
                <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  Created
                </label>
                <p className="text-white mt-1">
                  {formatDate(currentJob.created_at)}
                </p>
              </div>

              {currentJob.completed_at && (
                <div>
                  <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    Completed
                  </label>
                  <p className="text-white mt-1">
                    {formatDate(currentJob.completed_at)}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Success Actions */}
        {isComplete && (
          <Card className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border-green-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <CheckCircle className="w-12 h-12 text-green-400" />
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-white mb-1">
                    Generation Complete!
                  </h3>
                  <p className="text-sm text-zinc-300">
                    Successfully generated {formatNumber(currentJob.rows_generated || 0)} rows of synthetic data.
                    {currentJob.download_url && ' Your file is ready for download.'}
                  </p>
                </div>
                {canDownload && (
                  <Button variant="gradient" onClick={handleDownload} size="lg">
                    <Download className="w-5 h-5 mr-2" />
                    Download File
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Button
                variant="outline"
                onClick={() => currentJob.dataset_id && router.push(`/datasets/${currentJob.dataset_id}`)}
                disabled={!currentJob.dataset_id}
                className="w-full"
              >
                <Database className="w-4 h-4 mr-2" />
                View Dataset
              </Button>
              <Button
                variant="outline"
                onClick={handleRetry}
                className="w-full"
              >
                <PlayCircle className="w-4 h-4 mr-2" />
                Generate Again
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push('/jobs')}
                className="w-full"
              >
                <FileText className="w-4 h-4 mr-2" />
                All Jobs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
