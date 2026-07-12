'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  useFeatureFlags,
  useCreateFeatureFlag,
  useUpdateFeatureFlag,
  useDeleteFeatureFlag,
} from '@/hooks/use-admin-api';
import { formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Plus,
  Flag,
  Trash2,
  Edit,
  Loader2,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react';

export default function FeatureFlagsPage() {
  const { data: flags, isLoading } = useFeatureFlags();
  const createFlag = useCreateFeatureFlag();
  const updateFlag = useUpdateFeatureFlag();
  const deleteFlag = useDeleteFeatureFlag();

  const [showCreate, setShowCreate] = useState(false);
  const [newFlag, setNewFlag] = useState({ key: '', name: '', description: '' });

  const handleCreate = async () => {
    if (!newFlag.key.trim() || !newFlag.name.trim()) {
      toast.error('Key and name are required');
      return;
    }

    try {
      await createFlag.mutateAsync({
        key: newFlag.key,
        name: newFlag.name,
        description: newFlag.description,
        is_enabled: false,
      });
      setNewFlag({ key: '', name: '', description: '' });
      setShowCreate(false);
      toast.success('Feature flag created');
    } catch (error: any) {
      toast.error(error.message || 'Failed to create feature flag');
    }
  };

  const handleToggle = async (flag: any) => {
    try {
      await updateFlag.mutateAsync({
        id: flag.id,
        data: { is_enabled: !flag.is_enabled },
      });
      toast.success(`Feature flag ${flag.is_enabled ? 'disabled' : 'enabled'}`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to update feature flag');
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await deleteFlag.mutateAsync(id);
      toast.success('Feature flag deleted');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete feature flag');
    }
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-medium text-white">Feature Flags</h2>
            <p className="text-gray-400 mt-1">Control feature rollouts across the platform</p>
          </div>
          <Button
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setShowCreate(true)}
          >
            Add Flag
          </Button>
        </div>

        {/* Create Form */}
        {showCreate && (
          <Card>
            <CardHeader>
              <CardTitle>Create Feature Flag</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Key"
                  placeholder="feature_new_dashboard"
                  value={newFlag.key}
                  onChange={(e) => setNewFlag({ ...newFlag, key: e.target.value })}
                  helperText="Unique identifier used in code"
                />
                <Input
                  label="Name"
                  placeholder="New Dashboard"
                  value={newFlag.name}
                  onChange={(e) => setNewFlag({ ...newFlag, name: e.target.value })}
                />
              </div>
              <Input
                label="Description"
                placeholder="Optional description..."
                value={newFlag.description}
                onChange={(e) => setNewFlag({ ...newFlag, description: e.target.value })}
              />
              <div className="flex gap-2">
                <Button onClick={handleCreate} loading={createFlag.isPending}>
                  Create Flag
                </Button>
                <Button variant="outline" onClick={() => setShowCreate(false)}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Flags List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Flag className="w-5 h-5" />
              All Flags ({flags?.length || 0})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
              </div>
            ) : !flags || flags.length === 0 ? (
              <div className="text-center py-16">
                <Flag className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">No feature flags</h3>
                <p className="text-gray-400">Create your first feature flag to get started</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-700">
                {flags.map((flag) => (
                  <div
                    key={flag.id}
                    className="flex items-center gap-4 px-6 py-4 hover:bg-gray-700/30"
                  >
                    <button
                      onClick={() => handleToggle(flag)}
                      className="flex-shrink-0"
                      title={flag.is_enabled ? 'Disable' : 'Enable'}
                    >
                      {flag.is_enabled ? (
                        <ToggleRight className="w-10 h-10 text-green-400" />
                      ) : (
                        <ToggleLeft className="w-10 h-10 text-gray-500" />
                      )}
                    </button>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-white">{flag.name}</h4>
                        <code className="text-xs px-2 py-0.5 bg-gray-700 text-gray-300 rounded">
                          {flag.key}
                        </code>
                      </div>
                      {flag.description && (
                        <p className="text-sm text-gray-400 mt-1">{flag.description}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        Created {formatDate(flag.created_at)}
                        {flag.updated_at && ` • Updated ${formatDate(flag.updated_at)}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Badge variant={flag.is_enabled ? 'success' : 'default'}>
                        {flag.is_enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(flag.id, flag.name)}
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}
