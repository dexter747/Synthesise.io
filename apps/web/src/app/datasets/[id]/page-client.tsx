'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { SchemaEditor } from '@/components/datasets/schema-editor';
import { useDataset, useDeleteDataset, useGenerateData, useDatasetJobs } from '@/hooks/use-api';
import { useAuth } from '@/providers/auth-provider';
import { formatDate, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';
import { getAPI } from '@synthesize/api-client';
import {
  ArrowLeft,
  Download,
  Play,
  Edit,
  Trash2,
  Share2,
  Archive,
  Loader2,
  Database,
  Clock,
  FileText,
  MoreVertical,
  Sparkles,
  Eye,
  Code,
  Table as TableIcon,
} from 'lucide-react';

export default function DatasetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const datasetId = params.id as string;
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showSchemaEditor, setShowSchemaEditor] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [rowCount, setRowCount] = useState('100');
  const [menuOpen, setMenuOpen] = useState(false);
  
  // Auto-open generate modal if ?generate=true is in the URL
  useEffect(() => {
    if (searchParams.get('generate') === 'true') {
      setShowGenerateModal(true);
    }
  }, [searchParams]);

  const { user } = useAuth();
  const { data: dataset, isLoading } = useDataset(datasetId);
  const { data: datasetJobs, isLoading: isLoadingJobs } = useDatasetJobs(datasetId);
  const deleteDataset = useDeleteDataset();
  const generateData = useGenerateData();

  // Get max rows based on subscription tier
  const getMaxRows = () => {
    const tier = user?.subscription_tier?.toLowerCase();
    switch (tier) {
      case 'business': return 1000000; // 1M
      case 'pro': return 100000; // 100K
      case 'beginner': return 5000;
      case 'enterprise': return 10000000; // 10M
      default: return 5000; // Free tier
    }
  };
  const maxRows = getMaxRows();

  const handleDelete = async () => {
    try {
      await deleteDataset.mutateAsync(datasetId);
      toast.success('Dataset deleted successfully');
      router.push('/datasets');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete dataset');
    }
  };

  const handleGenerate = async () => {
    const count = parseInt(rowCount);
    if (isNaN(count) || count < 1 || count > maxRows) {
      toast.error(`Please enter a valid row count (1-${formatNumber(maxRows)})`);
      return;
    }

    try {
      const job = await generateData.mutateAsync({
        datasetId: datasetId,
        data: {
          row_count: count,
        },
      });
      toast.success('Data generation started!');
      setShowGenerateModal(false);
      router.push(`/jobs/${job.id}`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to start generation');
    }
  };

  const handleDownloadJob = (jobId: string) => {
    const url = getAPI().getJobDownloadUrl(jobId);
    window.open(url, '_blank');
  };

  const handlePreviewData = async () => {
    setIsLoadingPreview(true);
    try {
      // Generate preview (5-10 rows)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(
        `${apiUrl}/datasets/${datasetId}/preview`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({ row_count: 10 }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to generate preview');
      }

      const data = await response.json();
      setPreviewData(data.sample || data.data || []);
      setShowPreview(true);
      toast.success('Preview generated!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate preview');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const handleSaveSchema = async (fields: any[]) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(
        `${apiUrl}/datasets/${datasetId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            schema_definition: {
              fields: fields,
              version: (dataset?.schema_definition?.version || 0) + 1,
            },
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update schema');
      }

      // Refresh dataset
      window.location.reload();
    } catch (error: any) {
      throw error;
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-zinc-400" />
        </div>
      </DashboardLayout>
    );
  }

  if (!dataset) {
    return (
      <DashboardLayout>
        <div className="text-center py-16">
          <Database className="w-16 h-16 text-zinc-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">Dataset not found</h3>
          <p className="text-zinc-400 mb-6">The dataset you're looking for doesn't exist.</p>
          <Button onClick={() => router.push('/datasets')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Datasets
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <Button variant="ghost" onClick={() => router.push('/datasets')}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-medium text-white">{dataset.name}</h1>
                <StatusBadge status={dataset.status} />
              </div>
              {dataset.description && (
                <p className="text-zinc-400 font-medium mt-1">{dataset.description}</p>
              )}
              <div className="flex items-center gap-4 mt-2 text-sm font-medium text-zinc-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Created {formatDate(dataset.created_at)}
                </span>
                <span className="flex items-center gap-1">
                  <Database className="w-4 h-4" />
                  {dataset.schema_definition?.fields?.length || 0} fields
                </span>
                {(dataset.row_count || 0) > 0 && (
                  <span className="flex items-center gap-1 text-teal-400">
                    <Sparkles className="w-4 h-4" />
                    {formatNumber(dataset.row_count || 0)} rows generated
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handlePreviewData} disabled={isLoadingPreview}>
              {isLoadingPreview ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Eye className="w-4 h-4 mr-2" />
              )}
              Preview Data
            </Button>
            <Button variant="gradient" size="lg" onClick={() => setShowGenerateModal(true)}>
              <Sparkles className="w-4 h-4 mr-2" />
              Generate Data
            </Button>
            <div className="relative">
              <Button variant="ghost" size="sm" onClick={() => setMenuOpen(!menuOpen)}>
                <MoreVertical className="w-4 h-4" />
              </Button>
              {menuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
                  <div className="absolute right-0 mt-1 w-48 bg-white/10 backdrop-blur-xl rounded-lg shadow-lg border border-white/10 py-1 z-50">
                    <button 
                      className="flex items-center gap-2 w-full px-4 py-2 text-sm text-zinc-300 hover:bg-white/10"
                      onClick={() => {
                        setMenuOpen(false);
                        setShowSchemaEditor(true);
                      }}
                    >
                      <Edit className="w-4 h-4" />
                      Edit Schema
                    </button>
                    <button className="flex items-center gap-2 w-full px-4 py-2 text-sm text-zinc-300 hover:bg-white/10">
                      <Download className="w-4 h-4" />
                      Export Schema
                    </button>
                    <button className="flex items-center gap-2 w-full px-4 py-2 text-sm text-zinc-300 hover:bg-white/10">
                      <Share2 className="w-4 h-4" />
                      Share
                    </button>
                    <button className="flex items-center gap-2 w-full px-4 py-2 text-sm text-zinc-300 hover:bg-white/10">
                      <Archive className="w-4 h-4" />
                      Archive
                    </button>
                    <hr className="my-1 border-white/10" />
                    <button
                      className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-400 hover:bg-white/10"
                      onClick={() => {
                        setMenuOpen(false);
                        setShowDeleteConfirm(true);
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

        {/* Info banner when no data generated */}
        {(!dataset.row_count || dataset.row_count === 0) && (
          <Card className="bg-gradient-to-br from-teal-500/10 via-emerald-500/10 to-cyan-500/10 border-teal-500/30">
            <CardContent className="py-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-white mb-1">Ready to Generate Data</h3>
                  <p className="text-sm text-zinc-400 font-medium">
                    Your schema is configured. Use the "Generate Data" button above to create synthetic data.
                    You can generate up to {formatNumber(maxRows)} rows with your {user?.subscription_tier || 'current'} plan.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Schema */}
        <Card glass>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5 text-teal-400" />
                Schema Definition
              </CardTitle>
              <Badge variant="outline" className="text-xs">
                {dataset.schema_definition?.fields?.length || 0} fields
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {(!dataset.schema_definition?.fields || dataset.schema_definition.fields.length === 0) ? (
              <div className="text-center py-8">
                <Database className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
                <p className="text-zinc-400 font-medium">No schema fields defined</p>
              </div>
            ) : (
              <div className="space-y-2">
                {dataset.schema_definition.fields.map((field: any, index: number) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500/20 to-emerald-500/20 flex items-center justify-center">
                      <Database className="w-4 h-4 text-teal-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-white">{field.name}</span>
                        <Badge variant="outline" className="text-xs font-medium bg-white/5">
                          {field.data_type || field.type || 'string'}
                        </Badge>
                        {field.required && (
                          <Badge variant="default" className="text-xs bg-amber-500/20 text-amber-400 border-amber-500/30">
                            Required
                          </Badge>
                        )}
                      </div>
                      {field.description && (
                        <p className="text-sm font-medium text-zinc-400 mt-1 truncate">{field.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Generation Jobs for this Dataset */}
        <Card glass>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-teal-400" />
                Generation Jobs
              </CardTitle>
              <Link href="/jobs">
                <Button variant="ghost" size="sm" className="text-xs text-zinc-400 hover:text-white">
                  View All Jobs
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {isLoadingJobs ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
              </div>
            ) : !datasetJobs || datasetJobs.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
                <p className="text-zinc-400 font-medium">No jobs yet</p>
                <p className="text-xs text-zinc-500 mt-1">Generate data to see jobs here</p>
              </div>
            ) : (
              <div className="space-y-2">
                {datasetJobs.slice(0, 10).map((job: any) => (
                  <div
                    key={job.id}
                    className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      job.status === 'completed' ? 'bg-green-500/20' :
                      job.status === 'failed' ? 'bg-red-500/20' :
                      job.status === 'processing' || job.status === 'running' ? 'bg-teal-500/20' :
                      'bg-zinc-500/20'
                    }`}>
                      {job.status === 'completed' ? (
                        <Play className="w-4 h-4 text-green-400" />
                      ) : job.status === 'failed' ? (
                        <Trash2 className="w-4 h-4 text-red-400" />
                      ) : job.status === 'processing' || job.status === 'running' ? (
                        <Loader2 className="w-4 h-4 text-teal-400 animate-spin" />
                      ) : (
                        <Clock className="w-4 h-4 text-zinc-400" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white">
                          {formatNumber(job.row_count || 0)} rows
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {(job.output_format || 'csv').toUpperCase()}
                        </Badge>
                        <StatusBadge status={job.status} />
                      </div>
                      <p className="text-xs text-zinc-500 mt-0.5">
                        {formatDate(job.created_at)}
                        {job.completed_at && ` • Completed ${formatDate(job.completed_at)}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      {job.status === 'completed' && (
                        <Button
                          variant="gradient"
                          size="sm"
                          onClick={() => handleDownloadJob(job.id)}
                          className="text-xs"
                        >
                          <Download className="w-3.5 h-3.5 mr-1" />
                          Download
                        </Button>
                      )}
                      <Link href={`/jobs/${job.id}`}>
                        <Button variant="ghost" size="sm" className="text-xs text-zinc-400">
                          Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Generate Modal */}
        {showGenerateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <Card glass className="w-full max-w-lg border border-white/10 shadow-2xl">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  Generate Data
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                <p className="text-sm text-zinc-400 font-medium">
                  Generate synthetic data based on your <span className="text-zinc-200">"{dataset.name}"</span> schema ({dataset.schema_definition?.fields?.length || 0} fields).
                </p>

                {/* Row count input */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Number of Rows
                  </label>
                  <input
                    type="number"
                    min="1"
                    max={maxRows}
                    value={rowCount}
                    onChange={(e) => setRowCount(e.target.value)}
                    placeholder="Enter any number..."
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-lg font-medium focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  />
                  <p className="text-xs font-medium text-zinc-500 mt-1.5">
                    Maximum: {formatNumber(maxRows)} rows ({user?.subscription_tier || 'free'} tier) — type any number
                  </p>
                </div>

                {/* Quick select buttons */}
                <div className="flex flex-wrap gap-2">
                  {[100, 500, 1000, 5000, 10000, 50000, 100000, 500000].filter(n => n <= maxRows).map((num) => (
                    <button
                      key={num}
                      onClick={() => setRowCount(String(num))}
                      className={`px-3 py-1.5 text-sm font-medium rounded-lg border transition-all ${
                        rowCount === String(num)
                          ? 'border-teal-500 bg-teal-500/10 text-teal-400'
                          : 'border-white/10 bg-white/5 text-zinc-400 hover:border-white/20 hover:text-zinc-300'
                      }`}
                    >
                      {formatNumber(num)}
                    </button>
                  ))}
                </div>

                {/* Warning for large datasets */}
                {parseInt(rowCount) > 50000 && (
                  <div className="flex items-start gap-2 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                    <Clock className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-amber-300/80">
                      Large datasets (&gt;50K rows) may take several minutes to generate. You'll be redirected to the job tracker.
                    </p>
                  </div>
                )}

                <div className="flex gap-3 pt-1">
                  <Button
                    variant="outline"
                    onClick={() => setShowGenerateModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="gradient"
                    onClick={handleGenerate}
                    loading={generateData.isPending}
                    className="flex-1"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate {formatNumber(parseInt(rowCount) || 0)} Rows
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Delete Confirmation */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <Card glass className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Delete Dataset</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-zinc-300 font-medium">
                  Are you sure you want to delete "{dataset.name}"? This action cannot be undone
                  and will delete all associated generation jobs.
                </p>
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    loading={deleteDataset.isPending}
                    className="flex-1"
                  >
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Schema Editor Modal */}
        {showSchemaEditor && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 overflow-y-auto">
            <Card glass className="w-full max-w-3xl my-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5 text-teal-400" />
                  Edit Schema
                </CardTitle>
              </CardHeader>
              <CardContent>
                <SchemaEditor
                  initialFields={dataset.schema_definition?.fields || []}
                  onSave={handleSaveSchema}
                  onCancel={() => setShowSchemaEditor(false)}
                />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Data Preview Modal */}
        {showPreview && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 overflow-y-auto">
            <Card glass className="w-full max-w-6xl my-8">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <TableIcon className="w-5 h-5 text-teal-400" />
                    Data Preview
                  </CardTitle>
                  <Button variant="ghost" size="sm" onClick={() => setShowPreview(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {previewData.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-white/10">
                          {Object.keys(previewData[0]).map((key) => (
                            <th key={key} className="px-4 py-3 text-left text-zinc-400 font-medium">
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {previewData.map((row, idx) => (
                          <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                            {Object.values(row).map((value: any, cellIdx) => (
                              <td key={cellIdx} className="px-4 py-3 text-zinc-300 font-mono text-xs">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="text-xs text-zinc-500 mt-4 text-center">
                      Showing {previewData.length} sample rows. Generate full dataset to get more data.
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-zinc-400">No preview data available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
