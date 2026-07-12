'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { WebhookEvent } from '@synthesize/types';
import {
  useWebhooks,
  useCreateWebhook,
  useDeleteWebhook,
  useTestWebhook,
} from '@/hooks/use-api';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Plus,
  Webhook,
  Trash2,
  Send,
  CheckCircle,
  XCircle,
  Loader2,
  Copy,
  Eye,
  EyeOff,
} from 'lucide-react';
import Link from 'next/link';

const WEBHOOK_EVENTS = [
  { value: 'job.completed', label: 'Job Completed' },
  { value: 'job.failed', label: 'Job Failed' },
  { value: 'dataset.created', label: 'Dataset Created' },
  { value: 'dataset.updated', label: 'Dataset Updated' },
  { value: 'dataset.deleted', label: 'Dataset Deleted' },
];

export default function WebhooksPage() {
  const { data: webhooks, isLoading } = useWebhooks();
  const createWebhook = useCreateWebhook();
  const deleteWebhook = useDeleteWebhook();
  const testWebhook = useTestWebhook();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWebhook, setNewWebhook] = useState<{
    url: string;
    events: WebhookEvent[];
  }>({
    url: '',
    events: [],
  });

  const handleCreate = async () => {
    if (!newWebhook.url.trim()) {
      toast.error('Please enter a webhook URL');
      return;
    }
    if (newWebhook.events.length === 0) {
      toast.error('Please select at least one event');
      return;
    }

    try {
      await createWebhook.mutateAsync({
        url: newWebhook.url,
        events: newWebhook.events,
      });
      setNewWebhook({ url: '', events: [] });
      setShowCreateModal(false);
      toast.success('Webhook created');
    } catch (error: any) {
      toast.error(error.message || 'Failed to create webhook');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return;

    try {
      await deleteWebhook.mutateAsync(id);
      toast.success('Webhook deleted');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete webhook');
    }
  };

  const handleTest = async (id: string) => {
    try {
      const result = await testWebhook.mutateAsync({ id, event: 'job.completed' });
      if (result.success) {
        toast.success('Test webhook sent successfully');
      } else {
        toast.error(`Test failed with status ${result.status_code}`);
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to test webhook');
    }
  };

  const toggleEvent = (event: WebhookEvent) => {
    setNewWebhook((prev) => ({
      ...prev,
      events: prev.events.includes(event)
        ? prev.events.filter((e) => e !== event)
        : [...prev.events, event],
    }));
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium text-white">Webhooks</h1>
            <p className="text-zinc-400 mt-1">
              Receive real-time notifications when events occur
            </p>
          </div>
          <Button
            variant="gradient"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Webhook
          </Button>
        </div>

        {/* Create Webhook Modal */}
        {showCreateModal && (
          <Card glass>
            <CardHeader>
              <CardTitle>Add Webhook</CardTitle>
              <CardDescription>
                Configure a new webhook endpoint to receive event notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Webhook URL"
                placeholder="https://your-app.com/webhook"
                value={newWebhook.url}
                onChange={(e) =>
                  setNewWebhook((prev) => ({ ...prev, url: e.target.value }))
                }
              />

              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  Events to receive
                </label>
                <div className="flex flex-wrap gap-2">
                  {WEBHOOK_EVENTS.map((event) => (
                    <button
                      key={event.value}
                      type="button"
                      onClick={() => toggleEvent(event.value as WebhookEvent)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        newWebhook.events.includes(event.value as WebhookEvent)
                          ? 'bg-teal-500/20 text-teal-300 border-2 border-teal-500'
                          : 'bg-white/10 text-zinc-300 border-2 border-transparent hover:bg-white/10'
                      }`}
                    >
                      {event.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="gradient" onClick={handleCreate} loading={createWebhook.isPending}>
                  Create Webhook
                </Button>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Webhooks List */}
        <Card glass>
          <CardHeader>
            <CardTitle>Your Webhooks</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
              </div>
            ) : !webhooks || webhooks.length === 0 ? (
              <div className="text-center py-12">
                <Webhook className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
                <p className="text-zinc-500">No webhooks configured</p>
                <p className="text-sm text-zinc-500 mt-1">
                  Add a webhook to receive real-time notifications
                </p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {webhooks.map((webhook) => (
                  <WebhookRow
                    key={webhook.id}
                    webhook={webhook}
                    onDelete={() => handleDelete(webhook.id)}
                    onTest={() => handleTest(webhook.id)}
                    isTesting={testWebhook.isPending}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Webhook Documentation */}
        <Card glass>
          <CardHeader>
            <CardTitle>Webhook Payload</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-zinc-400">
              Webhook events are sent as POST requests with a JSON payload. Each request includes
              a signature header for verification.
            </p>
            <pre className="p-4 bg-zinc-900 text-zinc-100 rounded-lg text-sm overflow-x-auto">
              {`{
  "id": "evt_123456",
  "type": "job.completed",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job_789",
    "dataset_id": "ds_456",
    "row_count": 10000,
    "format": "json"
  }
}`}
            </pre>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

function WebhookRow({
  webhook,
  onDelete,
  onTest,
  isTesting,
}: {
  webhook: any;
  onDelete: () => void;
  onTest: () => void;
  isTesting: boolean;
}) {
  const [showSecret, setShowSecret] = useState(false);

  return (
    <div className="px-6 py-4">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <code className="text-sm font-mono text-white truncate">{webhook.url}</code>
            {webhook.is_active ? (
              <Badge variant="success" size="sm">
                Active
              </Badge>
            ) : (
              <Badge variant="error" size="sm">
                Disabled
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {webhook.events?.map((event: string) => (
              <Badge key={event} variant="default" size="sm">
                {event}
              </Badge>
            ))}
          </div>
          <p className="text-sm text-zinc-500 mt-2">
            Created {formatRelativeTime(webhook.created_at)}
            {webhook.last_triggered_at && ` • Last triggered ${formatRelativeTime(webhook.last_triggered_at)}`}
          </p>
        </div>
        <div className="flex items-center gap-1 ml-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onTest}
            loading={isTesting}
            title="Send test event"
          >
            <Send className="w-4 h-4" />
          </Button>
          <Link href={`/settings/webhooks/${webhook.id}`}>
            <Button variant="ghost" size="sm" title="View deliveries">
              <Eye className="w-4 h-4" />
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={onDelete}
            className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
            title="Delete webhook"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
