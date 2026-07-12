'use client';

import { useState, useRef, useEffect } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Users,
  Plus,
  Mail,
  Crown,
  UserCog,
  Eye,
  Trash2,
  Send,
  Loader2,
  ChevronDown,
  Check,
  Shield,
} from 'lucide-react';
import { toast } from 'sonner';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  avatar_url?: string;
  joined_at: string;
}

interface PendingInvite {
  id: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  sent_at: string;
  expires_at: string;
}

const mockMembers: TeamMember[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    role: 'owner',
    joined_at: '2024-01-15',
  },
];

const mockInvites: PendingInvite[] = [];

const roleConfig = {
  owner: { label: 'Owner', description: 'Full access and billing', color: 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30', icon: Crown },
  admin: { label: 'Admin', description: 'Manage team and settings', color: 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30', icon: Shield },
  member: { label: 'Member', description: 'Create and manage datasets', color: 'bg-gradient-to-r from-blue-500/20 to-cyan-500/20 text-blue-400 border-blue-500/30', icon: Users },
  viewer: { label: 'Viewer', description: 'View only access', color: 'bg-gradient-to-r from-zinc-500/20 to-gray-500/20 text-zinc-400 border-zinc-500/30', icon: Eye },
};

// Custom Dropdown Component
function RoleDropdown({
  value,
  onChange,
  excludeOwner = true,
}: {
  value: 'admin' | 'member' | 'viewer';
  onChange: (value: 'admin' | 'member' | 'viewer') => void;
  excludeOwner?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const roles = excludeOwner 
    ? (['admin', 'member', 'viewer'] as const)
    : (['owner', 'admin', 'member', 'viewer'] as const);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentRole = roleConfig[value];
  const CurrentIcon = currentRole.icon;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-3 px-4 py-2.5 rounded-lg border transition-all w-full min-w-[160px] ${
          isOpen 
            ? 'border-teal-500 bg-teal-500/10 ring-2 ring-teal-500/20' 
            : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'
        }`}
      >
        <CurrentIcon className={`w-4 h-4 ${currentRole.color.split(' ')[1]}`} />
        <span className="text-white flex-1 text-left">{currentRole.label}</span>
        <ChevronDown className={`w-4 h-4 text-zinc-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-50 top-full left-0 right-0 mt-2 py-2 bg-zinc-900 border border-white/10 rounded-lg shadow-xl backdrop-blur-xl animate-in fade-in slide-in-from-top-2 duration-200">
          {roles.map((role) => {
            const config = roleConfig[role as keyof typeof roleConfig];
            const Icon = config.icon;
            const isSelected = value === role;
            
            return (
              <button
                key={role}
                type="button"
                onClick={() => {
                  onChange(role as 'admin' | 'member' | 'viewer');
                  setIsOpen(false);
                }}
                className={`w-full flex items-start gap-3 px-4 py-3 hover:bg-white/5 transition-colors ${
                  isSelected ? 'bg-teal-500/10' : ''
                }`}
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${config.color} border`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-white">{config.label}</span>
                    {isSelected && <Check className="w-4 h-4 text-teal-400" />}
                  </div>
                  <p className="text-xs text-zinc-500 mt-0.5">{config.description}</p>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function TeamPage() {
  const [members] = useState<TeamMember[]>(mockMembers);
  const [invites, setInvites] = useState<PendingInvite[]>(mockInvites);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'admin' | 'member' | 'viewer'>('member');
  const [isInviting, setIsInviting] = useState(false);

  const handleInvite = async () => {
    if (!inviteEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    setIsInviting(true);
    try {
      // TODO: API call to send invite
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newInvite: PendingInvite = {
        id: Date.now().toString(),
        email: inviteEmail,
        role: inviteRole,
        sent_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      };
      
      setInvites([...invites, newInvite]);
      setInviteEmail('');
      toast.success(`Invitation sent to ${inviteEmail}`);
    } catch (error) {
      toast.error('Failed to send invitation');
    } finally {
      setIsInviting(false);
    }
  };

  const cancelInvite = (inviteId: string) => {
    setInvites(invites.filter(i => i.id !== inviteId));
    toast.success('Invitation cancelled');
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-medium text-white">Team Management</h1>
          <p className="text-zinc-400 mt-1">Manage your team members and their permissions</p>
        </div>

        {/* Invite Member */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Invite Team Member
            </CardTitle>
            <CardDescription>Send an invitation to add a new team member</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                type="email"
                placeholder="colleague@company.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                className="flex-1"
              />
              <RoleDropdown
                value={inviteRole}
                onChange={setInviteRole}
              />
              <Button variant="gradient" onClick={handleInvite} disabled={isInviting}>
                {isInviting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Send className="w-4 h-4 mr-2" />
                )}
                Send Invite
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Team Members */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Users className="w-5 h-5" />
              Team Members
            </CardTitle>
            <CardDescription>{members.length} member(s)</CardDescription>
          </CardHeader>
          <CardContent className="divide-y divide-white/5">
            {members.map((member) => {
              const role = roleConfig[member.role];
              const RoleIcon = role.icon;
              return (
                <div key={member.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                  <Avatar className="w-10 h-10">
                    <AvatarFallback className="bg-gradient-to-br from-teal-500 to-emerald-500 text-white">
                      {member.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="font-medium text-white">{member.name}</h3>
                    <p className="text-sm text-zinc-400">{member.email}</p>
                  </div>
                  <Badge className={`${role.color} border`}>
                    <RoleIcon className="w-3 h-3 mr-1" />
                    {role.label}
                  </Badge>
                  {member.role !== 'owner' && (
                    <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-red-400">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Pending Invitations */}
        {invites.length > 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Mail className="w-5 h-5" />
                Pending Invitations
              </CardTitle>
              <CardDescription>{invites.length} pending invitation(s)</CardDescription>
            </CardHeader>
            <CardContent className="divide-y divide-white/5">
              {invites.map((invite) => {
                const role = roleConfig[invite.role];
                const RoleIcon = role.icon;
                return (
                  <div key={invite.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                    <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center">
                      <Mail className="w-5 h-5 text-zinc-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-white">{invite.email}</h3>
                      <p className="text-sm text-zinc-500">
                        Expires {new Date(invite.expires_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge className={`${role.color} border`}>
                      <RoleIcon className="w-3 h-3 mr-1" />
                      {role.label}
                    </Badge>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-zinc-400 hover:text-red-400"
                      onClick={() => cancelInvite(invite.id)}
                    >
                      Cancel
                    </Button>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
