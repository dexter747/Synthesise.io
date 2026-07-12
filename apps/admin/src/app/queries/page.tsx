'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useCustomerQueries, useCustomerQueryStats, useUpdateCustomerQuery, useDeleteCustomerQuery, useBulkQueryAction } from '@/hooks/use-admin-api';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Search,
  MessageSquare,
  MoreVertical,
  Mail,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Filter,
  RefreshCw,
  Eye,
  CheckCircle,
  Clock,
  Archive,
  Trash2,
  Phone,
  Building2,
  User,
  XCircle,
  Send,
  Inbox,
  TrendingUp,
  AlertCircle,
} from 'lucide-react';

interface CustomerQuery {
  id: string;
  name: string;
  email: string;
  company?: string;
  phone?: string;
  subject: string;
  message: string;
  category: string;
  status: 'new' | 'read' | 'responded' | 'closed';
  admin_notes?: string;
  responded_at?: string;
  created_at: string;
  updated_at: string;
}

const statusOptions = [
  { value: '', label: 'All Status' },
  { value: 'new', label: 'New' },
  { value: 'read', label: 'Read' },
  { value: 'responded', label: 'Responded' },
  { value: 'closed', label: 'Closed' },
];

const categoryOptions = [
  { value: '', label: 'All Categories' },
  { value: 'general', label: 'General' },
  { value: 'sales', label: 'Sales' },
  { value: 'support', label: 'Support' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'other', label: 'Other' },
];

export default function CustomerQueriesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selectedQuery, setSelectedQuery] = useState<CustomerQuery | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [adminNotes, setAdminNotes] = useState('');

  const { data, isLoading, refetch } = useCustomerQueries({
    page,
    per_page: 20,
    search: search || undefined,
    status: statusFilter || undefined,
    category: categoryFilter || undefined,
  });

  const { data: stats } = useCustomerQueryStats();
  const updateQuery = useUpdateCustomerQuery();
  const deleteQuery = useDeleteCustomerQuery();
  const bulkAction = useBulkQueryAction();

  const queries = data?.items || [];
  const totalPages = data?.total_pages || 1;

  const handleStatusChange = async (queryId: string, newStatus: string) => {
    try {
      await updateQuery.mutateAsync({ queryId, data: { status: newStatus } });
      toast.success(`Status updated to ${newStatus}`);
      if (selectedQuery?.id === queryId) {
        setSelectedQuery({ ...selectedQuery, status: newStatus as CustomerQuery['status'] });
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to update status');
    }
  };

  const handleSaveNotes = async () => {
    if (!selectedQuery) return;
    try {
      await updateQuery.mutateAsync({ queryId: selectedQuery.id, data: { admin_notes: adminNotes } });
      toast.success('Notes saved');
      setSelectedQuery({ ...selectedQuery, admin_notes: adminNotes });
    } catch (error: any) {
      toast.error(error.message || 'Failed to save notes');
    }
  };

  const handleDelete = async (queryId: string) => {
    if (!confirm('Are you sure you want to delete this query?')) return;
    try {
      await deleteQuery.mutateAsync(queryId);
      toast.success('Query deleted');
      if (selectedQuery?.id === queryId) {
        setSelectedQuery(null);
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete query');
    }
  };

  const handleBulkAction = async (action: string) => {
    if (selectedIds.length === 0) {
      toast.error('Please select at least one query');
      return;
    }
    try {
      await bulkAction.mutateAsync({ queryIds: selectedIds, action });
      toast.success(`Bulk action completed: ${action}`);
      setSelectedIds([]);
    } catch (error: any) {
      toast.error(error.message || 'Failed to perform bulk action');
    }
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === queries.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(queries.map((q: CustomerQuery) => q.id));
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const getStatusConfig = (status: string) => {
    const configs: Record<string, { bg: string; text: string; icon: typeof Inbox }> = {
      new: { bg: 'bg-teal-500/10', text: 'text-teal-400', icon: Inbox },
      read: { bg: 'bg-blue-500/10', text: 'text-blue-400', icon: Eye },
      responded: { bg: 'bg-green-500/10', text: 'text-green-400', icon: CheckCircle },
      closed: { bg: 'bg-gray-500/10', text: 'text-gray-400', icon: Archive },
    };
    return configs[status] || configs.new;
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      general: 'General',
      sales: 'Sales',
      support: 'Support',
      partnership: 'Partnership',
      other: 'Other',
    };
    return labels[category] || category;
  };

  return (
    <AdminLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Page Header */}
        <div className="page-header">
          <div>
            <h2 className="page-title">
              <span className="gradient-teal-text">Customer Queries</span>
            </h2>
            <p className="page-subtitle">Manage and respond to customer inquiries</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatsCard
            title="Total"
            value={stats?.total || 0}
            icon={MessageSquare}
            color="teal"
          />
          <StatsCard
            title="New"
            value={stats?.new || 0}
            icon={Inbox}
            color="teal"
            highlight
          />
          <StatsCard
            title="Read"
            value={stats?.read || 0}
            icon={Eye}
            color="blue"
          />
          <StatsCard
            title="Responded"
            value={stats?.responded || 0}
            icon={CheckCircle}
            color="green"
          />
          <StatsCard
            title="Closed"
            value={stats?.closed || 0}
            icon={Archive}
            color="gray"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Query List */}
          <div className="lg:col-span-2 space-y-4">
            {/* Filters */}
            <Card className="admin-card">
              <CardContent className="py-4">
                <div className="flex flex-wrap gap-4">
                  <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                      <Input
                        placeholder="Search queries..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="pl-10 bg-white/5 border-white/10"
                      />
                    </div>
                  </div>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 transition-all duration-200 appearance-none"
                  >
                    {statusOptions.map(opt => (
                      <option key={opt.value} value={opt.value} className="bg-gray-900">{opt.label}</option>
                    ))}
                  </select>
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 transition-all duration-200 appearance-none"
                  >
                    {categoryOptions.map(opt => (
                      <option key={opt.value} value={opt.value} className="bg-gray-900">{opt.label}</option>
                    ))}
                  </select>
                </div>

                {/* Bulk Actions */}
                {selectedIds.length > 0 && (
                  <div className="flex items-center gap-3 mt-4 pt-4 border-t border-white/5">
                    <span className="text-sm text-gray-400">{selectedIds.length} selected</span>
                    <Button size="sm" variant="outline" onClick={() => handleBulkAction('mark_read')}>
                      <Eye className="w-4 h-4 mr-1" /> Mark Read
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleBulkAction('mark_responded')}>
                      <CheckCircle className="w-4 h-4 mr-1" /> Mark Responded
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleBulkAction('close')}>
                      <Archive className="w-4 h-4 mr-1" /> Close
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => handleBulkAction('delete')}>
                      <Trash2 className="w-4 h-4 mr-1" /> Delete
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Query List */}
            <Card className="admin-card">
              {isLoading ? (
                <div className="flex items-center justify-center py-20">
                  <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
                </div>
              ) : queries.length === 0 ? (
                <div className="text-center py-20">
                  <MessageSquare className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">No queries found</h3>
                  <p className="text-gray-400">Customer queries will appear here</p>
                </div>
              ) : (
                <>
                  {/* Table Header */}
                  <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b border-white/5 text-xs font-medium text-gray-500 uppercase tracking-wide">
                    <div className="col-span-1 flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedIds.length === queries.length}
                        onChange={toggleSelectAll}
                        className="rounded border-white/20 bg-white/5 text-teal-500 focus:ring-teal-500"
                      />
                    </div>
                    <div className="col-span-4">Contact</div>
                    <div className="col-span-4">Subject</div>
                    <div className="col-span-2">Status</div>
                    <div className="col-span-1">Actions</div>
                  </div>

                  {/* Query Rows */}
                  {queries.map((query: CustomerQuery) => {
                    const statusConfig = getStatusConfig(query.status);
                    const StatusIcon = statusConfig.icon;
                    return (
                      <div
                        key={query.id}
                        className={`grid grid-cols-12 gap-4 px-6 py-4 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer ${
                          selectedQuery?.id === query.id ? 'bg-teal-500/5' : ''
                        }`}
                        onClick={() => {
                          setSelectedQuery(query);
                          setAdminNotes(query.admin_notes || '');
                        }}
                      >
                        <div className="col-span-1 flex items-center" onClick={e => e.stopPropagation()}>
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(query.id)}
                            onChange={() => toggleSelect(query.id)}
                            className="rounded border-white/20 bg-white/5 text-teal-500 focus:ring-teal-500"
                          />
                        </div>
                        <div className="col-span-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 flex items-center justify-center text-white font-medium text-sm">
                              {query.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="text-white font-medium">{query.name}</p>
                              <p className="text-gray-500 text-sm">{query.email}</p>
                            </div>
                          </div>
                        </div>
                        <div className="col-span-4 flex flex-col justify-center">
                          <p className="text-white text-sm truncate">{query.subject}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">
                              {getCategoryLabel(query.category)}
                            </span>
                            <span className="text-gray-600">•</span>
                            <span className="text-xs text-gray-500">
                              {formatRelativeTime(query.created_at)}
                            </span>
                          </div>
                        </div>
                        <div className="col-span-2 flex items-center">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${statusConfig.bg} ${statusConfig.text}`}>
                            <StatusIcon className="w-3.5 h-3.5" />
                            {query.status}
                          </span>
                        </div>
                        <div className="col-span-1 flex items-center justify-end" onClick={e => e.stopPropagation()}>
                          <button
                            onClick={() => handleDelete(query.id)}
                            className="p-2 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
                  <p className="text-sm text-gray-400">
                    Page {page} of {totalPages}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </div>

          {/* Query Detail Panel */}
          <div className="lg:col-span-1">
            <Card className="admin-card sticky top-6">
              {selectedQuery ? (
                <div className="divide-y divide-white/5">
                  <CardHeader className="pb-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg text-white">{selectedQuery.name}</CardTitle>
                        <p className="text-sm text-gray-400 mt-1">{formatDate(selectedQuery.created_at)}</p>
                      </div>
                      <button
                        onClick={() => setSelectedQuery(null)}
                        className="p-1 rounded-lg hover:bg-white/5 text-gray-400"
                      >
                        <XCircle className="w-5 h-5" />
                      </button>
                    </div>
                  </CardHeader>

                  <CardContent className="py-4 space-y-4">
                    {/* Contact Info */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-3 text-sm">
                        <Mail className="w-4 h-4 text-gray-500" />
                        <a href={`mailto:${selectedQuery.email}`} className="text-teal-400 hover:underline">
                          {selectedQuery.email}
                        </a>
                      </div>
                      {selectedQuery.phone && (
                        <div className="flex items-center gap-3 text-sm">
                          <Phone className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-300">{selectedQuery.phone}</span>
                        </div>
                      )}
                      {selectedQuery.company && (
                        <div className="flex items-center gap-3 text-sm">
                          <Building2 className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-300">{selectedQuery.company}</span>
                        </div>
                      )}
                    </div>

                    {/* Subject & Message */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-400">Subject</h4>
                      <p className="text-white">{selectedQuery.subject}</p>
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-400">Message</h4>
                      <p className="text-gray-300 text-sm whitespace-pre-wrap">{selectedQuery.message}</p>
                    </div>

                    {/* Status */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-400">Status</h4>
                      <select
                        value={selectedQuery.status}
                        onChange={(e) => handleStatusChange(selectedQuery.id, e.target.value)}
                        className="w-full px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 transition-all duration-200 appearance-none"
                      >
                        <option value="new" className="bg-gray-900">New</option>
                        <option value="read" className="bg-gray-900">Read</option>
                        <option value="responded" className="bg-gray-900">Responded</option>
                        <option value="closed" className="bg-gray-900">Closed</option>
                      </select>
                    </div>

                    {/* Admin Notes */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-400">Admin Notes</h4>
                      <textarea
                        value={adminNotes}
                        onChange={(e) => setAdminNotes(e.target.value)}
                        placeholder="Add internal notes..."
                        rows={3}
                        className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm focus:border-teal-500/50 focus:outline-none resize-none placeholder:text-gray-600"
                      />
                      <Button
                        size="sm"
                        onClick={handleSaveNotes}
                        disabled={updateQuery.isPending}
                        className="w-full bg-teal-500 hover:bg-teal-600"
                      >
                        {updateQuery.isPending ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <CheckCircle className="w-4 h-4 mr-2" />
                        )}
                        Save Notes
                      </Button>
                    </div>

                    {/* Quick Actions */}
                    <div className="space-y-2 pt-2">
                      <h4 className="text-sm font-medium text-gray-400">Quick Actions</h4>
                      <div className="grid grid-cols-2 gap-2">
                        <a
                          href={`mailto:${selectedQuery.email}?subject=Re: ${selectedQuery.subject}`}
                          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-teal-500/10 text-teal-400 hover:bg-teal-500/20 transition-colors text-sm font-medium"
                        >
                          <Send className="w-4 h-4" />
                          Reply
                        </a>
                        <button
                          onClick={() => handleDelete(selectedQuery.id)}
                          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors text-sm font-medium"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </CardContent>
                </div>
              ) : (
                <CardContent className="py-16 text-center">
                  <MessageSquare className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">Select a Query</h3>
                  <p className="text-gray-400 text-sm">Click on a query to view details and take actions</p>
                </CardContent>
              )}
            </Card>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}

// Stats Card Component
function StatsCard({
  title,
  value,
  icon: Icon,
  color,
  highlight = false,
}: {
  title: string;
  value: number;
  icon: typeof MessageSquare;
  color: 'teal' | 'blue' | 'green' | 'gray' | 'red';
  highlight?: boolean;
}) {
  const colorMap = {
    teal: 'from-teal-500/20 to-emerald-500/20 text-teal-400',
    blue: 'from-blue-500/20 to-indigo-500/20 text-blue-400',
    green: 'from-green-500/20 to-emerald-500/20 text-green-400',
    gray: 'from-gray-500/20 to-zinc-500/20 text-gray-400',
    red: 'from-red-500/20 to-pink-500/20 text-red-400',
  };

  return (
    <Card className={`admin-card overflow-hidden ${highlight ? 'ring-1 ring-teal-500/30' : ''}`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</p>
            <p className="text-2xl font-medium text-white mt-1">{value}</p>
          </div>
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colorMap[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
