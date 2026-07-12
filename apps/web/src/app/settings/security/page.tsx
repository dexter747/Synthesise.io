'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Shield,
  Key,
  Smartphone,
  Lock,
  AlertTriangle,
  Eye,
  EyeOff,
  Loader2,
  Check,
  Monitor,
  Globe,
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/providers/auth-provider';

interface Session {
  id: string;
  device: string;
  browser: string;
  location: string;
  ip: string;
  last_active: string;
  is_current: boolean;
}

const mockSessions: Session[] = [
  {
    id: '1',
    device: 'MacBook Pro',
    browser: 'Safari 18',
    location: 'Mumbai, India',
    ip: '103.xxx.xxx.xxx',
    last_active: new Date().toISOString(),
    is_current: true,
  },
];

export default function SecurityPage() {
  const { user } = useAuth();
  const [sessions] = useState<Session[]>(mockSessions);
  
  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  
  // 2FA state
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [enablingTwoFactor, setEnablingTwoFactor] = useState(false);

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error('Please fill in all password fields');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }
    
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setChangingPassword(true);
    try {
      // TODO: API call to change password
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error) {
      toast.error('Failed to change password');
    } finally {
      setChangingPassword(false);
    }
  };

  const handleToggleTwoFactor = async () => {
    setEnablingTwoFactor(true);
    try {
      // TODO: API call to enable/disable 2FA
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTwoFactorEnabled(!twoFactorEnabled);
      toast.success(twoFactorEnabled ? 'Two-factor authentication disabled' : 'Two-factor authentication enabled');
    } catch (error) {
      toast.error('Failed to update two-factor authentication');
    } finally {
      setEnablingTwoFactor(false);
    }
  };

  const revokeSession = async (sessionId: string) => {
    try {
      // TODO: API call to revoke session
      toast.success('Session revoked');
    } catch (error) {
      toast.error('Failed to revoke session');
    }
  };

  const revokeAllSessions = async () => {
    try {
      // TODO: API call to revoke all sessions
      toast.success('All other sessions have been revoked');
    } catch (error) {
      toast.error('Failed to revoke sessions');
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-medium text-white">Security Settings</h1>
          <p className="text-zinc-400 mt-1">Manage your account security and active sessions</p>
        </div>

        {/* Change Password */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Key className="w-5 h-5" />
              Change Password
            </CardTitle>
            <CardDescription>Update your password to keep your account secure</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Current Password</label>
              <div className="relative">
                <Input
                  type={showPasswords ? 'text' : 'password'}
                  placeholder="Enter current password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-zinc-300">New Password</label>
                <Input
                  type={showPasswords ? 'text' : 'password'}
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-zinc-300">Confirm New Password</label>
                <Input
                  type={showPasswords ? 'text' : 'password'}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setShowPasswords(!showPasswords)}
                className="text-zinc-400"
              >
                {showPasswords ? (
                  <><EyeOff className="w-4 h-4 mr-2" /> Hide passwords</>
                ) : (
                  <><Eye className="w-4 h-4 mr-2" /> Show passwords</>
                )}
              </Button>
              <div className="flex-1" />
              <Button variant="gradient" onClick={handleChangePassword} disabled={changingPassword}>
                {changingPassword ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Check className="w-4 h-4 mr-2" />
                )}
                Update Password
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Two-Factor Authentication */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Smartphone className="w-5 h-5" />
              Two-Factor Authentication
            </CardTitle>
            <CardDescription>Add an extra layer of security to your account</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  twoFactorEnabled 
                    ? 'bg-teal-500/20 text-teal-400' 
                    : 'bg-zinc-800 text-zinc-400'
                }`}>
                  <Shield className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-medium text-white">
                    {twoFactorEnabled ? 'Two-factor authentication is enabled' : 'Two-factor authentication is disabled'}
                  </h3>
                  <p className="text-sm text-zinc-400">
                    {twoFactorEnabled 
                      ? 'Your account is protected with an authenticator app' 
                      : 'Enable 2FA to add an extra layer of security'}
                  </p>
                </div>
              </div>
              <Button 
                variant={twoFactorEnabled ? 'outline' : 'gradient'}
                onClick={handleToggleTwoFactor}
                disabled={enablingTwoFactor}
              >
                {enablingTwoFactor ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                {twoFactorEnabled ? 'Disable' : 'Enable'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Active Sessions */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                <Monitor className="w-5 h-5" />
                Active Sessions
              </CardTitle>
              <CardDescription>Manage your active sessions across devices</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={revokeAllSessions}>
              Revoke All Others
            </Button>
          </CardHeader>
          <CardContent className="divide-y divide-white/5">
            {sessions.map((session) => (
              <div key={session.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                  <Monitor className="w-5 h-5 text-zinc-400" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium text-white">{session.device}</h3>
                    {session.is_current && (
                      <Badge className="bg-teal-500/20 text-teal-400 border-teal-500/30">
                        Current
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-zinc-400">
                    {session.browser} • {session.location}
                  </p>
                </div>
                <div className="text-right text-sm">
                  <p className="text-zinc-400">{session.ip}</p>
                  <p className="text-zinc-500">
                    {session.is_current ? 'Active now' : `Last active ${new Date(session.last_active).toLocaleDateString()}`}
                  </p>
                </div>
                {!session.is_current && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-zinc-400 hover:text-red-400"
                    onClick={() => revokeSession(session.id)}
                  >
                    Revoke
                  </Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="bg-red-500/5 border-red-500/20">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Danger Zone
            </CardTitle>
            <CardDescription className="text-red-400/70">
              Irreversible and destructive actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-white">Delete Account</h3>
                <p className="text-sm text-zinc-400">
                  Permanently delete your account and all associated data
                </p>
              </div>
              <Button variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10">
                Delete Account
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
