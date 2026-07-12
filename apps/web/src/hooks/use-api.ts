import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { getAPI } from '@synthesize/api-client';
import type {
  User,
  Dataset,
  GenerationJob,
  Organization,
  Subscription,
  SubscriptionPlan,
  UsageStats,
  APIKey,
  Webhook,
  PaginatedResponse,
  CreateDatasetRequest,
  CreateDatasetFromDescriptionRequest,
  UpdateDatasetRequest,
  GenerateDataRequest,
  CreateOrganizationRequest,
  CreateAPIKeyRequest,
  CreateWebhookRequest,
  OrganizationInvite,
  Notification,
  DatasetTemplate,
  DatasetWithJobResponse,
} from '@synthesize/types';

// =============================================================================
// USER HOOKS
// =============================================================================

export function useCurrentUser(options?: Partial<UseQueryOptions<User>>) {
  return useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => getAPI().getCurrentUser(),
    ...options,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<User>) => getAPI().updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
    },
  });
}

export function useUserStats() {
  return useQuery({
    queryKey: ['user', 'stats'],
    queryFn: () => getAPI().getUserStats(),
  });
}

export function useNotifications(page = 1, perPage = 20) {
  return useQuery({
    queryKey: ['notifications', page, perPage],
    queryFn: () => getAPI().getNotifications(page, perPage),
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

// =============================================================================
// DATASET HOOKS
// =============================================================================

export function useDatasets(params?: { page?: number; per_page?: number; status?: string; search?: string }) {
  return useQuery({
    queryKey: ['datasets', params],
    queryFn: () => getAPI().getDatasets(params),
  });
}

export function useDataset(id: string, options?: Partial<UseQueryOptions<Dataset>>) {
  return useQuery({
    queryKey: ['datasets', id],
    queryFn: () => getAPI().getDataset(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateDataset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateDatasetFromDescriptionRequest) => getAPI().createDatasetFromDescription(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
    },
  });
}

export function useUpdateDataset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateDatasetRequest }) => getAPI().updateDataset(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      queryClient.invalidateQueries({ queryKey: ['datasets', id] });
    },
  });
}

export function useDeleteDataset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().deleteDataset(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
    },
  });
}

export function useDuplicateDataset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().duplicateDataset(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
    },
  });
}

export function useDatasetTemplates() {
  return useQuery({
    queryKey: ['datasets', 'templates'],
    queryFn: async () => {
      const templates = await getAPI().getTemplates();
      return templates || [];
    },
  });
}

export function usePreviewGeneration() {
  return useMutation({
    mutationFn: ({ datasetId, rows }: { datasetId: string; rows?: number }) =>
      getAPI().previewGeneration(datasetId, rows),
  });
}

export function useGenerateData() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ datasetId, data }: { datasetId: string; data: GenerateDataRequest }) =>
      getAPI().generateData(datasetId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['user', 'stats'] });
      queryClient.invalidateQueries({ queryKey: ['dataset-jobs'] });
    },
  });
}

export function useDatasetJobs(datasetId: string) {
  return useQuery({
    queryKey: ['dataset-jobs', datasetId],
    queryFn: () => getAPI().getDatasetJobs(datasetId),
    enabled: !!datasetId,
  });
}

// =============================================================================
// JOB HOOKS
// =============================================================================

export function useJobs(params?: { page?: number; per_page?: number; status?: string }) {
  return useQuery({
    queryKey: ['jobs', params],
    queryFn: () => getAPI().getJobs(params),
  });
}

export function useJob(id: string, options?: Partial<UseQueryOptions<GenerationJob>>) {
  return useQuery({
    queryKey: ['jobs', id],
    queryFn: () => getAPI().getJob(id),
    enabled: !!id,
    ...options,
  });
}

export function useJobStatus(id: string, enabled = true) {
  return useQuery({
    queryKey: ['jobs', id, 'status'],
    queryFn: () => getAPI().getJobStatus(id),
    enabled: !!id && enabled,
    refetchInterval: (query) => {
      const status = query?.state?.data?.status;
      if (status === 'completed' || status === 'failed' || status === 'cancelled' || status === 'canceled') {
        return false;
      }
      return 3000; // Poll every 3 seconds while in progress
    },
  });
}

export function useCancelJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().cancelJob(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['jobs', id] });
    },
  });
}

export function useRetryJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().retryJob(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });
}

export function useDeleteJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().deleteJob(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });
}

export function useJobStats() {
  return useQuery({
    queryKey: ['jobs', 'stats'],
    queryFn: () => getAPI().getJobStats(),
  });
}

// =============================================================================
// ORGANIZATION HOOKS
// =============================================================================

export function useOrganizations() {
  // Check if user is authenticated before making the request
  const isAuthenticated = typeof window !== 'undefined' && !!localStorage.getItem('access_token');
  
  return useQuery({
    queryKey: ['organizations'],
    queryFn: () => getAPI().getOrganizations(),
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: isAuthenticated, // Only run query if user is authenticated
  });
}

export function useOrganization(id: string, options?: Partial<UseQueryOptions<Organization>>) {
  return useQuery({
    queryKey: ['organizations', id],
    queryFn: () => getAPI().getOrganization(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateOrganizationRequest) => getAPI().createOrganization(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}

export function useUpdateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateOrganizationRequest> }) =>
      getAPI().updateOrganization(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      queryClient.invalidateQueries({ queryKey: ['organizations', id] });
    },
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().deleteOrganization(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}

export function useOrganizationMembers(orgId: string) {
  return useQuery({
    queryKey: ['organizations', orgId, 'members'],
    queryFn: () => getAPI().getOrganizationMembers(orgId),
    enabled: !!orgId,
  });
}

export function useOrganizationInvites(orgId: string) {
  return useQuery({
    queryKey: ['organizations', orgId, 'invites'],
    queryFn: () => getAPI().getInvites(orgId),
    enabled: !!orgId,
  });
}

export function usePendingInvites() {
  return useQuery({
    queryKey: ['invites', 'pending'],
    queryFn: () => getAPI().getPendingInvites(),
  });
}

// Alias for usePendingInvites
export function useMyInvites() {
  return usePendingInvites();
}

export function useSendInvite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orgId, email, role }: { orgId: string; email: string; role: string }) =>
      getAPI().sendInvite(orgId, { email, role: role as any }),
    onSuccess: (_, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ['organizations', orgId, 'invites'] });
    },
  });
}

export function useCancelInvite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orgId, inviteId }: { orgId: string; inviteId: string }) =>
      getAPI().cancelInvite(orgId, inviteId),
    onSuccess: (_, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ['organizations', orgId, 'invites'] });
    },
  });
}

export function useUpdateMemberRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orgId, memberId, role }: { orgId: string; memberId: string; role: string }) =>
      getAPI().updateMemberRole(orgId, memberId, role as any),
    onSuccess: (_, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ['organizations', orgId, 'members'] });
    },
  });
}

export function useRemoveMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orgId, memberId }: { orgId: string; memberId: string }) =>
      getAPI().removeMember(orgId, memberId),
    onSuccess: (_, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ['organizations', orgId, 'members'] });
    },
  });
}

export function useLeaveOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orgId: string) => getAPI().leaveOrganization(orgId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}

export function useAcceptInvite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (inviteId: string) => getAPI().acceptInvite(inviteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invites'] });
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}

export function useDeclineInvite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (inviteId: string) => getAPI().declineInvite(inviteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invites'] });
    },
  });
}

// =============================================================================
// SUBSCRIPTION HOOKS
// =============================================================================

export function useSubscriptionPlans() {
  return useQuery({
    queryKey: ['subscriptions', 'plans'],
    queryFn: async () => {
      try {
        return await getAPI().getPlans();
      } catch (error) {
        console.error('Failed to fetch subscription plans:', error);
        return [];
      }
    },
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCurrentSubscription() {
  return useQuery({
    queryKey: ['subscriptions', 'current'],
    queryFn: () => getAPI().getCurrentSubscription(),
  });
}

export function useUsage() {
  return useQuery({
    queryKey: ['subscriptions', 'usage'],
    queryFn: () => getAPI().getUsage(),
  });
}

export function useCheckout() {
  return useMutation({
    mutationFn: ({ planId, annual, couponCode }: { planId: string; annual?: boolean; couponCode?: string }) =>
      getAPI().checkout(planId, annual, couponCode),
  });
}

export function useBillingPortal() {
  return useMutation({
    mutationFn: () => getAPI().getPortalUrl(),
  });
}

export function useCancelSubscription() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => getAPI().cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
    },
  });
}

export function useInvoices(page = 1, perPage = 20) {
  return useQuery({
    queryKey: ['subscriptions', 'invoices', page, perPage],
    queryFn: () => getAPI().getInvoices(page, perPage),
  });
}

export function usePaymentMethods() {
  return useQuery({
    queryKey: ['subscriptions', 'payment-methods'],
    queryFn: () => getAPI().getPaymentMethods(),
  });
}

// =============================================================================
// API KEY HOOKS
// =============================================================================

export function useAPIKeys() {
  return useQuery({
    queryKey: ['api-keys'],
    queryFn: () => getAPI().getAPIKeys(),
  });
}

export function useCreateAPIKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateAPIKeyRequest) => getAPI().createAPIKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
}

export function useDeleteAPIKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().deleteAPIKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
}

export function useRotateAPIKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().rotateAPIKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
}

// =============================================================================
// WEBHOOK HOOKS
// =============================================================================

export function useWebhooks() {
  return useQuery({
    queryKey: ['webhooks'],
    queryFn: () => getAPI().getWebhooks(),
  });
}

export function useWebhook(id: string) {
  return useQuery({
    queryKey: ['webhooks', id],
    queryFn: () => getAPI().getWebhook(id),
    enabled: !!id,
  });
}

export function useCreateWebhook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateWebhookRequest) => getAPI().createWebhook(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
  });
}

export function useUpdateWebhook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateWebhookRequest> }) =>
      getAPI().updateWebhook(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
  });
}

export function useDeleteWebhook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => getAPI().deleteWebhook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
  });
}

export function useTestWebhook() {
  return useMutation({
    mutationFn: ({ id, event }: { id: string; event: string }) =>
      getAPI().testWebhook(id, event as any),
  });
}

export function useWebhookDeliveries(webhookId: string, page = 1, perPage = 20) {
  return useQuery({
    queryKey: ['webhooks', webhookId, 'deliveries', page, perPage],
    queryFn: () => getAPI().getWebhookDeliveries(webhookId, page, perPage),
    enabled: !!webhookId,
  });
}
