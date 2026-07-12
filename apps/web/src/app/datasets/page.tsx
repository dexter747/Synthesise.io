'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { useDatasets, useDeleteDataset } from '@/hooks/use-api';
import { formatRelativeTime, debounce } from '@/lib/utils';
import Link from 'next/link';
import { toast } from 'sonner';
import {
  Plus,
  Search,
  Database,
  MoreVertical,
  Edit,
  Trash2,
  Copy,
  Play,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export default function DatasetsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  
  const { data, isLoading, refetch } = useDatasets({
    page,
    per_page: 10,
    search: search || undefined,
    status: statusFilter || undefined,
  });

  const deleteDataset = useDeleteDataset();

  const datasets = data?.items || [];
  const totalPages = Math.ceil((data?.total || 0) / (data?.per_page || 10));

  const handleSearch = debounce((value: string) => {
    setSearch(value);
    setPage(1);
  }, 300);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteDataset.mutateAsync(id);
      toast.success('Dataset deleted successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete dataset');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-medium text-white">Datasets</h1>
            <p className="text-zinc-400 mt-1">Manage your synthetic data schemas</p>
          </div>
          <Link href="/datasets/new">
            <Button variant="gradient">
              <Plus className="w-4 h-4 mr-2" />
              New Dataset
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <Card glass>
          <CardContent className="py-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                  <Input
                    placeholder="Search datasets..."
                    className="pl-10"
                    onChange={(e) => handleSearch(e.target.value)}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                {['', 'draft', 'active', 'archived'].map((status) => (
                  <Button
                    key={status}
                    variant={statusFilter === status ? 'gradient' : 'outline'}
                    size="sm"
                    onClick={() => {
                      setStatusFilter(status);
                      setPage(1);
                    }}
                  >
                    {status || 'All'}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Dataset List */}
        <Card glass>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
              </div>
            ) : datasets.length === 0 ? (
              <div className="text-center py-16">
                <Database className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No datasets found</h3>
                <p className="text-zinc-400 mb-6">
                  {search || statusFilter
                    ? 'Try adjusting your filters'
                    : 'Create your first dataset to get started'}
                </p>
                {!search && !statusFilter && (
                  <Link href="/datasets/new">
                    <Button variant="gradient">Create Dataset</Button>
                  </Link>
                )}
              </div>
            ) : (
              <>
                <div className="divide-y divide-white/5">
                  {datasets.map((dataset) => (
                    <DatasetRow
                      key={dataset.id}
                      dataset={dataset}
                      onDelete={() => handleDelete(dataset.id, dataset.name)}
                    />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
                    <p className="text-sm text-zinc-500">
                      Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, data?.total || 0)} of{' '}
                      {data?.total || 0} datasets
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

function DatasetRow({
  dataset,
  onDelete,
}: {
  dataset: any;
  onDelete: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="flex items-center gap-4 px-6 py-4 hover:bg-white/5 transition-colors">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
        <Database className="w-5 h-5 text-white" />
      </div>
      
      <div className="flex-1 min-w-0">
        <Link href={`/datasets/${dataset.id}`} className="block">
          <h3 className="font-medium text-white truncate hover:text-teal-400 transition-colors">
            {dataset.name}
          </h3>
        </Link>
        <p className="text-sm font-medium text-zinc-500">
          {dataset.schema_definition?.fields?.length || 0} fields
          {(dataset.row_count || 0) > 0 && ` • ${(dataset.row_count || 0).toLocaleString()} rows generated`}
          {' '}• Updated {formatRelativeTime(dataset.updated_at)}
        </p>
      </div>

      <div className="flex items-center gap-2">
        {(dataset.row_count || 0) === 0 && (
          <Link href={`/datasets/${dataset.id}?generate=true`}>
            <Button variant="gradient" size="sm" className="text-xs">
              <Play className="w-3.5 h-3.5 mr-1" />
              Generate
            </Button>
          </Link>
        )}
      </div>

      <StatusBadge status={dataset.status} />

      <div className="relative">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setMenuOpen(!menuOpen)}
          className="p-2"
        >
          <MoreVertical className="w-4 h-4" />
        </Button>

        {menuOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
            <div className="absolute right-0 mt-1 w-48 bg-zinc-900 rounded-lg shadow-lg border border-white/10 py-1 z-50">
              <Link
                href={`/datasets/${dataset.id}`}
                className="flex items-center gap-2 px-4 py-2 text-sm text-zinc-300 hover:bg-white/5"
                onClick={() => setMenuOpen(false)}
              >
                <Edit className="w-4 h-4" />
                View & Edit
              </Link>
              <Link
                href={`/datasets/${dataset.id}?generate=true`}
                className="flex items-center gap-2 px-4 py-2 text-sm text-teal-400 hover:bg-white/5"
                onClick={() => setMenuOpen(false)}
              >
                <Play className="w-4 h-4" />
                Generate Data
              </Link>
              <button
                className="flex items-center gap-2 w-full px-4 py-2 text-sm text-zinc-300 hover:bg-white/5"
                onClick={() => {
                  setMenuOpen(false);
                  // Handle duplicate
                }}
              >
                <Copy className="w-4 h-4" />
                Duplicate
              </button>
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
  );
}
