'use client';

import { useState } from 'react';
import { useOrganizationContext } from '@/providers/organization-provider';
import { useAuth } from '@/providers/auth-provider';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Users,
  UserPlus,
  Mail,
  MoreVertical,
  Shield,
  ShieldCheck,
  Eye,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  Search,
  RefreshCw,
  Crown,
  Settings,
} from 'lucide-react';

interface Member {
  id: string;
  user_id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: 'admin' | 'member' | 'viewer';
  joined_at: string;
  last_active?: string;
}

interface Invite {
  id: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  status: 'pending' | 'accepted' | 'expired';
  created_at: string;
  expires_at: string;
}

// Mock data - replace with actual API calls
const mockMembers: Member[] = [
  {
    id: '1',
    user_id: 'u1',
    email: 'john@example.com',
    name: 'John Smith',
    role: 'admin',
    joined_at: '2024-01-01T00:00:00Z',
    last_active: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    user_id: 'u2',
    email: 'sarah@example.com',
    name: 'Sarah Johnson',
    role: 'member',
    joined_at: '2024-01-05T00:00:00Z',
    last_active: '2024-01-14T14:20:00Z',
  },
  {
    id: '3',
    user_id: 'u3',
    email: 'mike@example.com',
    name: 'Mike Wilson',
    role: 'viewer',
    joined_at: '2024-01-10T00:00:00Z',
    last_active: '2024-01-13T09:15:00Z',
  },
];

const mockInvites: Invite[] = [
  {
    id: 'i1',
    email: 'alice@example.com',
    role: 'member',
    status: 'pending',
    created_at: '2024-01-14T00:00:00Z',
    expires_at: '2024-01-21T00:00:00Z',
  },
];

export default function TeamMembersPage() {
  const { currentOrganization } = useOrganizationContext();
  const { user } = useAuth();
  const [members, setMembers] = useState<Member[]>(mockMembers);
  const [invites, setInvites] = useState<Invite[]>(mockInvites);
  const [search, setSearch] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const filteredMembers = members.filter(
    (m) =>
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.email.toLowerCase().includes(search.toLowerCase())
  );

  const isAdmin = true; // Check if current user is admin

  const handleInvite = async (email: string, role: string) => {
    try {
      setIsLoading(true);
      // API call would go here
      toast.success(`Invitation sent to ${email}`);
      setShowInviteModal(false);
    } catch (error) {
      toast.error('Failed to send invitation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this member?')) return;
    try {
      // API call would go here
      setMembers(members.filter((m) => m.id !== memberId));
      toast.success('Member removed');
    } catch (error) {
      toast.error('Failed to remove member');
    }
  };

  const handleUpdateRole = async (memberId: string, newRole: string) => {
    try {
      // API call would go here
      setMembers(
        members.map((m) =>
          m.id === memberId ? { ...m, role: newRole as Member['role'] } : m
        )
      );
      toast.success('Role updated');
    } catch (error) {
      toast.error('Failed to update role');
    }
  };

  const handleCancelInvite = async (inviteId: string) => {
    try {
      // API call would go here
      setInvites(invites.filter((i) => i.id !== inviteId));
      toast.success('Invitation canceled');
    } catch (error) {
      toast.error('Failed to cancel invitation');
    }
  };

  const handleResendInvite = async (inviteId: string) => {
    try {
      // API call would go here
      toast.success('Invitation resent');
    } catch (error) {
      toast.error('Failed to resend invitation');
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Total Members"
          value={members.length}
          icon={Users}
          color="teal"
        />
        <StatCard
          title="Pending Invites"
          value={invites.filter((i) => i.status === 'pending').length}
          icon={Mail}
          color="amber"
        />
        <StatCard
          title="Admins"
          value={members.filter((m) => m.role === 'admin').length}
          icon={Shield}
          color="purple"
        />
      </div>

      {/* Actions Bar */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search members..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
          />
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowInviteModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-teal-500 text-black font-medium rounded-lg hover:bg-teal-400 transition-colors"
          >
            <UserPlus className="w-4 h-4" />
            Invite Member
          </button>
        )}
      </div>

      {/* Members List */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-teal-400" />
            Team Members
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {filteredMembers.map((member) => (
              <MemberRow
                key={member.id}
                member={member}
                isAdmin={isAdmin}
                isCurrentUser={member.user_id === user?.id}
                onUpdateRole={handleUpdateRole}
                onRemove={handleRemoveMember}
              />
            ))}
            {filteredMembers.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                No members found
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Pending Invites */}
      {invites.filter((i) => i.status === 'pending').length > 0 && (
        <Card className="bg-white/[0.03] border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Mail className="w-5 h-5 text-amber-400" />
              Pending Invitations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {invites
                .filter((i) => i.status === 'pending')
                .map((invite) => (
                  <InviteRow
                    key={invite.id}
                    invite={invite}
                    isAdmin={isAdmin}
                    onCancel={handleCancelInvite}
                    onResend={handleResendInvite}
                  />
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invite Modal */}
      {showInviteModal && (
        <InviteModal
          onClose={() => setShowInviteModal(false)}
          onInvite={handleInvite}
          isLoading={isLoading}
        />
      )}
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
    amber: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400',
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

function MemberRow({
  member,
  isAdmin,
  isCurrentUser,
  onUpdateRole,
  onRemove,
}: {
  member: Member;
  isAdmin: boolean;
  isCurrentUser: boolean;
  onUpdateRole: (id: string, role: string) => void;
  onRemove: (id: string) => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  const roleConfig = {
    admin: { label: 'Admin', icon: ShieldCheck, color: 'text-purple-400 bg-purple-500/10 border-purple-500/30' },
    member: { label: 'Member', icon: Users, color: 'text-teal-400 bg-teal-500/10 border-teal-500/30' },
    viewer: { label: 'Viewer', icon: Eye, color: 'text-gray-400 bg-gray-500/10 border-gray-500/30' },
  };

  const config = roleConfig[member.role];
  const RoleIcon = config.icon;

  return (
    <div className="flex items-center justify-between p-4 bg-white/[0.02] rounded-lg border border-white/5 hover:border-white/10 transition-colors">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center text-white font-medium">
          {member.name.charAt(0).toUpperCase()}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-white font-medium">{member.name}</span>
            {isCurrentUser && (
              <Badge className="text-xs bg-teal-500/10 text-teal-400 border-teal-500/30">
                You
              </Badge>
            )}
          </div>
          <p className="text-sm text-gray-400">{member.email}</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Badge className={`${config.color} border`}>
          <RoleIcon className="w-3 h-3 mr-1" />
          {config.label}
        </Badge>

        {isAdmin && !isCurrentUser && (
          <div className="relative">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-2 rounded-lg hover:bg-white/5 transition-colors"
            >
              <MoreVertical className="w-4 h-4 text-gray-400" />
            </button>

            {menuOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
                <div className="absolute right-0 top-full mt-2 w-48 bg-[#111111] rounded-xl shadow-2xl border border-white/10 py-2 z-50">
                  <div className="px-3 py-1.5 text-xs text-gray-500 uppercase">Change Role</div>
                  {['admin', 'member', 'viewer'].map((role) => (
                    <button
                      key={role}
                      onClick={() => {
                        onUpdateRole(member.id, role);
                        setMenuOpen(false);
                      }}
                      className={`flex items-center gap-2 w-full px-4 py-2 text-sm text-left hover:bg-white/5 ${
                        member.role === role ? 'text-teal-400' : 'text-gray-300'
                      }`}
                    >
                      {member.role === role && <CheckCircle className="w-3 h-3" />}
                      <span className="capitalize">{role}</span>
                    </button>
                  ))}
                  <div className="border-t border-white/10 mt-2 pt-2">
                    <button
                      onClick={() => {
                        onRemove(member.id);
                        setMenuOpen(false);
                      }}
                      className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-400 hover:bg-red-500/10"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remove Member
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function InviteRow({
  invite,
  isAdmin,
  onCancel,
  onResend,
}: {
  invite: Invite;
  isAdmin: boolean;
  onCancel: (id: string) => void;
  onResend: (id: string) => void;
}) {
  const expiresIn = Math.ceil(
    (new Date(invite.expires_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className="flex items-center justify-between p-4 bg-amber-500/5 rounded-lg border border-amber-500/20">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-amber-500/10 flex items-center justify-center">
          <Mail className="w-5 h-5 text-amber-400" />
        </div>
        <div>
          <p className="text-white font-medium">{invite.email}</p>
          <div className="flex items-center gap-2 text-sm">
            <Badge className="text-xs bg-white/5 text-gray-400 border-white/10">
              {invite.role}
            </Badge>
            <span className="text-gray-500">•</span>
            <span className="text-gray-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Expires in {expiresIn} days
            </span>
          </div>
        </div>
      </div>

      {isAdmin && (
        <div className="flex items-center gap-2">
          <button
            onClick={() => onResend(invite.id)}
            className="px-3 py-1.5 text-sm text-teal-400 hover:bg-teal-500/10 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => onCancel(invite.id)}
            className="px-3 py-1.5 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

function InviteModal({
  onClose,
  onInvite,
  isLoading,
}: {
  onClose: () => void;
  onInvite: (email: string, role: string) => void;
  isLoading: boolean;
}) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('member');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    onInvite(email, role);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-[#0a0a0a] rounded-2xl border border-white/10 p-6 shadow-2xl">
        <h2 className="text-xl font-medium text-white mb-6 flex items-center gap-2">
          <UserPlus className="w-5 h-5 text-teal-400" />
          Invite Team Member
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="colleague@company.com"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Role
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'admin', label: 'Admin', desc: 'Full access', icon: ShieldCheck },
                { value: 'member', label: 'Member', desc: 'Create & edit', icon: Users },
                { value: 'viewer', label: 'Viewer', desc: 'View only', icon: Eye },
              ].map((r) => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() => setRole(r.value)}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    role === r.value
                      ? 'bg-teal-500/10 border-teal-500/50 text-white'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/20'
                  }`}
                >
                  <r.icon className={`w-4 h-4 mb-1 ${role === r.value ? 'text-teal-400' : ''}`} />
                  <div className="text-sm font-medium">{r.label}</div>
                  <div className="text-xs text-gray-500">{r.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !email}
              className="flex-1 px-4 py-2.5 bg-teal-500 text-black font-medium rounded-lg hover:bg-teal-400 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Sending...' : 'Send Invite'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
