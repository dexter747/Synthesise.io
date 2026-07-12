'use client';

import { useState } from 'react';
import { useOrganizationContext } from '@/providers/organization-provider';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Settings,
  Building2,
  Globe,
  Mail,
  Shield,
  Trash2,
  Save,
  AlertTriangle,
  Image as ImageIcon,
  Link as LinkIcon,
  FileText,
  Users,
  Bell,
  Lock,
} from 'lucide-react';

export default function TeamSettingsPage() {
  const { currentOrganization } = useOrganizationContext();
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  
  // Form states
  const [name, setName] = useState(currentOrganization?.name || '');
  const [slug, setSlug] = useState(currentOrganization?.slug || '');
  const [description, setDescription] = useState(currentOrganization?.description || '');
  const [website, setWebsite] = useState(currentOrganization?.website || '');
  const [billingEmail, setBillingEmail] = useState(currentOrganization?.billing_email || '');

  // Settings states
  const [settings, setSettings] = useState({
    allowMemberInvites: true,
    requireApproval: false,
    defaultRole: 'member',
    datasetVisibility: 'team',
    notifyOnNewMember: true,
    notifyOnDatasetShare: true,
  });

  const handleSaveGeneral = async () => {
    try {
      setIsLoading(true);
      // API call would go here
      await new Promise((r) => setTimeout(r, 1000));
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteOrganization = async () => {
    try {
      setIsLoading(true);
      // API call would go here
      toast.success('Organization deleted');
      window.location.href = '/dashboard';
    } catch (error) {
      toast.error('Failed to delete organization');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* General Settings */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-teal-400" />
            General Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Logo Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Organization Logo
            </label>
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center text-white text-2xl font-medium">
                {name.charAt(0).toUpperCase()}
              </div>
              <div>
                <button className="px-4 py-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors text-sm">
                  <ImageIcon className="w-4 h-4 inline mr-2" />
                  Upload Logo
                </button>
                <p className="text-xs text-gray-500 mt-2">
                  Recommended: 200x200px, PNG or JPG
                </p>
              </div>
            </div>
          </div>

          {/* Name & Slug */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Organization Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                URL Slug
              </label>
              <div className="flex">
                <span className="px-3 py-3 bg-white/5 border border-r-0 border-white/10 rounded-l-lg text-gray-500 text-sm">
                  synthesize.io/
                </span>
                <input
                  type="text"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                  className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-r-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
                />
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50 resize-none"
              placeholder="A brief description of your organization..."
            />
          </div>

          {/* Website & Billing Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                <Globe className="w-4 h-4 inline mr-1" />
                Website
              </label>
              <input
                type="url"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                Billing Email
              </label>
              <input
                type="email"
                value={billingEmail}
                onChange={(e) => setBillingEmail(e.target.value)}
                placeholder="billing@example.com"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-teal-500/50"
              />
            </div>
          </div>

          <button
            onClick={handleSaveGeneral}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2.5 bg-teal-500 text-black font-medium rounded-lg hover:bg-teal-400 transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </CardContent>
      </Card>

      {/* Team Settings */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-400" />
            Team Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingToggle
            label="Allow Member Invites"
            description="Let team members invite new people"
            checked={settings.allowMemberInvites}
            onChange={(checked) => setSettings({ ...settings, allowMemberInvites: checked })}
          />

          <SettingToggle
            label="Require Admin Approval"
            description="New members need admin approval to join"
            checked={settings.requireApproval}
            onChange={(checked) => setSettings({ ...settings, requireApproval: checked })}
          />

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Default Role for New Members
            </label>
            <select
              value={settings.defaultRole}
              onChange={(e) => setSettings({ ...settings, defaultRole: e.target.value })}
              className="w-full max-w-xs px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-teal-500/50"
            >
              <option value="viewer">Viewer</option>
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Default Dataset Visibility
            </label>
            <select
              value={settings.datasetVisibility}
              onChange={(e) => setSettings({ ...settings, datasetVisibility: e.target.value })}
              className="w-full max-w-xs px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-teal-500/50"
            >
              <option value="private">Private (Owner only)</option>
              <option value="team">Team (All members)</option>
              <option value="public">Public</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card className="bg-white/[0.03] border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-amber-400" />
            Notification Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingToggle
            label="New Member Notifications"
            description="Get notified when someone joins the team"
            checked={settings.notifyOnNewMember}
            onChange={(checked) => setSettings({ ...settings, notifyOnNewMember: checked })}
          />

          <SettingToggle
            label="Dataset Share Notifications"
            description="Get notified when datasets are shared with the team"
            checked={settings.notifyOnDatasetShare}
            onChange={(checked) => setSettings({ ...settings, notifyOnDatasetShare: checked })}
          />
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="bg-red-500/5 border-red-500/20">
        <CardHeader>
          <CardTitle className="text-red-400 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Danger Zone
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium">Delete Organization</p>
              <p className="text-sm text-gray-400">
                Permanently delete this organization and all its data
              </p>
            </div>
            <button
              onClick={() => setShowDeleteModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/20 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Delete Organization
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <DeleteModal
          organizationName={name}
          onClose={() => setShowDeleteModal(false)}
          onConfirm={handleDeleteOrganization}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}

function SettingToggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-white font-medium">{label}</p>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-12 h-6 rounded-full transition-colors ${
          checked ? 'bg-teal-500' : 'bg-white/10'
        }`}
      >
        <div
          className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
            checked ? 'translate-x-7' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}

function DeleteModal({
  organizationName,
  onClose,
  onConfirm,
  isLoading,
}: {
  organizationName: string;
  onClose: () => void;
  onConfirm: () => void;
  isLoading: boolean;
}) {
  const [confirmation, setConfirmation] = useState('');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-[#0a0a0a] rounded-2xl border border-red-500/20 p-6 shadow-2xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 rounded-xl bg-red-500/10">
            <AlertTriangle className="w-6 h-6 text-red-400" />
          </div>
          <h2 className="text-xl font-medium text-white">Delete Organization</h2>
        </div>

        <p className="text-gray-400 mb-4">
          This action cannot be undone. This will permanently delete the organization,
          all team members will lose access, and all shared datasets will be unshared.
        </p>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Type <span className="text-red-400 font-mono">{organizationName}</span> to confirm
          </label>
          <input
            type="text"
            value={confirmation}
            onChange={(e) => setConfirmation(e.target.value)}
            className="w-full px-4 py-3 bg-white/5 border border-red-500/30 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-red-500/50"
            placeholder="Enter organization name"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading || confirmation !== organizationName}
            className="flex-1 px-4 py-2.5 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Deleting...' : 'Delete Organization'}
          </button>
        </div>
      </div>
    </div>
  );
}
