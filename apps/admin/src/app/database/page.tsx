'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAPI } from '@synthesize/api-client';
import { formatNumber, formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Database,
  Table,
  Users,
  CreditCard,
  FileText,
  Zap,
  HardDrive,
  RefreshCw,
  Search,
  ChevronRight,
  Loader2,
  Activity,
  BarChart3,
  Clock,
  CheckCircle,
  AlertTriangle,
  Flag,
  Key,
  Webhook,
  Building2,
  MessageSquare,
} from 'lucide-react';

interface TableStats {
  name: string;
  row_count: number;
  size_bytes: number;
  last_modified?: string;
}

interface DatabaseStats {
  total_tables: number;
  total_rows: number;
  database_size: string;
  tables: TableStats[];
}

export default function DatabasePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  const { data: stats, isLoading, refetch, isRefetching } = useQuery<DatabaseStats>({
    queryKey: ['admin', 'database-stats'],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/database/stats');
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fallback static data if API doesn't have this endpoint yet
  const defaultStats: DatabaseStats = {
    total_tables: 15,
    total_rows: 0,
    database_size: 'Calculating...',
    tables: [
      { name: 'users', row_count: 0, size_bytes: 0 },
      { name: 'organizations', row_count: 0, size_bytes: 0 },
      { name: 'organization_members', row_count: 0, size_bytes: 0 },
      { name: 'datasets', row_count: 0, size_bytes: 0 },
      { name: 'dataset_columns', row_count: 0, size_bytes: 0 },
      { name: 'generation_jobs', row_count: 0, size_bytes: 0 },
      { name: 'generation_requests', row_count: 0, size_bytes: 0 },
      { name: 'subscriptions', row_count: 0, size_bytes: 0 },
      { name: 'subscription_plans', row_count: 0, size_bytes: 0 },
      { name: 'invoices', row_count: 0, size_bytes: 0 },
      { name: 'api_keys', row_count: 0, size_bytes: 0 },
      { name: 'webhooks', row_count: 0, size_bytes: 0 },
      { name: 'feature_flags', row_count: 0, size_bytes: 0 },
      { name: 'audit_logs', row_count: 0, size_bytes: 0 },
      { name: 'customer_queries', row_count: 0, size_bytes: 0 },
    ],
  };

  const tableData = stats?.tables || defaultStats.tables;
  
  const filteredTables = tableData.filter(t => 
    t.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getTableIcon = (tableName: string) => {
    const icons: Record<string, React.ComponentType<{ className?: string }>> = {
      users: Users,
      organizations: Building2,
      organization_members: Users,
      datasets: FileText,
      dataset_columns: Table,
      generation_jobs: Zap,
      generation_requests: Activity,
      subscriptions: CreditCard,
      subscription_plans: CreditCard,
      invoices: FileText,
      api_keys: Key,
      webhooks: Webhook,
      feature_flags: Flag,
      audit_logs: Clock,
      customer_queries: MessageSquare,
    };
    return icons[tableName] || Table;
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <AdminLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium text-white">Database Management</h1>
            <p className="text-gray-400 mt-1">View database tables and statistics</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              disabled={isRefetching}
              className="border-gray-700 hover:bg-white/5"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefetching ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="admin-card">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-teal-500/10">
                  <Database className="w-6 h-6 text-teal-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Total Tables</p>
                  <p className="text-2xl font-semibold text-white">
                    {stats?.total_tables || defaultStats.total_tables}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="admin-card">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-blue-500/10">
                  <BarChart3 className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Total Rows</p>
                  <p className="text-2xl font-semibold text-white">
                    {formatNumber(stats?.total_rows || 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="admin-card">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-purple-500/10">
                  <HardDrive className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Database Size</p>
                  <p className="text-2xl font-semibold text-white">
                    {stats?.database_size || defaultStats.database_size}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search tables..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white/5 border-white/10"
          />
        </div>

        {/* Tables Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-teal-500 mb-4" />
            <p className="text-gray-400">Loading database tables...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTables.map((table) => {
              const Icon = getTableIcon(table.name);
              return (
                <Card key={table.name} className="admin-card hover:border-white/20 transition-colors cursor-pointer group">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5 group-hover:bg-teal-500/10 transition-colors">
                          <Icon className="w-5 h-5 text-gray-400 group-hover:text-teal-400 transition-colors" />
                        </div>
                        <div>
                          <h3 className="font-medium text-white">{table.name}</h3>
                          <p className="text-sm text-gray-500">
                            {formatNumber(table.row_count)} rows
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-white transition-colors" />
                    </div>
                    <div className="mt-4 flex items-center justify-between text-sm">
                      <span className="text-gray-500">Size</span>
                      <span className="text-gray-400">{formatBytes(table.size_bytes)}</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Database Actions */}
        <Card className="admin-card">
          <CardHeader>
            <CardTitle className="text-white">Database Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                variant="outline"
                className="h-auto py-4 border-white/10 hover:bg-white/5"
                onClick={() => toast.info('Backup functionality coming soon')}
              >
                <div className="text-left">
                  <div className="flex items-center gap-2 mb-1">
                    <HardDrive className="w-4 h-4 text-teal-400" />
                    <span className="font-medium text-white">Create Backup</span>
                  </div>
                  <p className="text-xs text-gray-400">Export database snapshot</p>
                </div>
              </Button>
              
              <Button
                variant="outline"
                className="h-auto py-4 border-white/10 hover:bg-white/5"
                onClick={() => toast.info('Vacuum functionality coming soon')}
              >
                <div className="text-left">
                  <div className="flex items-center gap-2 mb-1">
                    <RefreshCw className="w-4 h-4 text-blue-400" />
                    <span className="font-medium text-white">Run VACUUM</span>
                  </div>
                  <p className="text-xs text-gray-400">Reclaim storage space</p>
                </div>
              </Button>
              
              <Button
                variant="outline"
                className="h-auto py-4 border-white/10 hover:bg-white/5"
                onClick={() => toast.info('Analyze functionality coming soon')}
              >
                <div className="text-left">
                  <div className="flex items-center gap-2 mb-1">
                    <BarChart3 className="w-4 h-4 text-purple-400" />
                    <span className="font-medium text-white">Run ANALYZE</span>
                  </div>
                  <p className="text-xs text-gray-400">Update table statistics</p>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}
