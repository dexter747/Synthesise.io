import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { getAPI } from '@synthesize/api-client';
import type {
  User,
  AdminDashboard,
  AdminAnalytics,
  FeatureFlag,
  AuditLog,
  SystemHealth,
  PaginatedResponse,
} from '@synthesize/types';

// =============================================================================
// ADMIN DASHBOARD
// =============================================================================

export function useAdminDashboard() {
  return useQuery({
    queryKey: ['admin', 'dashboard'],
    queryFn: () => getAPI().getAdminDashboard(),
    refetchInterval: 60000, // Refresh every minute
  });
}

export function useAdminAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: ['admin', 'analytics', period],
    queryFn: () => getAPI().getAdminAnalytics(period),
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['admin', 'health'],
    queryFn: () => getAPI().getSystemHealth(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

// =============================================================================
// USER MANAGEMENT
// =============================================================================

export function useAdminUsers(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  role?: string;
  status?: string;
}) {
  return useQuery({
    queryKey: ['admin', 'users', params],
    queryFn: () => getAPI().getAdminUsers(params),
  });
}

export function useAdminUserAction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, action }: { userId: string; action: 'suspend' | 'unsuspend' | 'verify' | 'delete' }) =>
      getAPI().adminUserAction(userId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });
}

// =============================================================================
// FEATURE FLAGS
// =============================================================================

export function useFeatureFlags() {
  return useQuery({
    queryKey: ['admin', 'feature-flags'],
    queryFn: () => getAPI().getFeatureFlags(),
  });
}

export function useCreateFeatureFlag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<FeatureFlag>) => getAPI().createFeatureFlag(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'feature-flags'] });
    },
  });
}

export function useUpdateFeatureFlag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FeatureFlag> }) =>
      getAPI().updateFeatureFlag(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'feature-flags'] });
    },
  });
}

export function useDeleteFeatureFlag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().deleteFeatureFlag(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'feature-flags'] });
    },
  });
}

// =============================================================================
// AUDIT LOGS
// =============================================================================

export function useAuditLogs(params?: {
  page?: number;
  per_page?: number;
  user_id?: string;
  action?: string;
  resource_type?: string;
  start_date?: string;
  end_date?: string;
}) {
  return useQuery({
    queryKey: ['admin', 'audit-logs', params],
    queryFn: () => getAPI().getAuditLogs(params),
  });
}

// =============================================================================
// CUSTOMER QUERIES
// =============================================================================

export function useCustomerQueries(params?: {
  page?: number;
  per_page?: number;
  status?: string;
  category?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}) {
  return useQuery({
    queryKey: ['admin', 'customer-queries', params],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/queries', { params });
      return response.data;
    },
  });
}

export function useCustomerQueryStats() {
  return useQuery({
    queryKey: ['admin', 'customer-queries', 'stats'],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/queries/stats');
      return response.data;
    },
  });
}
// =============================================================================
// JOBS MANAGEMENT
// =============================================================================

export function useAdminJobs(params?: {
  page?: number;
  per_page?: number;
  status?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: ['admin', 'jobs', params],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/jobs', { params });
      return response.data;
    },
    refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
  });
}

// =============================================================================
// SERVER LOGS
// =============================================================================

export function useServerLogs(params?: {
  level?: string;
  source?: string;
  search?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ['admin', 'logs', params],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/admin/logs', { params });
      return response.data;
    },
  });
}

export function useDeleteLog() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (logId: string) => {
      const api = getAPI();
      const response = await (api as any).client.delete(`/admin/logs/${logId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'logs'] });
    },
  });
}
export function useCustomerQueryDetail(queryId: string) {
  return useQuery({
    queryKey: ['admin', 'customer-queries', queryId],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get(`/admin/queries/${queryId}`);
      return response.data;
    },
    enabled: !!queryId,
  });
}

export function useUpdateCustomerQuery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ queryId, data }: { queryId: string; data: { status?: string; admin_notes?: string } }) => {
      const api = getAPI();
      const response = await (api as any).client.patch(`/admin/queries/${queryId}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'customer-queries'] });
    },
  });
}

export function useDeleteCustomerQuery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (queryId: string) => {
      const api = getAPI();
      const response = await (api as any).client.delete(`/admin/queries/${queryId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'customer-queries'] });
    },
  });
}

export function useBulkQueryAction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ queryIds, action }: { queryIds: string[]; action: string }) => {
      const api = getAPI();
      const response = await (api as any).client.post('/admin/queries/bulk-action', {
        query_ids: queryIds,
        action,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'customer-queries'] });
    },
  });
}
