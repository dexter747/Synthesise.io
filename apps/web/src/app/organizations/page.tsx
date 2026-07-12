'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useOrganizations, useCreateOrganization, useMyInvites, useAcceptInvite, useDeclineInvite } from '@/hooks/use-api';
import { toast } from 'sonner';
import {
  Building2,
  Plus,
  Users,
  Mail,
  CheckCircle2,
  XCircle,
  Loader2,
  ExternalLink,
  Crown,
  Shield,
  Eye,
  Settings,
  ChevronRight,
} from 'lucide-react';
import Link from 'next/link';

const roleConfig = {
  owner: { label: 'Owner', color: 'bg-amber-500/20 text-amber-400 border-amber-500/30', icon: Crown },
  admin: { label: 'Admin', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: Shield },
  member: { label: 'Member', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: Users },
  viewer: { label: 'Viewer', color: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30', icon: Eye },
};

export default function OrganizationsPage() {
  const [isCreating, setIsCreating] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const { data: organizations = [], isLoading: orgsLoading } = useOrganizations();
  const { data: invites = [], isLoading: invitesLoading } = useMyInvites();
  const createOrg = useCreateOrganization();
  const acceptInvite = useAcceptInvite();
  const declineInvite = useDeclineInvite();

  const handleCreateOrg = async () => {
    if (!newOrgName.trim()) {
      toast.error('Please enter an organization name');
      return;
    }

    setIsCreating(true);
    try {
      await createOrg.mutateAsync({ name: newOrgName });
      toast.success('Organization created successfully!');
      setNewOrgName('');
      setShowCreateForm(false);
    } catch (error: any) {
      toast.error(error.message || 'Failed to create organization');
    } finally {
      setIsCreating(false);
    }
  };

  const handleAcceptInvite = async (inviteId: string, orgName: string) => {
    try {
      await acceptInvite.mutateAsync(inviteId);
      toast.success(`Joined ${orgName}!`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to accept invite');
    }
  };

  const handleDeclineInvite = async (inviteId: string) => {
    try {
      await declineInvite.mutateAsync(inviteId);
      toast.success('Invite declined');
    } catch (error: any) {
      toast.error(error.message || 'Failed to decline invite');
    }
  };

  const isLoading = orgsLoading || invitesLoading;
  const orgList = organizations || [];
  const inviteList = invites || [];

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium text-white">Organizations</h1>
            <p className="text-zinc-400 mt-1">Manage your organizations and memberships</p>
          </div>
          {!showCreateForm && (
            <Button variant="gradient" onClick={() => setShowCreateForm(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Organization
            </Button>
          )}
        </div>

        {/* Create Organization Form */}
        {showCreateForm && (
          <Card className="bg-zinc-900/50 border-teal-500/30 border-2">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Building2 className="w-5 h-5 text-teal-400" />
                Create New Organization
              </CardTitle>
              <CardDescription>Create a new workspace for your team</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <Input
                  placeholder="Organization name"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  className="flex-1"
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateOrg()}
                />
                <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                  Cancel
                </Button>
                <Button variant="gradient" onClick={handleCreateOrg} disabled={isCreating}>
                  {isCreating ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Plus className="w-4 h-4 mr-2" />
                  )}
                  Create
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pending Invites */}
        {inviteList.length > 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Mail className="w-5 h-5 text-teal-400" />
                Pending Invitations
              </CardTitle>
              <CardDescription>You have been invited to join these organizations</CardDescription>
            </CardHeader>
            <CardContent className="divide-y divide-white/5">
              {inviteList.map((invite: any) => (
                <div key={invite.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-teal-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-white">{invite.organization_name}</h3>
                    <p className="text-sm text-zinc-500">
                      Invited as {invite.role} • Expires {new Date(invite.expires_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-zinc-400 hover:text-red-400"
                      onClick={() => handleDeclineInvite(invite.id)}
                      disabled={declineInvite.isPending}
                    >
                      <XCircle className="w-4 h-4 mr-1" />
                      Decline
                    </Button>
                    <Button
                      variant="gradient"
                      size="sm"
                      onClick={() => handleAcceptInvite(invite.id, invite.organization_name)}
                      disabled={acceptInvite.isPending}
                    >
                      <CheckCircle2 className="w-4 h-4 mr-1" />
                      Accept
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Organizations List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
          </div>
        ) : orgList.length === 0 ? (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="py-12 text-center">
              <Building2 className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-white mb-2">No Organizations Yet</h3>
              <p className="text-zinc-500 mb-4">
                Create an organization to start collaborating with your team
              </p>
              <Button variant="gradient" onClick={() => setShowCreateForm(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Organization
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {orgList.map((org: any) => {
              const role = roleConfig[org.role as keyof typeof roleConfig] || roleConfig.member;
              const RoleIcon = role.icon;
              
              return (
                <Card key={org.id} className="bg-zinc-900/50 border-white/10 hover:border-white/20 transition-colors">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
                        <span className="text-xl font-medium text-white">
                          {org.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-medium text-white truncate">{org.name}</h3>
                          <Badge className={`${role.color} border`}>
                            <RoleIcon className="w-3 h-3 mr-1" />
                            {role.label}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-zinc-500">
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            {org.member_count || 1} member{(org.member_count || 1) !== 1 ? 's' : ''}
                          </span>
                          <span>Created {new Date(org.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {(org.role === 'owner' || org.role === 'admin') && (
                          <Link href={`/organizations/${org.id}`}>
                            <Button variant="outline" size="sm">
                              <Settings className="w-4 h-4 mr-1" />
                              Manage
                            </Button>
                          </Link>
                        )}
                        <Link href={`/dashboard?org=${org.id}`}>
                          <Button variant="ghost" size="icon">
                            <ChevronRight className="w-5 h-5 text-zinc-400" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
