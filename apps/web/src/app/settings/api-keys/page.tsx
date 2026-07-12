'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  useAPIKeys,
  useCreateAPIKey,
  useDeleteAPIKey,
  useRotateAPIKey,
} from '@/hooks/use-api';
import { formatDate } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Plus,
  Key,
  Copy,
  Trash2,
  RefreshCw,
  Eye,
  EyeOff,
  Loader2,
  CheckCircle,
} from 'lucide-react';
import { Input } from '@/components/ui/input';

export default function APIKeysPage() {
  const { data: keys, isLoading } = useAPIKeys();
  const createKey = useCreateAPIKey();
  const deleteKey = useDeleteAPIKey();
  const rotateKey = useRotateAPIKey();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a name for the API key');
      return;
    }

    try {
      const response = await createKey.mutateAsync({
        name: newKeyName,
        scopes: ['datasets:read', 'datasets:write', 'jobs:read', 'jobs:write'],
      });
      setCreatedKey(response.key);
      setNewKeyName('');
    } catch (error: any) {
      toast.error(error.message || 'Failed to create API key');
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete the API key "${name}"?`)) return;

    try {
      await deleteKey.mutateAsync(id);
      toast.success('API key deleted');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete API key');
    }
  };

  const handleRotate = async (id: string, name: string) => {
    if (
      !confirm(
        `Are you sure you want to rotate the API key "${name}"? The old key will stop working immediately.`
      )
    )
      return;

    try {
      const response = await rotateKey.mutateAsync(id);
      setCreatedKey(response.key);
      toast.success('API key rotated');
    } catch (error: any) {
      toast.error(error.message || 'Failed to rotate API key');
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
    toast.success('Copied to clipboard');
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium text-white">API Keys</h1>
            <p className="text-zinc-400 mt-1">
              Manage API keys for programmatic access to Synthesize.io
            </p>
          </div>
          <Button
            variant="gradient"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Key
          </Button>
        </div>

        {/* New Key Created */}
        {createdKey && (
          <Card glass className="border-emerald-500/30 bg-emerald-500/10">
            <CardContent className="py-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-emerald-300">API Key Created</h4>
                  <p className="text-sm text-emerald-400 mt-1">
                    Make sure to copy your API key now. You won't be able to see it again!
                  </p>
                  <div className="flex items-center gap-2 mt-3">
                    <code className="flex-1 px-3 py-2 bg-white/5 border border-emerald-500/30 rounded-lg text-sm font-mono text-white">
                      {createdKey}
                    </code>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(createdKey, 'new')}
                    >
                      {copiedId === 'new' ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2"
                    onClick={() => setCreatedKey(null)}
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Create Key Modal */}
        {showCreateModal && (
          <Card glass>
            <CardHeader>
              <CardTitle>Create API Key</CardTitle>
              <CardDescription>
                Create a new API key to access Synthesize.io programmatically
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Key Name"
                placeholder="e.g., Production Server"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
              <div className="flex gap-2">
                <Button variant="gradient" onClick={handleCreate} loading={createKey.isPending}>
                  Create Key
                </Button>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* API Keys List */}
        <Card glass>
          <CardHeader>
            <CardTitle>Your API Keys</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
              </div>
            ) : !keys || keys.length === 0 ? (
              <div className="text-center py-12">
                <Key className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
                <p className="text-zinc-500">No API keys yet</p>
                <p className="text-sm text-zinc-500 mt-1">
                  Create your first API key to get started
                </p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {keys.map((key) => (
                  <div key={key.id} className="flex items-center gap-4 px-6 py-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
                      <Key className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-white">{key.name}</h4>
                        {key.is_active ? (
                          <Badge variant="success" size="sm">
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="error" size="sm">
                            Revoked
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-zinc-500">
                        {key.prefix}... • Created {formatDate(key.created_at)}
                        {key.last_used_at && ` • Last used ${formatDate(key.last_used_at)}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRotate(key.id, key.name)}
                        title="Rotate key"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(key.id, key.name)}
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        title="Delete key"
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

        {/* Usage Instructions */}
        <Card glass>
          <CardHeader>
            <CardTitle>Using Your API Key</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-zinc-400">
              Include your API key in the <code className="px-1 bg-white/10 rounded">Authorization</code>{' '}
              header of your requests:
            </p>
            <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg text-sm overflow-x-auto">
              {`curl -X GET "https://api.synthesize.io/v1/datasets" \\
  -H "Authorization: Bearer YOUR_API_KEY"`}
            </pre>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
