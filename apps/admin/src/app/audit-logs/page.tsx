'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAuditLogs } from '@/hooks/use-admin-api';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import {
  Search,
  FileText,
  Loader2,
  ChevronLeft,
  ChevronRight,
  User,
  Database,
  Play,
  Key,
  Settings,
} from 'lucide-react';

const ACTION_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  user: User,
  dataset: Database,
  job: Play,
  api_key: Key,
  settings: Settings,
};

export default function AuditLogsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  const { data, isLoading } = useAuditLogs({
    page,
    per_page: 50,
  });

  const logs = data?.items || [];
  const totalPages = Math.ceil((data?.total || 0) / 50);

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Filters */}
        <Card>
          <CardContent className="py-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <Input
                    placeholder="Search audit logs..."
                    className="pl-10"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Audit Logs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Audit Logs ({data?.total || 0})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
              </div>
            ) : logs.length === 0 ? (
              <div className="text-center py-16">
                <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No audit logs</h3>
                <p className="text-gray-400">Activity will appear here as users interact with the platform</p>
              </div>
            ) : (
              <>
                <div className="divide-y divide-gray-700">
                  {logs.map((log) => {
                    const Icon = ACTION_ICONS[log.resource_type] || FileText;
                    return (
                      <div
                        key={log.id}
                        className="flex items-start gap-4 px-6 py-4 hover:bg-gray-700/30"
                      >
                        <div className="w-10 h-10 rounded-lg bg-gray-700 flex items-center justify-center flex-shrink-0">
                          <Icon className="w-5 h-5 text-gray-300" />
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <p className="text-white">
                                <span className="font-medium">{log.user_email || 'Unknown'}</span>{' '}
                                <span className="text-gray-400">{log.action}</span>{' '}
                                <span className="font-medium">{log.resource_type}</span>
                              </p>
                              {log.resource_id && (
                                <p className="text-sm text-gray-500 mt-0.5">
                                  Resource ID: {log.resource_id}
                                </p>
                              )}
                              {log.metadata && (
                                <p className="text-sm text-gray-400 mt-1">
                                  {typeof log.metadata === 'string'
                                    ? log.metadata
                                    : JSON.stringify(log.metadata)}
                                </p>
                              )}
                            </div>
                            <div className="text-right flex-shrink-0">
                              <p className="text-sm text-gray-400">
                                {formatRelativeTime(log.created_at)}
                              </p>
                              <p className="text-xs text-gray-500 mt-0.5">{log.ip_address}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-6 py-4 border-t border-gray-700">
                    <p className="text-sm text-gray-400">
                      Showing {(page - 1) * 50 + 1} to {Math.min(page * 50, data?.total || 0)} of{' '}
                      {data?.total || 0} logs
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
    </AdminLayout>
  );
}
