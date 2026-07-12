'use client';

import { useState } from 'react';
import { useOrganizationContext } from '@/providers/organization-provider';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Activity,
  Users,
  Database,
  Settings,
  Mail,
  Download,
  Upload,
  Trash2,
  Shield,
  Clock,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  UserPlus,
  UserMinus,
  FileText,
  Eye,
  Edit,
} from 'lucide-react';

interface ActivityEvent {
  id: string;
  type: string;
  user_name: string;
  user_email: string;
  resource_type?: string;
  resource_name?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

// Mock activity data
const mockActivities: ActivityEvent[] = [
  {
    id: '1',
    type: 'dataset.created',
    user_name: 'John Smith',
    user_email: 'john@example.com',
    resource_type: 'dataset',
    resource_name: 'Customer Analytics',
    created_at: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    type: 'member.added',
    user_name: 'Sarah Johnson',
    user_email: 'sarah@example.com',
    resource_type: 'member',
    resource_name: 'Mike Wilson',
    metadata: { role: 'member' },
    created_at: '2024-01-15T09:15:00Z',
  },
  {
    id: '3',
    type: 'dataset.exported',
    user_name: 'Mike Wilson',
    user_email: 'mike@example.com',
    resource_type: 'dataset',
    resource_name: 'Sales Data 2024',
    metadata: { format: 'xlsx', rows: 50000 },
    created_at: '2024-01-14T16:45:00Z',
  },
  {
    id: '4',
    type: 'invite.sent',
    user_name: 'John Smith',
    user_email: 'john@example.com',
    resource_type: 'invite',
    resource_name: 'alice@example.com',
    metadata: { role: 'viewer' },
    created_at: '2024-01-14T14:20:00Z',
  },
  {
    id: '5',
    type: 'dataset.shared',
    user_name: 'Sarah Johnson',
    user_email: 'sarah@example.com',
    resource_type: 'dataset',
    resource_name: 'E-commerce Transactions',
    metadata: { access_level: 'edit' },
    created_at: '2024-01-14T11:30:00Z',
  },
  {
    id: '6',
    type: 'organization.settings_changed',
    user_name: 'John Smith',
    user_email: 'john@example.com',
    resource_type: 'settings',
    metadata: { changed: ['billing_email', 'name'] },
    created_at: '2024-01-13T15:00:00Z',
  },
  {
    id: '7',
    type: 'member.role_changed',
    user_name: 'John Smith',
    user_email: 'john@example.com',
    resource_type: 'member',
    resource_name: 'Sarah Johnson',
    metadata: { old_role: 'member', new_role: 'admin' },
    created_at: '2024-01-13T10:45:00Z',
  },
  {
    id: '8',
    type: 'dataset.deleted',
    user_name: 'Mike Wilson',
    user_email: 'mike@example.com',
    resource_type: 'dataset',
    resource_name: 'Test Dataset',
    created_at: '2024-01-12T09:00:00Z',
  },
];

const activityTypes = [
  { value: '', label: 'All Activities' },
  { value: 'dataset', label: 'Dataset' },
  { value: 'member', label: 'Members' },
  { value: 'invite', label: 'Invites' },
  { value: 'settings', label: 'Settings' },
];

export default function TeamActivityPage() {
  const { currentOrganization } = useOrganizationContext();
  const [activities] = useState<ActivityEvent[]>(mockActivities);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [page, setPage] = useState(1);
  const perPage = 10;

  const filteredActivities = activities.filter((activity) => {
    const matchesSearch =
      !search ||
      activity.user_name.toLowerCase().includes(search.toLowerCase()) ||
      activity.resource_name?.toLowerCase().includes(search.toLowerCase());
    const matchesType =
      !typeFilter || activity.type.startsWith(typeFilter);
    return matchesSearch && matchesType;
  });

  const paginatedActivities = filteredActivities.slice(
    (page - 1) * perPage,
    page * perPage
  );

  const totalPages = Math.ceil(filteredActivities.length / perPage);

  return (
    <div className="space-y-6">
      {/* Activity Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCard
          title="Today"
          value={activities.filter(a => 
            new Date(a.created_at).toDateString() === new Date().toDateString()
          ).length}
          icon={Activity}
          color="teal"
        />
        <StatCard
          title="This Week"
          value={activities.filter(a => {
            const date = new Date(a.created_at);
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return date >= weekAgo;
          }).length}
          icon={Clock}
          color="blue"
        />
        <StatCard
          title="Dataset Events"
          value={activities.filter(a => a.type.startsWith('dataset')).length}
          icon={Database}
          color="purple"
        />
        <StatCard
          title="Member Events"
          value={activities.filter(a => 
            a.type.startsWith('member') || a.type.startsWith('invite')
          ).length}
          icon={Users}
          color="amber"
        />
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search activities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
          />
        </div>
        <div className="flex gap-1 p-1 bg-white/5 rounded-lg border border-white/10">
          {activityTypes.map((type) => (
            <button
              key={type.value}
              onClick={() => setTypeFilter(type.value)}
              className={`px-3 py-1.5 text-sm rounded-md transition-all ${
                typeFilter === type.value
                  ? 'bg-teal-500/20 text-teal-400'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Activity Feed */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-teal-400" />
            Activity Feed
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            {paginatedActivities.map((activity, index) => (
              <ActivityRow key={activity.id} activity={activity} index={index} />
            ))}
            {paginatedActivities.length === 0 && (
              <div className="text-center py-12 text-gray-400">
                <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No activities found</p>
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/10">
              <p className="text-sm text-gray-400">
                Showing {(page - 1) * perPage + 1} to{' '}
                {Math.min(page * perPage, filteredActivities.length)} of{' '}
                {filteredActivities.length} activities
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                  className="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    teal: 'from-teal-500/20 to-emerald-500/20 border-teal-500/30 text-teal-400',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400',
    amber: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400',
  };

  return (
    <div className="p-4 bg-white/[0.03] rounded-xl border border-white/10">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-medium text-white mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]} border`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}

function ActivityRow({ activity, index }: { activity: ActivityEvent; index: number }) {
  const getActivityConfig = (type: string) => {
    const configs: Record<string, { icon: any; color: string; label: string }> = {
      'dataset.created': { icon: Database, color: 'text-emerald-400 bg-emerald-500/10', label: 'created dataset' },
      'dataset.updated': { icon: Edit, color: 'text-blue-400 bg-blue-500/10', label: 'updated dataset' },
      'dataset.deleted': { icon: Trash2, color: 'text-red-400 bg-red-500/10', label: 'deleted dataset' },
      'dataset.exported': { icon: Download, color: 'text-purple-400 bg-purple-500/10', label: 'exported dataset' },
      'dataset.shared': { icon: Users, color: 'text-teal-400 bg-teal-500/10', label: 'shared dataset' },
      'dataset.unshared': { icon: Eye, color: 'text-gray-400 bg-gray-500/10', label: 'unshared dataset' },
      'member.added': { icon: UserPlus, color: 'text-emerald-400 bg-emerald-500/10', label: 'added member' },
      'member.removed': { icon: UserMinus, color: 'text-red-400 bg-red-500/10', label: 'removed member' },
      'member.role_changed': { icon: Shield, color: 'text-amber-400 bg-amber-500/10', label: 'changed role for' },
      'invite.sent': { icon: Mail, color: 'text-blue-400 bg-blue-500/10', label: 'sent invite to' },
      'invite.accepted': { icon: UserPlus, color: 'text-emerald-400 bg-emerald-500/10', label: 'accepted invite' },
      'invite.canceled': { icon: Mail, color: 'text-gray-400 bg-gray-500/10', label: 'canceled invite for' },
      'organization.settings_changed': { icon: Settings, color: 'text-purple-400 bg-purple-500/10', label: 'updated settings' },
    };
    return configs[type] || { icon: Activity, color: 'text-gray-400 bg-gray-500/10', label: type };
  };

  const config = getActivityConfig(activity.type);
  const Icon = config.icon;

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div
      className="flex items-start gap-4 p-4 rounded-lg hover:bg-white/[0.02] transition-colors animate-fade-in"
      style={{ animationDelay: `${index * 30}ms` }}
    >
      <div className={`p-2.5 rounded-lg ${config.color}`}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-white">
          <span className="font-medium">{activity.user_name}</span>
          <span className="text-gray-400"> {config.label} </span>
          {activity.resource_name && (
            <span className="font-medium text-teal-400">{activity.resource_name}</span>
          )}
        </p>
        {activity.metadata && (
          <div className="flex flex-wrap gap-2 mt-1">
            {activity.metadata.format && (
              <Badge className="text-xs bg-white/5 text-gray-400 border-white/10">
                {activity.metadata.format.toUpperCase()}
              </Badge>
            )}
            {activity.metadata.rows && (
              <Badge className="text-xs bg-white/5 text-gray-400 border-white/10">
                {activity.metadata.rows.toLocaleString()} rows
              </Badge>
            )}
            {activity.metadata.role && (
              <Badge className="text-xs bg-white/5 text-gray-400 border-white/10">
                {activity.metadata.role}
              </Badge>
            )}
            {activity.metadata.old_role && activity.metadata.new_role && (
              <Badge className="text-xs bg-white/5 text-gray-400 border-white/10">
                {activity.metadata.old_role} → {activity.metadata.new_role}
              </Badge>
            )}
            {activity.metadata.access_level && (
              <Badge className="text-xs bg-white/5 text-gray-400 border-white/10">
                {activity.metadata.access_level} access
              </Badge>
            )}
          </div>
        )}
        <p className="text-xs text-gray-500 mt-1">{formatTime(activity.created_at)}</p>
      </div>
    </div>
  );
}
