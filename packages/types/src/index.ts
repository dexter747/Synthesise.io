// =============================================================================
// SYNTHESIZE.IO - SHARED TYPES
// =============================================================================

// =============================================================================
// USER & AUTHENTICATION
// =============================================================================

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: UserRole;
  email_verified: boolean;
  is_active: boolean;
  subscription_tier: SubscriptionTier;
  created_at: string;
  updated_at: string;
}

export type UserRole = "user" | "admin" | "super_admin";

export interface Session {
  id: string;
  device_info?: DeviceInfo;
  ip_address?: string;
  expires_at: string;
  created_at: string;
  is_current?: boolean;
}

export interface DeviceInfo {
  browser: string;
  os: string;
  device_type: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

// =============================================================================
// ORGANIZATIONS
// =============================================================================

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
  billing_email?: string;
  owner_id: string;
  member_count: number;
  subscription_tier: SubscriptionTier;
  created_at: string;
  updated_at: string;
}

export interface OrganizationMember {
  id: string;
  user_id: string;
  organization_id: string;
  role: OrganizationRole;
  user: User;
  joined_at: string;
}

export type OrganizationRole = "owner" | "admin" | "member" | "viewer";

export interface OrganizationInvite {
  id: string;
  organization_id: string;
  email: string;
  role: OrganizationRole;
  status: "pending" | "accepted" | "expired" | "canceled";
  expires_at: string;
  created_at: string;
}

// =============================================================================
// SUBSCRIPTIONS & BILLING
// =============================================================================

export type SubscriptionTier = "free" | "starter" | "professional" | "business" | "enterprise";
export type SubscriptionStatus = "active" | "past_due" | "canceled" | "paused" | "trialing";

export interface SubscriptionPlan {
  id: string;
  name: string;
  tier: SubscriptionTier;
  slug?: string; // Optional slug for plan identification (e.g., 'free', 'enterprise')
  description?: string; // Optional description for display
  price_monthly: number;  // Price in dollars (already converted from cents by API)
  price_yearly: number;
  price_inr_monthly?: number;  // Price in INR (optional)
  price_inr_annual?: number;
  currency: string;
  features: PlanFeatures;
  limits?: PlanLimits; // Optional limits object for display
  is_popular?: boolean;
}

export interface PlanLimits {
  monthly_data_gb: number; // -1 for unlimited
  max_datasets: number; // -1 for unlimited
}

export interface PlanFeatures {
  rows_per_month: number;
  datasets_limit: number;
  team_members: number;
  api_access: boolean;
  priority_support: boolean;
  priority_queue?: boolean; // Optional priority queue feature
  custom_schemas: boolean;
  data_export_formats: string[];
  retention_days: number;
}

export interface Subscription {
  id: string;
  user_id: string;
  plan_id: string;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  trial_ends_at?: string;
}

export interface UsageStats {
  rows_generated: number;
  rows_limit: number;
  datasets_count: number;
  datasets_limit: number;
  api_calls: number;
  storage_used_bytes: number;
  billing_period_start: string;
  billing_period_end: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  amount_cents: number;
  currency: string;
  status: "draft" | "open" | "paid" | "void" | "uncollectible";
  invoice_date: string;
  due_date: string;
  paid_at?: string;
  pdf_url?: string;
}

export interface PaymentMethod {
  id: string;
  type: "card" | "bank_account";
  last_four: string;
  brand?: string;
  exp_month?: number;
  exp_year?: number;
  is_default: boolean;
}

// =============================================================================
// DATASETS
// =============================================================================

export type DatasetStatus = "draft" | "ready" | "generating" | "completed" | "error" | "archived";
export type DataFormat = "csv" | "json" | "parquet" | "excel";

export interface Dataset {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  organization_id?: string;
  status: DatasetStatus;
  schema_definition: SchemaField[];
  row_count: number;
  column_count: number;
  format: DataFormat;
  size_bytes: number;
  quality_score?: number;
  is_public: boolean;
  tags: string[];
  download_count: number;
  created_at: string;
  updated_at: string;
}

export interface SchemaField {
  name: string;
  display_name: string;
  field_type: FieldType;
  description?: string;
  is_nullable: boolean;
  is_unique: boolean;
  default_value?: any;
  constraints?: FieldConstraints;
  generator_config?: GeneratorConfig;
}

export type FieldType = 
  | "string" | "text" | "email" | "phone" | "url"
  | "integer" | "float" | "decimal"
  | "boolean"
  | "date" | "datetime" | "time"
  | "uuid" | "json"
  | "name" | "first_name" | "last_name"
  | "address" | "city" | "country" | "zip_code"
  | "company" | "job_title"
  | "credit_card" | "ssn"
  | "custom";

export interface FieldConstraints {
  min_length?: number;
  max_length?: number;
  min_value?: number;
  max_value?: number;
  pattern?: string;
  enum_values?: string[];
}

export interface GeneratorConfig {
  generator_type: string;
  params?: Record<string, any>;
  locale?: string;
}

export interface DatasetTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  schema_definition: SchemaField[];
  preview_data?: any[];
  usage_count: number;
}

// =============================================================================
// GENERATION JOBS
// =============================================================================

export type JobStatus = "queued" | "processing" | "completed" | "failed" | "cancelled" | "pending";
export type JobPriority = "low" | "normal" | "high";

export interface GenerationJob {
  id: string;
  dataset_id: string;
  dataset?: Dataset;
  user_id: string;
  status: JobStatus;
  priority: JobPriority;
  row_count?: number;  // New API field name
  rows_requested?: number;  // Deprecated, kept for compatibility
  rows_generated: number;
  progress_percent?: number;
  progress?: number;  // New API field name (0-100)
  output_format?: DataFormat;  // New API field name
  format?: DataFormat;  // Deprecated, kept for compatibility
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  download_url?: string;
  file_size_bytes?: number;
  file_size?: number;
}

export interface DatasetWithJobResponse {
  dataset: Dataset;
  job?: GenerationJob;
  message: string;
}

export interface JobStats {
  total_jobs: number;
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  rows_generated_today: number;
  avg_processing_time_seconds: number;
}

// =============================================================================
// API KEYS
// =============================================================================

export interface APIKey {
  id: string;
  name: string;
  prefix: string;
  scopes: APIScope[];
  last_used_at?: string;
  expires_at?: string;
  is_active: boolean;
  created_at: string;
}

export interface APIKeyCreateResponse {
  id: string;
  name: string;
  key: string;
  prefix: string;
  scopes: APIScope[];
  expires_at?: string;
}

export type APIScope = 
  | "datasets:read" | "datasets:write"
  | "jobs:read" | "jobs:write"
  | "user:read" | "user:write";

// =============================================================================
// WEBHOOKS
// =============================================================================

export type WebhookEvent = 
  | "job.started" | "job.completed" | "job.failed"
  | "dataset.created" | "dataset.deleted"
  | "subscription.created" | "subscription.canceled"
  | "invoice.paid" | "invoice.failed";

export interface Webhook {
  id: string;
  url: string;
  events: WebhookEvent[];
  secret_preview: string;
  is_active: boolean;
  last_triggered_at?: string;
  failure_count: number;
  created_at: string;
}

export interface WebhookDelivery {
  id: string;
  webhook_id: string;
  event: WebhookEvent;
  status: "pending" | "success" | "failed";
  status_code?: number;
  response_body?: string;
  attempt_count: number;
  created_at: string;
}

// =============================================================================
// ADMIN
// =============================================================================

export interface AdminDashboard {
  total_users: number;
  active_users: number;
  total_datasets: number;
  total_jobs: number;
  rows_generated_today: number;
  revenue_this_month: number;
  new_users_this_week: number;
  subscription_breakdown: Record<SubscriptionTier, number>;
  avg_job_size?: number;
  // Change percentages
  users_change_pct?: number;
  active_users_change_pct?: number;
  datasets_change_pct?: number;
  jobs_change_pct?: number;
  revenue_change_pct?: number;
  rows_generated_change_pct?: number;
  new_users_week_change_pct?: number;
}

export interface AdminAnalytics {
  user_growth: TimeSeriesData[];
  revenue_trend: TimeSeriesData[];
  jobs_per_day: TimeSeriesData[];
  rows_generated_per_day: TimeSeriesData[];
  top_users: TopUser[];
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface TopUser {
  id: string;
  name: string;
  email: string;
  rows_generated: number;
  datasets_count: number;
}

export interface FeatureFlag {
  id: string;
  name: string;
  key: string;
  description?: string;
  is_enabled: boolean;
  rollout_percentage: number;
  targeting_rules?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  ip_address?: string;
  user_agent?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface SystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  database: "healthy" | "degraded" | "unhealthy" | "unknown";
  redis: "healthy" | "degraded" | "unhealthy" | "unknown";
  celery: "healthy" | "degraded" | "unhealthy" | "unknown";
  storage: "healthy" | "degraded" | "unhealthy" | "unknown";
  timestamp?: string;
  
  // Resource usage
  cpu_usage_percent?: number;
  memory_usage_percent?: number;
  disk_usage_percent?: number;
  
  // Queue stats
  pending_jobs?: number;
  active_workers?: number;
  
  // Additional fields (for backwards compatibility)
  api_status?: "healthy" | "degraded" | "down";
  database_status?: "healthy" | "degraded" | "down";
  redis_status?: "healthy" | "degraded" | "down";
  celery_status?: "healthy" | "degraded" | "down";
  queue_size?: number;
  uptime_seconds?: number;
  api_latency?: number;
  db_connections?: number;
  redis_memory?: number;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
  requests_per_minute?: number;
  error_rate?: number;
  recent_logs?: Array<{
    timestamp: string;
    level: string;
    message: string;
  }>;
  environment?: string;
  version?: string;
  region?: string;
  last_deploy?: string;
}

// =============================================================================
// NOTIFICATIONS
// =============================================================================

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

export type NotificationType = 
  | "job_completed" | "job_failed"
  | "quota_warning" | "quota_exceeded"
  | "subscription_expiring" | "payment_failed"
  | "team_invite" | "system_announcement";

// =============================================================================
// API RESPONSES
// =============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
  status_code: number;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
}

// =============================================================================
// FORMS & REQUESTS
// =============================================================================

export interface CreateDatasetRequest {
  name: string;
  description?: string;
  schema_definition: SchemaField[];
  format?: DataFormat;
  organization_id?: string;
  tags?: string[];
}

export interface CreateDatasetFromDescriptionRequest {
  name?: string;
  description: string;
  sample_data?: string;
  row_count?: number;
  output_format?: 'csv' | 'json' | 'sql';
  organization_id?: string;
  tags?: string[];
}

export interface UpdateDatasetRequest {
  name?: string;
  description?: string;
  schema_definition?: SchemaField[];
  tags?: string[];
}

export interface GenerateDataRequest {
  row_count: number;
  output_format?: DataFormat;
  priority?: JobPriority;
}

export interface CreateOrganizationRequest {
  name: string;
  description?: string;
  billing_email?: string;
}

export interface InviteMemberRequest {
  email: string;
  role: OrganizationRole;
}

export interface CreateAPIKeyRequest {
  name: string;
  scopes: APIScope[];
  expires_in_days?: number;
}

export interface CreateWebhookRequest {
  url: string;
  events: WebhookEvent[];
}
