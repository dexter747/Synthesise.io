// =============================================================================
// SYNTHESIZE.IO - API CLIENT
// =============================================================================

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from "axios";
import type {
  User,
  AuthTokens,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  Organization,
  OrganizationMember,
  OrganizationInvite,
  CreateOrganizationRequest,
  InviteMemberRequest,
  OrganizationRole,
  Dataset,
  DatasetTemplate,
  CreateDatasetRequest,
  CreateDatasetFromDescriptionRequest,
  UpdateDatasetRequest,
  GenerateDataRequest,
  GenerationJob,
  DatasetWithJobResponse,
  JobStats,
  Subscription,
  SubscriptionPlan,
  UsageStats,
  Invoice,
  PaymentMethod,
  APIKey,
  APIKeyCreateResponse,
  CreateAPIKeyRequest,
  Webhook,
  WebhookDelivery,
  CreateWebhookRequest,
  WebhookEvent,
  Session,
  Notification,
  PaginatedResponse,
  APIError,
  AdminDashboard,
  AdminAnalytics,
  FeatureFlag,
  AuditLog,
  SystemHealth,
} from "@synthesize/types";

// =============================================================================
// ERROR HANDLING
// =============================================================================

export class APIClientError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = "APIClientError";
  }
}

// =============================================================================
// API CLIENT CLASS
// =============================================================================

export class SynthesizeAPI {
  private client: AxiosInstance;
  private refreshPromise: Promise<AuthTokens> | null = null;
  private onTokenRefresh?: (tokens: AuthTokens) => void;
  private onUnauthorized?: () => void;

  constructor(config?: {
    baseURL?: string;
    onTokenRefresh?: (tokens: AuthTokens) => void;
    onUnauthorized?: () => void;
  }) {
    const baseURL = config?.baseURL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    this.onTokenRefresh = config?.onTokenRefresh;
    this.onUnauthorized = config?.onUnauthorized;

    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<APIError>) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle 401 - Try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const tokens = await this.refreshAccessToken();
            if (tokens && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            this.onUnauthorized?.();
            throw refreshError;
          }
        }

        // Transform error
        const apiError = error.response?.data;
        throw new APIClientError(
          apiError?.code || "UNKNOWN_ERROR",
          apiError?.message || error.message || "An unexpected error occurred",
          error.response?.status || 500,
          apiError?.details
        );
      }
    );
  }

  // Token management - override these in your app
  private getAccessToken(): string | null {
    if (typeof window !== "undefined") {
      // Check for 30 minutes of inactivity (1800000 ms)
      const lastActivity = localStorage.getItem("token_last_activity");
      if (lastActivity) {
        const inactivityTime = Date.now() - parseInt(lastActivity);
        if (inactivityTime > 1800000) {
          // More than 30 minutes inactive - clear tokens
          this.clearTokens();
          return null;
        }
      }
      
      // Update last activity on each request
      const token = localStorage.getItem("access_token");
      if (token) {
        localStorage.setItem("token_last_activity", Date.now().toString());
      }
      return token;
    }
    return null;
  }

  private getRefreshToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("refresh_token");
    }
    return null;
  }

  setTokens(tokens: AuthTokens) {
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      // Set last activity timestamp for 30-minute inactivity timeout
      localStorage.setItem("token_last_activity", Date.now().toString());
    }
  }

  clearTokens() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("token_last_activity");
    }
  }

  private async refreshAccessToken(): Promise<AuthTokens | null> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    this.refreshPromise = this.client
      .post<{ tokens: AuthTokens }>("/auth/refresh", { refresh_token: refreshToken })
      .then((response) => {
        const tokens = response.data.tokens;
        this.setTokens(tokens);
        this.onTokenRefresh?.(tokens);
        return tokens;
      })
      .finally(() => {
        this.refreshPromise = null;
      });

    return this.refreshPromise;
  }

  // ===========================================================================
  // AUTHENTICATION
  // ===========================================================================

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>("/auth/login", data);
    // Backend returns 'token' not 'tokens'
    const tokens = (response.data as any).token || response.data.tokens;
    if (tokens) {
      this.setTokens({
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        token_type: tokens.token_type,
        expires_in: tokens.expires_in,
      });
    }
    return response.data;
  }

  async register(data: RegisterRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>("/auth/register", data);
    // Don't store tokens on registration - user needs to verify email first
    // They will get tokens when they log in after verification
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post("/auth/logout");
    this.clearTokens();
  }

  async logoutAll(): Promise<void> {
    await this.client.post("/auth/logout-all");
    this.clearTokens();
  }

  async forgotPassword(email: string): Promise<void> {
    await this.client.post("/auth/forgot-password", { email });
  }

  async resetPassword(token: string, password: string): Promise<void> {
    await this.client.post("/auth/reset-password", { token, password });
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.client.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  async verifyEmail(token: string): Promise<void> {
    await this.client.post("/auth/verify-email", { token });
  }

  async resendVerification(): Promise<void> {
    await this.client.post("/auth/resend-verification");
  }

  async getSessions(): Promise<Session[]> {
    const response = await this.client.get<{ sessions: Session[] }>("/auth/sessions");
    return response.data.sessions;
  }

  async revokeSession(sessionId: string): Promise<void> {
    await this.client.delete(`/auth/sessions/${sessionId}`);
  }

  getGoogleAuthUrl(): string {
    return `${this.client.defaults.baseURL}/auth/google`;
  }

  // ===========================================================================
  // USERS
  // ===========================================================================

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>("/users/me");
    return response.data;
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await this.client.put<User>("/users/me", data);
    return response.data;
  }

  async updatePreferences(preferences: Record<string, any>): Promise<void> {
    await this.client.put("/users/me/preferences", preferences);
  }

  async deleteAccount(): Promise<void> {
    await this.client.delete("/users/me");
    this.clearTokens();
  }

  async getUserStats(): Promise<UsageStats> {
    const response = await this.client.get<UsageStats>("/users/me/stats");
    return response.data;
  }

  async getUserActivity(page = 1, perPage = 20): Promise<PaginatedResponse<AuditLog>> {
    const response = await this.client.get<PaginatedResponse<AuditLog>>("/users/me/activity", {
      params: { page, per_page: perPage },
    });
    return response.data;
  }

  async getNotifications(page = 1, perPage = 20): Promise<PaginatedResponse<Notification>> {
    const response = await this.client.get<PaginatedResponse<Notification>>("/users/me/notifications", {
      params: { page, per_page: perPage },
    });
    return response.data;
  }

  async markNotificationRead(id: string): Promise<void> {
    await this.client.post(`/users/me/notifications/${id}/read`);
  }

  async markAllNotificationsRead(): Promise<void> {
    await this.client.post("/users/me/notifications/read-all");
  }

  // ===========================================================================
  // ORGANIZATIONS
  // ===========================================================================

  async getOrganizations(): Promise<Organization[]> {
    const response = await this.client.get<{ items: Organization[] }>("/users/me/organizations");
    return response.data.items;
  }

  async createOrganization(data: CreateOrganizationRequest): Promise<Organization> {
    const response = await this.client.post<Organization>("/organizations", data);
    return response.data;
  }

  async getOrganization(id: string): Promise<Organization> {
    const response = await this.client.get<Organization>(`/organizations/${id}`);
    return response.data;
  }

  async updateOrganization(id: string, data: Partial<CreateOrganizationRequest>): Promise<Organization> {
    const response = await this.client.put<Organization>(`/organizations/${id}`, data);
    return response.data;
  }

  async deleteOrganization(id: string): Promise<void> {
    await this.client.delete(`/organizations/${id}`);
  }

  async getOrganizationMembers(orgId: string): Promise<OrganizationMember[]> {
    const response = await this.client.get<{ members: OrganizationMember[] }>(`/organizations/${orgId}/members`);
    return response.data.members;
  }

  async updateMemberRole(orgId: string, memberId: string, role: OrganizationRole): Promise<void> {
    await this.client.put(`/organizations/${orgId}/members/${memberId}`, { role });
  }

  async removeMember(orgId: string, memberId: string): Promise<void> {
    await this.client.delete(`/organizations/${orgId}/members/${memberId}`);
  }

  async leaveOrganization(orgId: string): Promise<void> {
    await this.client.post(`/organizations/${orgId}/leave`);
  }

  async getInvites(orgId: string): Promise<OrganizationInvite[]> {
    const response = await this.client.get<{ invites: OrganizationInvite[] }>(`/organizations/${orgId}/invites`);
    return response.data.invites;
  }

  async sendInvite(orgId: string, data: InviteMemberRequest): Promise<OrganizationInvite> {
    const response = await this.client.post<OrganizationInvite>(`/organizations/${orgId}/invites`, data);
    return response.data;
  }

  async cancelInvite(orgId: string, inviteId: string): Promise<void> {
    await this.client.delete(`/organizations/${orgId}/invites/${inviteId}`);
  }

  async acceptInvite(inviteId: string): Promise<void> {
    await this.client.post(`/organizations/invites/${inviteId}/accept`);
  }

  async declineInvite(inviteId: string): Promise<void> {
    await this.client.post(`/organizations/invites/${inviteId}/decline`);
  }

  async getPendingInvites(): Promise<OrganizationInvite[]> {
    const response = await this.client.get<{ invites: OrganizationInvite[] }>("/users/me/invites");
    return response.data?.invites || [];
  }

  // ===========================================================================
  // DATASETS
  // ===========================================================================

  async getDatasets(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    search?: string;
    org_id?: string;
  }): Promise<PaginatedResponse<Dataset>> {
    const response = await this.client.get<PaginatedResponse<Dataset>>("/datasets", { params });
    return response.data;
  }

  async getDataset(id: string): Promise<Dataset> {
    const response = await this.client.get<Dataset>(`/datasets/${id}`);
    return response.data;
  }

  async createDataset(data: CreateDatasetRequest): Promise<Dataset> {
    const response = await this.client.post<Dataset>("/datasets", data);
    return response.data;
  }

  async createDatasetFromDescription(data: CreateDatasetFromDescriptionRequest): Promise<DatasetWithJobResponse> {
    const response = await this.client.post<DatasetWithJobResponse>("/datasets/generate", data);
    return response.data;
  }

  async updateDataset(id: string, data: UpdateDatasetRequest): Promise<Dataset> {
    const response = await this.client.put<Dataset>(`/datasets/${id}`, data);
    return response.data;
  }

  async deleteDataset(id: string): Promise<void> {
    await this.client.delete(`/datasets/${id}`);
  }

  async duplicateDataset(id: string): Promise<Dataset> {
    const response = await this.client.post<Dataset>(`/datasets/${id}/duplicate`);
    return response.data;
  }

  async getTemplates(): Promise<DatasetTemplate[]> {
    const response = await this.client.get<DatasetTemplate[]>("/datasets/templates");
    return response.data || [];
  }

  async createFromTemplate(templateId: string, name: string): Promise<Dataset> {
    const response = await this.client.post<Dataset>(`/datasets/from-template/${templateId}`, { name });
    return response.data;
  }

  async previewGeneration(datasetId: string, rows = 10): Promise<any[]> {
    const response = await this.client.post<{ preview: any[] }>(`/datasets/${datasetId}/preview`, { rows });
    return response.data.preview;
  }

  async generateData(datasetId: string, data: GenerateDataRequest): Promise<GenerationJob> {
    const response = await this.client.post<GenerationJob>(`/datasets/${datasetId}/generate`, data);
    return response.data;
  }

  async getDatasetJobs(datasetId: string): Promise<GenerationJob[]> {
    const response = await this.client.get<{ jobs: GenerationJob[] }>(`/datasets/${datasetId}/jobs`);
    return response.data.jobs;
  }

  // ===========================================================================
  // JOBS
  // ===========================================================================

  async getJobs(params?: {
    page?: number;
    per_page?: number;
    status?: string;
  }): Promise<PaginatedResponse<GenerationJob>> {
    const response = await this.client.get<PaginatedResponse<GenerationJob>>("/jobs", { params });
    return response.data;
  }

  async getJob(id: string): Promise<GenerationJob> {
    const response = await this.client.get<GenerationJob>(`/jobs/${id}`);
    return response.data;
  }

  async getJobStatus(id: string): Promise<{ status: string; progress: number }> {
    const response = await this.client.get<{ status: string; progress: number }>(`/jobs/${id}/status`);
    return response.data;
  }

  async cancelJob(id: string): Promise<void> {
    await this.client.post(`/jobs/${id}/cancel`);
  }

  async retryJob(id: string): Promise<GenerationJob> {
    const response = await this.client.post<GenerationJob>(`/jobs/${id}/retry`);
    return response.data;
  }

  async deleteJob(id: string): Promise<void> {
    await this.client.delete(`/jobs/${id}`);
  }

  getJobDownloadUrl(id: string): string {
    const token = this.getAccessToken();
    return `${this.client.defaults.baseURL}/jobs/${id}/download?token=${token}`;
  }

  async getJobPreview(id: string): Promise<any[]> {
    const response = await this.client.get<{ preview: any[] }>(`/jobs/${id}/preview`);
    return response.data.preview;
  }

  async getJobStats(): Promise<JobStats> {
    const response = await this.client.get<JobStats>("/jobs/stats");
    return response.data;
  }

  // ===========================================================================
  // SUBSCRIPTIONS
  // ===========================================================================

  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await this.client.get<SubscriptionPlan[]>("/subscriptions/plans");
    return response.data;
  }

  async getCurrentSubscription(): Promise<Subscription | null> {
    const response = await this.client.get<Subscription | null>("/subscriptions/current");
    return response.data;
  }

  async getUsage(): Promise<UsageStats> {
    const response = await this.client.get<UsageStats>("/subscriptions/usage");
    return response.data;
  }

  async checkout(planId: string, annual = false, couponCode?: string): Promise<{ checkout_url: string }> {
    const response = await this.client.post<{ checkout_url: string }>("/subscriptions/checkout", {
      plan_id: planId,
      annual,
      coupon_code: couponCode,
    });
    return response.data;
  }

  async getPortalUrl(): Promise<{ portal_url: string }> {
    const response = await this.client.post<{ portal_url: string }>("/subscriptions/portal");
    return response.data;
  }

  async cancelSubscription(): Promise<void> {
    await this.client.post("/subscriptions/cancel");
  }

  async resumeSubscription(): Promise<void> {
    await this.client.post("/subscriptions/resume");
  }

  async getInvoices(page = 1, perPage = 20): Promise<PaginatedResponse<Invoice>> {
    const response = await this.client.get<PaginatedResponse<Invoice>>("/subscriptions/invoices", {
      params: { page, per_page: perPage },
    });
    return response.data;
  }

  async getPaymentMethods(): Promise<PaymentMethod[]> {
    const response = await this.client.get<{ payment_methods: PaymentMethod[] }>("/subscriptions/payment-methods");
    return response.data.payment_methods;
  }

  async setDefaultPaymentMethod(methodId: string): Promise<void> {
    await this.client.post(`/subscriptions/payment-methods/${methodId}/default`);
  }

  async removePaymentMethod(methodId: string): Promise<void> {
    await this.client.delete(`/subscriptions/payment-methods/${methodId}`);
  }

  async validateCoupon(code: string, planId: string): Promise<{ valid: boolean; discount_percent?: number }> {
    const response = await this.client.post<{ valid: boolean; discount_percent?: number }>("/subscriptions/coupons/validate", {
      code,
      plan_id: planId,
    });
    return response.data;
  }

  // ===========================================================================
  // API KEYS
  // ===========================================================================

  async getAPIKeys(): Promise<APIKey[]> {
    const response = await this.client.get<{ keys: APIKey[] }>("/api-keys");
    return response.data.keys;
  }

  async createAPIKey(data: CreateAPIKeyRequest): Promise<APIKeyCreateResponse> {
    const response = await this.client.post<APIKeyCreateResponse>("/api-keys", data);
    return response.data;
  }

  async getAPIKey(id: string): Promise<APIKey> {
    const response = await this.client.get<APIKey>(`/api-keys/${id}`);
    return response.data;
  }

  async updateAPIKey(id: string, data: Partial<CreateAPIKeyRequest>): Promise<APIKey> {
    const response = await this.client.put<APIKey>(`/api-keys/${id}`, data);
    return response.data;
  }

  async deleteAPIKey(id: string): Promise<void> {
    await this.client.delete(`/api-keys/${id}`);
  }

  async rotateAPIKey(id: string): Promise<APIKeyCreateResponse> {
    const response = await this.client.post<APIKeyCreateResponse>(`/api-keys/${id}/rotate`);
    return response.data;
  }

  async revokeAllAPIKeys(): Promise<void> {
    await this.client.post("/api-keys/revoke-all");
  }

  // ===========================================================================
  // WEBHOOKS
  // ===========================================================================

  async getWebhooks(): Promise<Webhook[]> {
    const response = await this.client.get<{ webhooks: Webhook[] }>("/webhooks");
    return response.data.webhooks;
  }

  async createWebhook(data: CreateWebhookRequest): Promise<Webhook> {
    const response = await this.client.post<Webhook>("/webhooks", data);
    return response.data;
  }

  async getWebhook(id: string): Promise<Webhook> {
    const response = await this.client.get<Webhook>(`/webhooks/${id}`);
    return response.data;
  }

  async updateWebhook(id: string, data: Partial<CreateWebhookRequest>): Promise<Webhook> {
    const response = await this.client.put<Webhook>(`/webhooks/${id}`, data);
    return response.data;
  }

  async deleteWebhook(id: string): Promise<void> {
    await this.client.delete(`/webhooks/${id}`);
  }

  async enableWebhook(id: string): Promise<void> {
    await this.client.post(`/webhooks/${id}/enable`);
  }

  async disableWebhook(id: string): Promise<void> {
    await this.client.post(`/webhooks/${id}/disable`);
  }

  async testWebhook(id: string, event: WebhookEvent): Promise<{ success: boolean; status_code: number }> {
    const response = await this.client.post<{ success: boolean; status_code: number }>(`/webhooks/${id}/test`, { event });
    return response.data;
  }

  async rotateWebhookSecret(id: string): Promise<{ secret: string }> {
    const response = await this.client.post<{ secret: string }>(`/webhooks/${id}/rotate-secret`);
    return response.data;
  }

  async getWebhookDeliveries(webhookId: string, page = 1, perPage = 20): Promise<PaginatedResponse<WebhookDelivery>> {
    const response = await this.client.get<PaginatedResponse<WebhookDelivery>>(`/webhooks/${webhookId}/deliveries`, {
      params: { page, per_page: perPage },
    });
    return response.data;
  }

  async retryDelivery(webhookId: string, deliveryId: string): Promise<void> {
    await this.client.post(`/webhooks/${webhookId}/deliveries/${deliveryId}/retry`);
  }

  // ===========================================================================
  // ADMIN (requires admin role)
  // ===========================================================================

  async getAdminDashboard(): Promise<AdminDashboard> {
    const response = await this.client.get<AdminDashboard>("/admin/dashboard");
    return response.data;
  }

  async getAdminAnalytics(period: "day" | "week" | "month" | "year" = "month"): Promise<AdminAnalytics> {
    const response = await this.client.get<AdminAnalytics>("/admin/analytics", { params: { period } });
    return response.data;
  }

  async getAdminUsers(params?: {
    page?: number;
    per_page?: number;
    search?: string;
    role?: string;
    status?: string;
  }): Promise<PaginatedResponse<User>> {
    const response = await this.client.get<PaginatedResponse<User>>("/admin/users", { params });
    return response.data;
  }

  async adminUserAction(userId: string, action: "suspend" | "unsuspend" | "verify" | "delete"): Promise<void> {
    await this.client.post(`/admin/users/${userId}/action`, { action });
  }

  async getFeatureFlags(): Promise<FeatureFlag[]> {
    const response = await this.client.get<{ flags: FeatureFlag[] }>("/admin/feature-flags");
    return response.data.flags;
  }

  async createFeatureFlag(data: Partial<FeatureFlag>): Promise<FeatureFlag> {
    const response = await this.client.post<FeatureFlag>("/admin/feature-flags", data);
    return response.data;
  }

  async updateFeatureFlag(id: string, data: Partial<FeatureFlag>): Promise<FeatureFlag> {
    const response = await this.client.put<FeatureFlag>(`/admin/feature-flags/${id}`, data);
    return response.data;
  }

  async deleteFeatureFlag(id: string): Promise<void> {
    await this.client.delete(`/admin/feature-flags/${id}`);
  }

  async getAuditLogs(params?: {
    page?: number;
    per_page?: number;
    user_id?: string;
    action?: string;
    resource_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<AuditLog>> {
    const response = await this.client.get<PaginatedResponse<AuditLog>>("/admin/audit-logs", { params });
    return response.data;
  }

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await this.client.get<SystemHealth>("/admin/health");
    return response.data;
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

let apiInstance: SynthesizeAPI | null = null;

export function getAPI(): SynthesizeAPI {
  if (!apiInstance) {
    apiInstance = new SynthesizeAPI();
  }
  return apiInstance;
}

export function initAPI(config?: {
  baseURL?: string;
  onTokenRefresh?: (tokens: AuthTokens) => void;
  onUnauthorized?: () => void;
}): SynthesizeAPI {
  apiInstance = new SynthesizeAPI(config);
  return apiInstance;
}

export default SynthesizeAPI;
