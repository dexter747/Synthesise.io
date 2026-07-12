'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/providers/auth-provider';
import { useUpdateProfile } from '@/hooks/use-api';
import { toast } from 'sonner';
import { getAPI } from '@synthesize/api-client';
import {
  User,
  Shield,
  Monitor,
  Key,
  Smartphone,
  AlertTriangle,
  Eye,
  EyeOff,
  Loader2,
  Check,
} from 'lucide-react';

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
});

const passwordSchema = z
  .object({
    currentPassword: z.string().min(1, 'Current password is required'),
    newPassword: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type ProfileFormData = z.infer<typeof profileSchema>;
type PasswordFormData = z.infer<typeof passwordSchema>;

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

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const updateProfile = useUpdateProfile();
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [sessions] = useState<Session[]>(mockSessions);
  const [showPasswords, setShowPasswords] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [enablingTwoFactor, setEnablingTwoFactor] = useState(false);
  
  // Security password state
  const [secCurrentPassword, setSecCurrentPassword] = useState('');
  const [secNewPassword, setSecNewPassword] = useState('');
  const [secConfirmPassword, setSecConfirmPassword] = useState('');
  const [changingSecPassword, setChangingSecPassword] = useState(false);

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
    },
  });

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  const onProfileSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfile.mutateAsync({
        name: data.name,
        email: data.email,
      });
      await refreshUser();
      toast.success('Profile updated successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to update profile');
    }
  };

  const onPasswordSubmit = async (data: PasswordFormData) => {
    setIsChangingPassword(true);
    try {
      const api = getAPI();
      await api.changePassword(data.currentPassword, data.newPassword);
      resetPassword();
      toast.success('Password changed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleSecurityPasswordChange = async () => {
    if (!secCurrentPassword || !secNewPassword || !secConfirmPassword) {
      toast.error('Please fill in all password fields');
      return;
    }
    
    if (secNewPassword !== secConfirmPassword) {
      toast.error('New passwords do not match');
      return;
    }
    
    if (secNewPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setChangingSecPassword(true);
    try {
      const api = getAPI();
      await api.changePassword(secCurrentPassword, secNewPassword);
      toast.success('Password changed successfully');
      setSecCurrentPassword('');
      setSecNewPassword('');
      setSecConfirmPassword('');
    } catch (error: any) {
      toast.error(error.message || 'Failed to change password');
    } finally {
      setChangingSecPassword(false);
    }
  };

  const handleToggleTwoFactor = async () => {
    setEnablingTwoFactor(true);
    try {
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
      toast.success('Session revoked');
    } catch (error) {
      toast.error('Failed to revoke session');
    }
  };

  const revokeAllSessions = async () => {
    try {
      toast.success('All other sessions have been revoked');
    } catch (error) {
      toast.error('Failed to revoke sessions');
    }
  };

  const userInitials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U';

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-medium text-white">Profile & Settings</h1>
          <p className="text-zinc-400 mt-1">Manage your account, security, and preferences</p>
        </div>

        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="bg-zinc-900/50 border border-white/10">
            <TabsTrigger value="profile" className="data-[state=active]:bg-teal-500/10 data-[state=active]:text-teal-400">
              <User className="w-4 h-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="security" className="data-[state=active]:bg-teal-500/10 data-[state=active]:text-teal-400">
              <Shield className="w-4 h-4 mr-2" />
              Security
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6 mt-6">
            {/* Profile Settings */}
            <Card glass>
              <CardHeader>
                <CardTitle className="text-white">Profile Information</CardTitle>
                <CardDescription>Update your personal information</CardDescription>
              </CardHeader>
              <form onSubmit={handleProfileSubmit(onProfileSubmit)}>
                <CardContent className="space-y-4">
                  {/* Profile Picture */}
                  <div className="flex items-center gap-4">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center text-white text-2xl font-medium">
                      {userInitials}
                    </div>
                    <div>
                      <p className="text-sm text-zinc-400 mb-2">Profile picture is automatically fetched from your Google account</p>
                      <p className="text-xs text-zinc-500">To change it, update your Google account profile picture</p>
                    </div>
                  </div>
                  
                  <Input
                    label="Full Name"
                    error={profileErrors.name?.message}
                    {...registerProfile('name')}
                  />
                  <Input
                    label="Email"
                    type="email"
                    error={profileErrors.email?.message}
                    {...registerProfile('email')}
                  />
                </CardContent>
                <CardFooter>
                  <Button type="submit" variant="gradient" loading={updateProfile.isPending} disabled={!isDirty}>
                    Save Changes
                  </Button>
                </CardFooter>
              </form>
            </Card>

            {/* Password Settings */}
            <Card glass>
              <CardHeader>
                <CardTitle className="text-white">Change Password</CardTitle>
                <CardDescription>Update your password to keep your account secure</CardDescription>
              </CardHeader>
              <form onSubmit={handlePasswordSubmit(onPasswordSubmit)}>
                <CardContent className="space-y-4">
                  <Input
                    label="Current Password"
                    type="password"
                    error={passwordErrors.currentPassword?.message}
                    {...registerPassword('currentPassword')}
                  />
                  <Input
                    label="New Password"
                    type="password"
                    helperText="Must be at least 8 characters"
                    error={passwordErrors.newPassword?.message}
                    {...registerPassword('newPassword')}
                  />
                  <Input
                    label="Confirm New Password"
                    type="password"
                    error={passwordErrors.confirmPassword?.message}
                    {...registerPassword('confirmPassword')}
                  />
                </CardContent>
                <CardFooter>
                  <Button type="submit" variant="gradient" loading={isChangingPassword}>
                    Change Password
                  </Button>
                </CardFooter>
              </form>
            </Card>

            {/* Danger Zone */}
            <Card className="border-red-500/30 bg-red-500/5">
              <CardHeader>
                <CardTitle className="text-red-400">Danger Zone</CardTitle>
                <CardDescription className="text-red-400/70">Irreversible and destructive actions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between p-4 rounded-lg border border-red-500/20 bg-red-500/10">
                  <div>
                    <h4 className="font-medium text-white">Delete Account</h4>
                    <p className="text-sm text-zinc-400">
                      Permanently delete your account and all data
                    </p>
                  </div>
                  <Button
                    variant="destructive"
                    onClick={() => {
                      if (
                        confirm(
                          'Are you sure you want to delete your account? This action cannot be undone.'
                        )
                      ) {
                        toast.info('Account deletion not implemented in demo');
                      }
                    }}
                  >
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6 mt-6">
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
                      value={secCurrentPassword}
                      onChange={(e) => setSecCurrentPassword(e.target.value)}
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-300">New Password</label>
                    <Input
                      type={showPasswords ? 'text' : 'password'}
                      placeholder="Enter new password"
                      value={secNewPassword}
                      onChange={(e) => setSecNewPassword(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-300">Confirm New Password</label>
                    <Input
                      type={showPasswords ? 'text' : 'password'}
                      placeholder="Confirm new password"
                      value={secConfirmPassword}
                      onChange={(e) => setSecConfirmPassword(e.target.value)}
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
                  <Button variant="gradient" onClick={handleSecurityPasswordChange} disabled={changingSecPassword}>
                    {changingSecPassword ? (
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
                  <Button 
                    variant="outline" 
                    className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                    onClick={() => {
                      if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                        toast.info('Account deletion not implemented in demo');
                      }
                    }}
                  >
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
