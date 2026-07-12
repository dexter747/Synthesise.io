'use client';

import { useState } from 'react';
import { AdminLayout } from '@/components/layouts/admin-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { useAdminUsers, useAdminUserAction } from '@/hooks/use-admin-api';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Search,
  Users,
  MoreVertical,
  Ban,
  CheckCircle,
  Trash2,
  Mail,
  Loader2,
  ChevronLeft,
  ChevronRight,
  UserPlus,
  Filter,
  Download,
  RefreshCw,
  Eye,
  Edit,
  Shield,
  TrendingUp,
  Clock,
  AlertTriangle,
} from 'lucide-react';

export default function AdminUsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const { data, isLoading, refetch } = useAdminUsers({
    page,
    per_page: 20,
    search: search || undefined,
    role: roleFilter || undefined,
    status: statusFilter || undefined,
  });

  const userAction = useAdminUserAction();

  const users = data?.items || [];
  const totalPages = Math.ceil((data?.total || 0) / 20);

  const handleAction = async (userId: string, action: 'suspend' | 'unsuspend' | 'verify' | 'delete', name: string) => {
    const actionLabels = {
      suspend: 'suspend',
      unsuspend: 'unsuspend',
      verify: 'verify',
      delete: 'delete',
    };

    if (action === 'delete') {
      if (!confirm(`Are you sure you want to delete user "${name}"? This action cannot be undone.`)) {
        return;
      }
    }

    try {
      await userAction.mutateAsync({ userId, action });
      toast.success(`User ${actionLabels[action]}ed successfully`);
    } catch (error: any) {
      toast.error(error.message || `Failed to ${actionLabels[action]} user`);
    }
  };

  // Calculate stats
  const activeUsers = users.filter(u => !(u as any).is_suspended && u.email_verified).length;
  const pendingUsers = users.filter(u => !u.email_verified).length;
  const suspendedUsers = users.filter(u => (u as any).is_suspended).length;

  return (
    <AdminLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Page Header */}
        <div className="page-header">
          <div>
            <h2 className="page-title">
              <span className="gradient-teal-text">User Management</span>
            </h2>
            <p className="page-subtitle">Manage platform users, roles, and permissions</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export
            </button>
            <button className="btn-primary flex items-center gap-2">
              <UserPlus className="w-4 h-4" />
              Add User
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="stat-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Total Users</p>
                <p className="text-3xl font-medium text-white">{data?.total || 0}</p>
              </div>
              <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/20">
                <Users className="w-6 h-6 text-teal-400" />
              </div>
            </div>
            {data?.total && data.total > 0 && (
              <div className="flex items-center gap-1 mt-3 text-xs text-gray-500">
                <span>{data.total} total users</span>
              </div>
            )}
          </div>
          
          <div className="stat-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Active Users</p>
                <p className="text-3xl font-medium text-white">{activeUsers}</p>
              </div>
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                <CheckCircle className="w-6 h-6 text-emerald-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3 text-xs text-emerald-400">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
              <span>Verified & active</span>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Pending Verification</p>
                <p className="text-3xl font-medium text-white">{pendingUsers}</p>
              </div>
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                <Clock className="w-6 h-6 text-amber-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3 text-xs text-amber-400">
              <AlertTriangle className="w-3 h-3" />
              <span>Needs attention</span>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Suspended</p>
                <p className="text-3xl font-medium text-white">{suspendedUsers}</p>
              </div>
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                <Ban className="w-6 h-6 text-red-400" />
              </div>
            </div>
            {suspendedUsers > 0 && (
              <div className="flex items-center gap-1 mt-3 text-xs text-gray-500">
                <span>{suspendedUsers} suspended account{suspendedUsers !== 1 ? 's' : ''}</span>
              </div>
            )}
          </div>
        </div>

        {/* Filters Card */}
        <Card className="admin-card">
          <CardContent className="py-4">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search users by name or email..."
                    className="input-search w-full"
                    value={search}
                    onChange={(e) => {
                      setSearch(e.target.value);
                      setPage(1);
                    }}
                  />
                </div>
              </div>
              
              {/* Filters */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-400">Role:</span>
                </div>
                <div className="flex gap-1">
                  {[
                    { value: '', label: 'All' },
                    { value: 'user', label: 'Users' },
                    { value: 'admin', label: 'Admins' },
                  ].map((role) => (
                    <button
                      key={role.value}
                      onClick={() => { setRoleFilter(role.value); setPage(1); }}
                      className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                        roleFilter === role.value
                          ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30'
                          : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      {role.label}
                    </button>
                  ))}
                </div>
                
                <div className="w-px h-6 bg-white/10 mx-2" />
                
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-400">Status:</span>
                </div>
                <div className="flex gap-1">
                  {[
                    { value: '', label: 'All' },
                    { value: 'active', label: 'Active' },
                    { value: 'suspended', label: 'Suspended' },
                  ].map((status) => (
                    <button
                      key={status.value}
                      onClick={() => { setStatusFilter(status.value); setPage(1); }}
                      className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                        statusFilter === status.value
                          ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30'
                          : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      {status.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card className="admin-card overflow-hidden">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-10 h-10 animate-spin text-teal-400" />
                  <p className="text-gray-400">Loading users...</p>
                </div>
              </div>
            ) : users.length === 0 ? (
              <div className="text-center py-20">
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
                  <Users className="w-10 h-10 text-gray-600" />
                </div>
                <h3 className="text-xl font-medium text-white mb-2">No users found</h3>
                <p className="text-gray-400 max-w-sm mx-auto">Try adjusting your search or filters to find what you're looking for</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto scrollbar-thin">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="table-header">User</th>
                        <th className="table-header">Role</th>
                        <th className="table-header">Status</th>
                        <th className="table-header">Subscription</th>
                        <th className="table-header">Joined</th>
                        <th className="table-header">Last Active</th>
                        <th className="table-header text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user, index) => (
                        <UserRow
                          key={user.id}
                          user={user}
                          index={index}
                          onAction={(action) => handleAction(user.id, action, user.name)}
                        />
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-6 py-4 border-t border-white/10 bg-white/[0.02]">
                    <p className="text-sm text-gray-400">
                      Showing <span className="font-medium text-white">{(page - 1) * 20 + 1}</span> to{' '}
                      <span className="font-medium text-white">{Math.min(page * 20, data?.total || 0)}</span> of{' '}
                      <span className="font-medium text-white">{data?.total || 0}</span> users
                    </p>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="btn-icon disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      
                      {/* Page numbers */}
                      <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          let pageNum;
                          if (totalPages <= 5) {
                            pageNum = i + 1;
                          } else if (page <= 3) {
                            pageNum = i + 1;
                          } else if (page >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                          } else {
                            pageNum = page - 2 + i;
                          }
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setPage(pageNum)}
                              className={`w-9 h-9 rounded-lg text-sm font-medium transition-all ${
                                page === pageNum
                                  ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30'
                                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        })}
                      </div>
                      
                      <button
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="btn-icon disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}

function UserRow({
  user,
  index,
  onAction,
}: {
  user: any;
  index: number;
  onAction: (action: 'suspend' | 'unsuspend' | 'verify' | 'delete') => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  // Generate avatar gradient based on user id or name
  const gradients = [
    'from-teal-500 to-emerald-500',
    'from-blue-500 to-cyan-500',
    'from-purple-500 to-pink-500',
    'from-amber-500 to-orange-500',
    'from-rose-500 to-red-500',
  ];
  const gradient = gradients[index % gradients.length];

  return (
    <tr 
      className="table-row-interactive animate-fade-in"
      style={{ animationDelay: `${index * 30}ms` }}
    >
      <td className="table-cell">
        <Link href={`/users/${user.id}`} className="flex items-center gap-4 group">
          <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center text-white font-medium shadow-lg group-hover:scale-110 transition-transform`}>
            {user.name?.charAt(0).toUpperCase() || '?'}
          </div>
          <div>
            <p className="font-medium text-white group-hover:text-teal-400 transition-colors">{user.name}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </Link>
      </td>
      <td className="table-cell">
        <span className={`badge ${user.role === 'admin' ? 'badge-purple' : user.role === 'super_admin' ? 'badge-amber' : 'badge-gray'}`}>
          {user.role === 'admin' && <Shield className="w-3 h-3 mr-1" />}
          {user.role}
        </span>
      </td>
      <td className="table-cell">
        {(user as any).is_suspended ? (
          <span className="badge badge-red">Suspended</span>
        ) : user.email_verified ? (
          <span className="badge badge-emerald">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-1.5 animate-pulse" />
            Active
          </span>
        ) : (
          <span className="badge badge-amber">Pending</span>
        )}
      </td>
      <td className="table-cell">
        {user.subscription_tier ? (
          <span className={`badge ${
            user.subscription_tier === 'enterprise' ? 'badge-purple' :
            user.subscription_tier === 'business' ? 'badge-blue' :
            user.subscription_tier === 'professional' ? 'badge-teal' :
            user.subscription_tier === 'starter' ? 'badge-amber' :
            'badge-gray'
          }`}>
            {user.subscription_tier.charAt(0).toUpperCase() + user.subscription_tier.slice(1)}
          </span>
        ) : (
          <span className="badge badge-gray">Free</span>
        )}
      </td>
      <td className="table-cell">
        <span className="text-gray-400">{formatDate(user.created_at)}</span>
      </td>
      <td className="table-cell">
        <span className="text-gray-400">
          {user.last_login_at ? formatRelativeTime(user.last_login_at) : 'Never'}
        </span>
      </td>
      <td className="table-cell text-right">
        <div className="relative inline-flex items-center gap-1">
          <Link
            href={`/users/${user.id}`}
            className="btn-icon"
            title="View Details"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <Link
            href={`/users/${user.id}/edit`}
            className="btn-icon"
            title="Edit User"
          >
            <Edit className="w-4 h-4" />
          </Link>
          <button 
            onClick={() => setMenuOpen(!menuOpen)}
            className="btn-icon"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-full mt-2 w-52 bg-[#111111] rounded-xl shadow-2xl border border-white/10 py-2 z-50 animate-scale-in">
                <div className="px-4 py-2 border-b border-white/10 mb-2">
                  <p className="text-xs text-gray-500">Quick Actions</p>
                </div>
                
                {!user.email_verified && (
                  <button
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-300 hover:bg-white/5 transition-colors"
                    onClick={() => { setMenuOpen(false); onAction('verify'); }}
                  >
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    Verify Email
                  </button>
                )}
                
                <button
                  className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-300 hover:bg-white/5 transition-colors"
                  onClick={() => { setMenuOpen(false); }}
                >
                  <Mail className="w-4 h-4 text-blue-400" />
                  Send Email
                </button>
                
                {(user as any).is_suspended ? (
                  <button
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-300 hover:bg-white/5 transition-colors"
                    onClick={() => { setMenuOpen(false); onAction('unsuspend'); }}
                  >
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    Unsuspend User
                  </button>
                ) : (
                  <button
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-amber-400 hover:bg-white/5 transition-colors"
                    onClick={() => { setMenuOpen(false); onAction('suspend'); }}
                  >
                    <Ban className="w-4 h-4" />
                    Suspend User
                  </button>
                )}
                
                <div className="border-t border-white/10 mt-2 pt-2">
                  <button
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                    onClick={() => { setMenuOpen(false); onAction('delete'); }}
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete User
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </td>
    </tr>
  );
}
