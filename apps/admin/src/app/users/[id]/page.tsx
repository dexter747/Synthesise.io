'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAPI } from '@synthesize/api-client';
import { useAdminUserAction } from '@/hooks/use-admin-api';
import { formatDate, formatRelativeTime, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';
import {
  ArrowLeft,
  Mail,
  Shield,
  Ban,
  CheckCircle,
  Trash2,
  Edit,
  Clock,
  Database,
  Play,
  Loader2,
  User as UserIcon,
  Calendar,
  Activity,
  CreditCard,
  Settings,
  AlertTriangle,
  Plus,
  Minus,
} from 'lucide-react';

export default function AdminUserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const userId = params.id as string;
  const [activeTab, setActiveTab] = useState<'overview' | 'subscription' | 'datasets' | 'jobs' | 'activity'>('overview');

  const { data: user, isLoading } = useQuery({
    queryKey: ['admin', 'user', userId],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get(`/admin/users/${userId}`);
      return response.data;
    },
  });

  const userAction = useAdminUserAction();

  const handleAction = async (action: 'suspend' | 'unsuspend' | 'verify' | 'delete') => {
    const confirmMessages: Record<string, string> = {
      suspend: 'Are you sure you want to suspend this user?',
      unsuspend: 'Are you sure you want to unsuspend this user?',
      verify: 'Mark this user as verified?',
      delete: 'Are you sure you want to delete this user? This action cannot be undone.',
    };

    if (!confirm(confirmMessages[action])) return;

    try {
      await userAction.mutateAsync({ userId, action });
      toast.success(`User ${action}ed successfully`);
      if (action === 'delete') {
        router.push('/users');
      }
    } catch (error: any) {
      toast.error(error.message || `Failed to ${action} user`);
    }
  };

  if (isLoading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      </AdminLayout>
    );
  }

  if (!user) {
    return (
      <AdminLayout>
        <div className="text-center py-16">
          <UserIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">User not found</h3>
          <Button onClick={() => router.push('/users')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Users
          </Button>
        </div>
      </AdminLayout>
    );
  }

  const status = user.is_active ? (user.is_suspended ? 'suspended' : 'active') : 'pending';

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <Button variant="ghost" onClick={() => router.push('/users')}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-2xl font-medium">
                {user.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-medium">{user.name}</h1>
                  <StatusBadge status={status} />
                  {user.role === 'admin' || user.role === 'super_admin' ? (
                    <Badge variant="error">
                      <Shield className="w-3 h-3 mr-1" />
                      {user.role.replace('_', ' ')}
                    </Badge>
                  ) : null}
                </div>
                <p className="text-gray-400 mt-1">{user.email}</p>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    Joined {formatDate(user.created_at)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    Last active {user.last_login_at ? formatRelativeTime(user.last_login_at) : 'Never'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.location.href = `mailto:${user.email}`}
            >
              <Mail className="w-4 h-4 mr-2" />
              Email
            </Button>
            {!user.is_verified && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAction('verify')}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Verify
              </Button>
            )}
            {status === 'suspended' ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAction('unsuspend')}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Unsuspend
              </Button>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAction('suspend')}
              >
                <Ban className="w-4 h-4 mr-2" />
                Suspend
              </Button>
            )}
            <Button
              variant="danger"
              size="sm"
              onClick={() => handleAction('delete')}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-700">
          <div className="flex gap-6">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'subscription', label: 'Subscription & Quota' },
              { id: 'datasets', label: 'Datasets' },
              { id: 'jobs', label: 'Jobs' },
              { id: 'activity', label: 'Activity' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-red-500 text-white'
                    : 'border-transparent text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Stats */}
            <div className="lg:col-span-2 space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6 text-center">
                    <Database className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                    <p className="text-2xl font-medium text-white">
                      {formatNumber(user.stats?.datasets_count || 0)}
                    </p>
                    <p className="text-sm text-gray-400">Datasets</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6 text-center">
                    <Play className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                    <p className="text-2xl font-medium text-white">
                      {formatNumber(user.stats?.jobs_count || 0)}
                    </p>
                    <p className="text-sm text-gray-400">Jobs</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6 text-center">
                    <Activity className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <p className="text-2xl font-medium text-white">
                      {formatNumber(user.stats?.total_rows || 0)}
                    </p>
                    <p className="text-sm text-gray-400">Rows Generated</p>
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  {user.recent_activity?.length === 0 ? (
                    <p className="text-center py-8 text-gray-400">No recent activity</p>
                  ) : (
                    <div className="space-y-3">
                      {user.recent_activity?.map((activity: any, i: number) => (
                        <div key={i} className="flex items-start gap-3 p-3 bg-gray-800 rounded-lg">
                          <Activity className="w-4 h-4 text-gray-400 mt-0.5" />
                          <div className="flex-1">
                            <p className="text-sm text-white">{activity.description}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              {formatRelativeTime(activity.created_at)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* User Info */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>User Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-400">User ID</p>
                    <p className="text-white font-mono text-sm mt-1">{user.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Email</p>
                    <p className="text-white mt-1">{user.email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Role</p>
                    <Badge variant="default" className="mt-1">
                      {user.role}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Status</p>
                    <div className="mt-1">
                      <StatusBadge status={status} />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Email Verified</p>
                    <p className="text-white mt-1">{user.is_verified ? 'Yes' : 'No'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Subscription</p>
                    <Badge variant="default" className="mt-1">
                      {user.subscription_tier || 'Free'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Admin Controls Card */}
              <AdminControlsCard userId={userId} user={user} onUpdate={() => queryClient.invalidateQueries({ queryKey: ['admin', 'user', userId] })} />

              <Card>
                <CardHeader>
                  <CardTitle>Account Timeline</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-400">Created</p>
                    <p className="text-white text-sm mt-1">{formatDate(user.created_at)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Last Login</p>
                    <p className="text-white text-sm mt-1">
                      {user.last_login_at ? formatDate(user.last_login_at) : 'Never'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Last Updated</p>
                    <p className="text-white text-sm mt-1">{formatDate(user.updated_at)}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Datasets Tab */}
        {activeTab === 'datasets' && (
          <Card>
            <CardHeader>
              <CardTitle>User Datasets</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center py-8 text-gray-400">Datasets list coming soon...</p>
            </CardContent>
          </Card>
        )}

        {/* Subscription & Quota Tab */}
        {activeTab === 'subscription' && (
          <SubscriptionQuotaTab userId={userId} />
        )}

        {/* Jobs Tab */}
        {activeTab === 'jobs' && (
          <Card>
            <CardHeader>
              <CardTitle>User Jobs</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center py-8 text-gray-400">Jobs list coming soon...</p>
            </CardContent>
          </Card>
        )}

        {/* Activity Tab */}
        {activeTab === 'activity' && (
          <Card>
            <CardHeader>
              <CardTitle>Activity Log</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center py-8 text-gray-400">Activity log coming soon...</p>
            </CardContent>
          </Card>
        )}
      </div>
    </AdminLayout>
  );
}

// Subscription & Quota Management Tab Component
function SubscriptionQuotaTab({ userId }: { userId: string }) {
  const queryClient = useQueryClient();
  const [showQuotaOverride, setShowQuotaOverride] = useState(false);
  const [quotaOverride, setQuotaOverride] = useState({
    rows_per_month: '',
    max_rows_per_job: '',
    concurrent_jobs: '',
  });
  const [overrideReason, setOverrideReason] = useState('');
  const [showCreateSub, setShowCreateSub] = useState(false);
  const [extendDays, setExtendDays] = useState('30');

  // Fetch user usage data
  const { data: usageData, isLoading } = useQuery({
    queryKey: ['admin', 'user-usage', userId],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get(`/admin/users/${userId}/usage`);
      return response.data;
    },
  });

  // Fetch subscription plans
  const { data: plans } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: async () => {
      const api = getAPI();
      const response = await (api as any).client.get('/subscriptions/plans');
      return response.data;
    },
  });

  // Mutations
  const applyQuotaOverride = useMutation({
    mutationFn: async (data: { custom_limits: Record<string, number>; reason: string }) => {
      const api = getAPI();
      return (api as any).client.put(`/admin/users/${userId}/quota-override`, data);
    },
    onSuccess: () => {
      toast.success('Quota override applied');
      queryClient.invalidateQueries({ queryKey: ['admin', 'user-usage', userId] });
      setShowQuotaOverride(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to apply quota override');
    },
  });

  const removeQuotaOverride = useMutation({
    mutationFn: async () => {
      const api = getAPI();
      return (api as any).client.delete(`/admin/users/${userId}/quota-override`);
    },
    onSuccess: () => {
      toast.success('Quota override removed');
      queryClient.invalidateQueries({ queryKey: ['admin', 'user-usage', userId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to remove quota override');
    },
  });

  const extendSubscription = useMutation({
    mutationFn: async (data: { days: number; reason: string }) => {
      const api = getAPI();
      const subId = usageData?.subscription?.id;
      return (api as any).client.put(`/admin/subscriptions/${subId}/extend`, data);
    },
    onSuccess: () => {
      toast.success('Subscription extended');
      queryClient.invalidateQueries({ queryKey: ['admin', 'user-usage', userId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to extend subscription');
    },
  });

  const changeSubscriptionStatus = useMutation({
    mutationFn: async (data: { new_status: string; reason: string }) => {
      const api = getAPI();
      const subId = usageData?.subscription?.id;
      return (api as any).client.put(`/admin/subscriptions/${subId}/status`, data);
    },
    onSuccess: () => {
      toast.success('Status updated');
      queryClient.invalidateQueries({ queryKey: ['admin', 'user-usage', userId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update status');
    },
  });

  const createSubscription = useMutation({
    mutationFn: async (data: { plan_id: string; months: number; reason: string }) => {
      const api = getAPI();
      return (api as any).client.post(`/admin/users/${userId}/create-subscription`, data);
    },
    onSuccess: () => {
      toast.success('Subscription created');
      queryClient.invalidateQueries({ queryKey: ['admin', 'user-usage', userId] });
      setShowCreateSub(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create subscription');
    },
  });

  const handleApplyQuotaOverride = () => {
    const customLimits: Record<string, number> = {};
    if (quotaOverride.rows_per_month) customLimits.rows_per_month = parseInt(quotaOverride.rows_per_month);
    if (quotaOverride.max_rows_per_job) customLimits.max_rows_per_job = parseInt(quotaOverride.max_rows_per_job);
    if (quotaOverride.concurrent_jobs) customLimits.concurrent_jobs = parseInt(quotaOverride.concurrent_jobs);
    
    if (Object.keys(customLimits).length === 0) {
      toast.error('Please enter at least one limit to override');
      return;
    }
    
    applyQuotaOverride.mutate({ custom_limits: customLimits, reason: overrideReason || 'Admin override' });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  const subscription = usageData?.subscription;
  const usage = usageData?.usage || {};
  const quotas = usageData?.quotas || {};

  return (
    <div className="space-y-6">
      {/* Subscription Info */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="w-5 h-5" />
            Subscription
          </CardTitle>
          {subscription ? (
            <Badge 
              variant={subscription.status === 'active' ? 'success' : subscription.status === 'on_hold' ? 'warning' : 'error'}
            >
              {subscription.status}
            </Badge>
          ) : (
            <Badge variant="outline">No Subscription</Badge>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {subscription ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-400">Plan</p>
                  <p className="text-white font-medium">{subscription.plan?.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Tier</p>
                  <Badge variant="default">{subscription.plan?.tier}</Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Period End</p>
                  <p className="text-white">{formatDate(subscription.current_period_end)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Price</p>
                  <p className="text-white">${(subscription.plan?.monthly_price_cents || 0) / 100}/mo</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-700">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => extendSubscription.mutate({ days: parseInt(extendDays), reason: 'Admin extension' })}
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Extend
                </Button>
                <Input 
                  type="number" 
                  value={extendDays} 
                  onChange={(e) => setExtendDays(e.target.value)}
                  className="w-20 h-8"
                  placeholder="Days"
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => changeSubscriptionStatus.mutate({ 
                    new_status: subscription.status === 'active' ? 'paused' : 'active', 
                    reason: 'Admin toggle' 
                  })}
                >
                  {subscription.status === 'active' ? 'Pause' : 'Activate'}
                </Button>
                <Button 
                  variant="danger" 
                  size="sm"
                  onClick={() => {
                    if (confirm('Cancel this subscription?')) {
                      changeSubscriptionStatus.mutate({ new_status: 'cancelled', reason: 'Admin cancellation' });
                    }
                  }}
                >
                  Cancel
                </Button>
              </div>
            </>
          ) : (
            <div className="text-center py-6">
              <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
              <p className="text-gray-400 mb-4">User has no active subscription</p>
              <Button onClick={() => setShowCreateSub(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Grant Subscription
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Subscription Modal */}
      {showCreateSub && (
        <Card>
          <CardHeader>
            <CardTitle>Grant Subscription</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm text-gray-400">Select Plan</label>
              <select 
                className="w-full mt-1 px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 transition-all duration-200 appearance-none"
                id="plan-select"
              >
                {plans?.plans?.map((plan: any) => (
                  <option key={plan.id} value={plan.id} className="bg-gray-900">
                    {plan.name} - ${plan.price_monthly}/mo ({plan.tier})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-400">Duration (months)</label>
              <Input type="number" defaultValue="1" min="1" max="24" id="months-input" />
            </div>
            <div>
              <label className="text-sm text-gray-400">Reason</label>
              <Input placeholder="e.g., Employee account, promotion" id="reason-input" />
            </div>
            <div className="flex gap-2">
              <Button onClick={() => {
                const planId = (document.getElementById('plan-select') as HTMLSelectElement).value;
                const months = parseInt((document.getElementById('months-input') as HTMLInputElement).value);
                const reason = (document.getElementById('reason-input') as HTMLInputElement).value;
                createSubscription.mutate({ plan_id: planId, months, reason: reason || 'Admin grant' });
              }}>
                Grant Access
              </Button>
              <Button variant="outline" onClick={() => setShowCreateSub(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Usage Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Current Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Rows per month */}
            <UsageBar
              label="Rows Generated"
              current={usage.rows_per_month || 0}
              limit={quotas.rows_per_month || 0}
            />
            
            {/* Jobs per month */}
            <UsageBar
              label="Jobs This Month"
              current={usage.jobs_per_month || 0}
              limit={quotas.jobs_per_month || 0}
            />
            
            {/* Concurrent jobs */}
            <UsageBar
              label="Concurrent Jobs"
              current={usage.concurrent_jobs || 0}
              limit={quotas.concurrent_jobs || 0}
            />
            
            {/* API calls */}
            <UsageBar
              label="API Calls"
              current={usage.api_calls_per_month || 0}
              limit={quotas.api_calls_per_month || 0}
            />
          </div>
        </CardContent>
      </Card>

      {/* Quota Override */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Quota Override
          </CardTitle>
          {!showQuotaOverride && (
            <Button variant="outline" size="sm" onClick={() => setShowQuotaOverride(true)}>
              <Edit className="w-4 h-4 mr-2" />
              Set Override
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {showQuotaOverride ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Rows/Month</label>
                  <Input 
                    type="number"
                    placeholder={String(quotas.rows_per_month || 'Default')}
                    value={quotaOverride.rows_per_month}
                    onChange={(e) => setQuotaOverride(prev => ({ ...prev, rows_per_month: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400">Max Rows/Job</label>
                  <Input 
                    type="number"
                    placeholder={String(quotas.max_rows_per_job || 'Default')}
                    value={quotaOverride.max_rows_per_job}
                    onChange={(e) => setQuotaOverride(prev => ({ ...prev, max_rows_per_job: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400">Concurrent Jobs</label>
                  <Input 
                    type="number"
                    placeholder={String(quotas.concurrent_jobs || 'Default')}
                    value={quotaOverride.concurrent_jobs}
                    onChange={(e) => setQuotaOverride(prev => ({ ...prev, concurrent_jobs: e.target.value }))}
                  />
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Reason</label>
                <Input 
                  placeholder="e.g., Customer support resolution"
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleApplyQuotaOverride} disabled={applyQuotaOverride.isPending}>
                  {applyQuotaOverride.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Apply Override'}
                </Button>
                <Button variant="outline" onClick={() => setShowQuotaOverride(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-gray-400">
              <p>No custom quota override set for this user.</p>
              <p className="text-sm mt-2">User is using plan default limits.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Usage bar component
function UsageBar({ label, current, limit }: { label: string; current: number; limit: number }) {
  const isUnlimited = limit === -1;
  const percentage = isUnlimited ? 0 : Math.min((current / limit) * 100, 100);
  const isWarning = percentage >= 80;
  const isDanger = percentage >= 95;

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white">
          {formatNumber(current)} / {isUnlimited ? '∞' : formatNumber(limit)}
        </span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full transition-all ${
            isDanger ? 'bg-red-500' : isWarning ? 'bg-amber-500' : 'bg-teal-500'
          }`}
          style={{ width: isUnlimited ? '0%' : `${percentage}%` }}
        />
      </div>
    </div>
  );
}
// Admin Controls Card - Role & Subscription Management
function AdminControlsCard({ userId, user, onUpdate }: { userId: string; user: any; onUpdate: () => void }) {
  const [selectedRole, setSelectedRole] = useState(user?.role || 'user');
  const [selectedTier, setSelectedTier] = useState(user?.subscription_tier || 'free');

  const changeRole = useMutation({
    mutationFn: async (newRole: string) => {
      const api = getAPI();
      return (api as any).client.post(`/admin/users/${userId}/action`, {
        action: 'change_role',
        new_role: newRole,
      });
    },
    onSuccess: () => {
      toast.success('Role updated successfully');
      onUpdate();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to change role');
    },
  });

  const changeTier = useMutation({
    mutationFn: async (newTier: string) => {
      const api = getAPI();
      return (api as any).client.post(`/admin/users/${userId}/subscription-tier`, {
        tier: newTier,
      });
    },
    onSuccess: () => {
      toast.success('Subscription tier updated successfully');
      onUpdate();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to change subscription tier');
    },
  });

  const roles = [
    { value: 'user', label: 'User', description: 'Regular user access' },
    { value: 'admin', label: 'Admin', description: 'Full admin access' },
    { value: 'super_admin', label: 'Super Admin', description: 'Super administrator' },
    { value: 'support', label: 'Support', description: 'Customer support access' },
    { value: 'analyst', label: 'Analyst', description: 'Read-only analytics' },
  ];

  const tiers = [
    { value: 'free', label: 'Free', color: 'gray' },
    { value: 'starter', label: 'Starter', color: 'blue' },
    { value: 'professional', label: 'Professional', color: 'teal' },
    { value: 'business', label: 'Business', color: 'purple' },
    { value: 'enterprise', label: 'Enterprise', color: 'amber' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="w-4 h-4" />
          Admin Controls
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Role Management */}
        <div>
          <label className="text-sm text-gray-400 block mb-2">User Role</label>
          <div className="relative">
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full appearance-none px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50"
            >
              {roles.map((role) => (
                <option key={role.value} value={role.value} className="bg-gray-900">
                  {role.label}
                </option>
              ))}
            </select>
            <Shield className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          {selectedRole !== user?.role && (
            <Button
              size="sm"
              className="mt-2 w-full"
              onClick={() => changeRole.mutate(selectedRole)}
              disabled={changeRole.isPending}
            >
              {changeRole.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Update Role to {roles.find(r => r.value === selectedRole)?.label}
            </Button>
          )}
        </div>

        {/* Subscription Tier Override */}
        <div>
          <label className="text-sm text-gray-400 block mb-2">
            Subscription Tier
            <span className="text-xs text-amber-400 ml-2">(Manual Override)</span>
          </label>
          <div className="relative">
            <select
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="w-full appearance-none px-4 py-2.5 pr-10 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50"
            >
              {tiers.map((tier) => (
                <option key={tier.value} value={tier.value} className="bg-gray-900">
                  {tier.label}
                </option>
              ))}
            </select>
            <CreditCard className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Use this to manually fix subscription issues or grant access
          </p>
          {selectedTier !== (user?.subscription_tier || 'free') && (
            <Button
              size="sm"
              className="mt-2 w-full"
              onClick={() => changeTier.mutate(selectedTier)}
              disabled={changeTier.isPending}
            >
              {changeTier.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Update Tier to {tiers.find(t => t.value === selectedTier)?.label}
            </Button>
          )}
        </div>

        {/* Warning Notice */}
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
          <div className="flex gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-200">
              <p className="font-medium">Manual Override Warning</p>
              <p className="text-amber-300/70 mt-1">
                Changes made here bypass normal payment flows. Use only for technical issues or customer support cases.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}