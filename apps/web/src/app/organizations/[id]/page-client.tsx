'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  useOrganization,
  useOrganizationMembers,
  useOrganizationInvites,
  useSendInvite,
  useCancelInvite,
  useUpdateMemberRole,
  useRemoveMember,
  useUpdateOrganization,
  useDeleteOrganization,
} from '@/hooks/use-api';
import { useOrganizationContext } from '@/providers/organization-provider';
import { toast } from 'sonner';
import {
  Building2,
  Users,
  Mail,
  Settings,
  Crown,
  Shield,
  Eye,
  Loader2,
  Plus,
  Trash2,
  MoreHorizontal,
  ArrowLeft,
  Copy,
  Check,
  AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

const roleConfig = {
  owner: { label: 'Owner', color: 'bg-amber-500/20 text-amber-400 border-amber-500/30', icon: Crown },
  admin: { label: 'Admin', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: Shield },
  member: { label: 'Member', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: Users },
  viewer: { label: 'Viewer', color: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30', icon: Eye },
};

const roles = ['admin', 'member', 'viewer'] as const;

export default function OrganizationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const orgId = params.id as string;

  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<string>('member');
  const [isInviting, setIsInviting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [memberToRemove, setMemberToRemove] = useState<any>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);

  const { switchOrganization } = useOrganizationContext();
  const { data: org, isLoading: orgLoading } = useOrganization(orgId);
  const { data: members = [], isLoading: membersLoading } = useOrganizationMembers(orgId);
  const { data: invites = [], isLoading: invitesLoading } = useOrganizationInvites(orgId);

  const sendInvite = useSendInvite();
  const cancelInvite = useCancelInvite();
  const updateRole = useUpdateMemberRole();
  const removeMember = useRemoveMember();
  const deleteOrg = useDeleteOrganization();

  const isLoading = orgLoading || membersLoading || invitesLoading;

  // Get current user's role in this org
  const currentUserRole = (members as any[]).find((m: any) => m.is_current_user)?.role || 'member';
  const isAdmin = currentUserRole === 'owner' || currentUserRole === 'admin';
  const isOwner = currentUserRole === 'owner';

  const handleSendInvite = async () => {
    if (!inviteEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    setIsInviting(true);
    try {
      await sendInvite.mutateAsync({ orgId, email: inviteEmail, role: inviteRole });
      toast.success(`Invitation sent to ${inviteEmail}`);
      setInviteEmail('');
      setShowInviteForm(false);
    } catch (error: any) {
      toast.error(error.message || 'Failed to send invite');
    } finally {
      setIsInviting(false);
    }
  };

  const handleCancelInvite = async (inviteId: string) => {
    try {
      await cancelInvite.mutateAsync({ orgId, inviteId });
      toast.success('Invitation cancelled');
    } catch (error: any) {
      toast.error(error.message || 'Failed to cancel invite');
    }
  };

  const handleUpdateRole = async (memberId: string, newRole: string) => {
    try {
      await updateRole.mutateAsync({ orgId, memberId, role: newRole });
      toast.success('Role updated');
    } catch (error: any) {
      toast.error(error.message || 'Failed to update role');
    }
  };

  const handleRemoveMember = async () => {
    if (!memberToRemove) return;
    try {
      await removeMember.mutateAsync({ orgId, memberId: memberToRemove.id });
      toast.success('Member removed');
      setMemberToRemove(null);
    } catch (error: any) {
      toast.error(error.message || 'Failed to remove member');
    }
  };

  const handleDeleteOrg = async () => {
    try {
      await deleteOrg.mutateAsync(orgId);
      toast.success('Organization deleted');
      router.push('/organizations');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete organization');
    }
  };

  const handleSwitchToOrg = () => {
    switchOrganization(orgId);
    router.push('/dashboard');
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
        </div>
      </DashboardLayout>
    );
  }

  if (!org) {
    return (
      <DashboardLayout>
        <div className="text-center py-24">
          <Building2 className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <h2 className="text-xl font-medium text-white mb-2">Organization not found</h2>
          <p className="text-zinc-500 mb-4">The organization you're looking for doesn't exist or you don't have access.</p>
          <Link href="/organizations">
            <Button variant="outline">Back to Organizations</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/organizations">
            <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-medium text-white">{(org as any).name?.charAt(0).toUpperCase()}</span>
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-medium text-white">{(org as any).name}</h1>
            <p className="text-zinc-500">{(members as any[]).length} member{(members as any[]).length !== 1 ? 's' : ''}</p>
          </div>
          <Button variant="gradient" onClick={handleSwitchToOrg}>
            Switch to this workspace
          </Button>
        </div>

        <Tabs defaultValue="members" className="space-y-6">
          <TabsList className="bg-zinc-900/50 border border-white/10">
            <TabsTrigger value="members" className="data-[state=active]:bg-teal-500/20 data-[state=active]:text-teal-400">
              <Users className="w-4 h-4 mr-2" />
              Members
            </TabsTrigger>
            <TabsTrigger value="invites" className="data-[state=active]:bg-teal-500/20 data-[state=active]:text-teal-400">
              <Mail className="w-4 h-4 mr-2" />
              Invites
            </TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="settings" className="data-[state=active]:bg-teal-500/20 data-[state=active]:text-teal-400">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </TabsTrigger>
            )}
          </TabsList>

          {/* Members Tab */}
          <TabsContent value="members" className="space-y-4">
            <Card className="bg-zinc-900/50 border-white/10">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">Team Members</CardTitle>
                  <CardDescription>Manage who has access to this organization</CardDescription>
                </div>
                {isAdmin && (
                  <Button variant="gradient" size="sm" onClick={() => setShowInviteForm(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Invite Member
                  </Button>
                )}
              </CardHeader>
              <CardContent className="divide-y divide-white/5">
                {(members as any[]).map((member: any) => {
                  const role = roleConfig[member.role as keyof typeof roleConfig] || roleConfig.member;
                  const RoleIcon = role.icon;

                  return (
                    <div key={member.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                      <Avatar className="w-10 h-10 bg-gradient-to-br from-teal-500/50 to-emerald-500/50">
                        <AvatarFallback className="bg-transparent text-white">
                          {member.name?.charAt(0) || member.email?.charAt(0) || '?'}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate">
                          {member.name || 'Unnamed User'}
                          {member.is_current_user && (
                            <span className="text-zinc-500 text-sm ml-2">(you)</span>
                          )}
                        </p>
                        <p className="text-sm text-zinc-500 truncate">{member.email}</p>
                      </div>
                      <Badge className={`${role.color} border`}>
                        <RoleIcon className="w-3 h-3 mr-1" />
                        {role.label}
                      </Badge>
                      {isAdmin && member.role !== 'owner' && !member.is_current_user && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="text-zinc-400">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="bg-zinc-900 border-white/10">
                            {roles.map((r) => (
                              <DropdownMenuItem
                                key={r}
                                onClick={() => handleUpdateRole(member.id, r)}
                                className="text-zinc-300 focus:bg-white/5"
                              >
                                {r === member.role && <Check className="w-4 h-4 mr-2" />}
                                {!r && <span className="w-4 mr-2" />}
                                Make {r.charAt(0).toUpperCase() + r.slice(1)}
                              </DropdownMenuItem>
                            ))}
                            <DropdownMenuSeparator className="bg-white/10" />
                            <DropdownMenuItem
                              onClick={() => setMemberToRemove(member)}
                              className="text-red-400 focus:bg-red-500/10"
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Remove
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Invites Tab */}
          <TabsContent value="invites" className="space-y-4">
            {/* Invite Form */}
            {showInviteForm && isAdmin && (
              <Card className="bg-zinc-900/50 border-teal-500/30 border-2">
                <CardHeader>
                  <CardTitle className="text-white">Invite New Member</CardTitle>
                  <CardDescription>Send an invitation to join this organization</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-zinc-300">Email Address</Label>
                      <Input
                        type="email"
                        placeholder="colleague@company.com"
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-zinc-300">Role</Label>
                      <select
                        value={inviteRole}
                        onChange={(e) => setInviteRole(e.target.value)}
                        className="mt-1 w-full h-10 rounded-md border border-white/10 bg-zinc-900 px-3 text-white"
                      >
                        <option value="admin">Admin - Can manage team</option>
                        <option value="member">Member - Can create datasets</option>
                        <option value="viewer">Viewer - Read only access</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex gap-2 justify-end">
                    <Button variant="outline" onClick={() => setShowInviteForm(false)}>
                      Cancel
                    </Button>
                    <Button variant="gradient" onClick={handleSendInvite} disabled={isInviting}>
                      {isInviting ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Mail className="w-4 h-4 mr-2" />
                      )}
                      Send Invite
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Pending Invites */}
            <Card className="bg-zinc-900/50 border-white/10">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">Pending Invitations</CardTitle>
                  <CardDescription>Invites waiting to be accepted</CardDescription>
                </div>
                {!showInviteForm && isAdmin && (
                  <Button variant="outline" size="sm" onClick={() => setShowInviteForm(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Invite
                  </Button>
                )}
              </CardHeader>
              <CardContent>
                {(invites as any[]).length === 0 ? (
                  <p className="text-zinc-500 text-center py-6">No pending invitations</p>
                ) : (
                  <div className="divide-y divide-white/5">
                    {(invites as any[]).map((invite: any) => {
                      const role = roleConfig[invite.role as keyof typeof roleConfig] || roleConfig.member;

                      return (
                        <div key={invite.id} className="flex items-center gap-4 py-3 first:pt-0 last:pb-0">
                          <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center">
                            <Mail className="w-5 h-5 text-zinc-500" />
                          </div>
                          <div className="flex-1">
                            <p className="text-white">{invite.email}</p>
                            <p className="text-sm text-zinc-500">
                              Expires {new Date(invite.expires_at).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge className={`${role.color} border`}>{role.label}</Badge>
                          {isAdmin && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-zinc-400 hover:text-red-400"
                              onClick={() => handleCancelInvite(invite.id)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          {isAdmin && (
            <TabsContent value="settings" className="space-y-4">
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Organization Settings</CardTitle>
                  <CardDescription>Manage organization details and preferences</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="text-zinc-300">Organization ID</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Input value={orgId} readOnly className="bg-zinc-800 font-mono text-sm" />
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => {
                          navigator.clipboard.writeText(orgId);
                          toast.success('Copied to clipboard');
                        }}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Danger Zone */}
              {isOwner && (
                <Card className="bg-zinc-900/50 border-red-500/30">
                  <CardHeader>
                    <CardTitle className="text-red-400 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      Danger Zone
                    </CardTitle>
                    <CardDescription>Irreversible actions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                      <div>
                        <p className="font-medium text-white">Delete Organization</p>
                        <p className="text-sm text-zinc-400">
                          This will permanently delete the organization and all associated data.
                        </p>
                      </div>
                      <Button
                        variant="destructive"
                        onClick={() => setShowDeleteDialog(true)}
                      >
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          )}
        </Tabs>
      </div>

      {/* Remove Member Dialog */}
      <AlertDialog open={!!memberToRemove} onOpenChange={() => setMemberToRemove(null)}>
        <AlertDialogContent className="bg-zinc-900 border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Remove Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove {memberToRemove?.name || memberToRemove?.email} from this organization?
              They will lose access to all organization resources.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-zinc-800 border-white/10 text-white hover:bg-zinc-700">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-600 hover:bg-red-700"
              onClick={handleRemoveMember}
            >
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Org Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent className="bg-zinc-900 border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Delete Organization</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the organization
              "{(org as any).name}" and remove all member associations.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-zinc-800 border-white/10 text-white hover:bg-zinc-700">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-600 hover:bg-red-700"
              onClick={handleDeleteOrg}
            >
              Delete Organization
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
}
