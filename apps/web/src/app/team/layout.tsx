'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { useOrganizationContext } from '@/providers/organization-provider';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import {
  Users,
  Settings,
  CreditCard,
  Activity,
  Shield,
  Building2,
} from 'lucide-react';

const teamNavItems = [
  { href: '/team', label: 'Members', icon: Users, exact: true },
  { href: '/team/settings', label: 'Settings', icon: Settings },
  { href: '/team/billing', label: 'Billing', icon: CreditCard },
  { href: '/team/activity', label: 'Activity', icon: Activity },
];

export default function TeamLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const { currentOrganization, isLoading: orgLoading } = useOrganizationContext();

  // Redirect to dashboard if not in an organization
  useEffect(() => {
    if (!authLoading && !orgLoading && !currentOrganization) {
      router.push('/dashboard');
    }
  }, [authLoading, orgLoading, currentOrganization, router]);

  if (authLoading || orgLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="w-8 h-8 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  if (!currentOrganization) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-2">
            <div className="p-3 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30">
              <Building2 className="w-6 h-6 text-teal-400" />
            </div>
            <div>
              <h1 className="text-2xl font-medium text-white">
                {currentOrganization.name}
              </h1>
              <p className="text-gray-400 text-sm">
                Manage your team, billing, and organization settings
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex gap-1 p-1 bg-white/5 rounded-xl border border-white/10">
            {teamNavItems.map((item) => {
              const isActive = item.exact
                ? pathname === item.href
                : pathname.startsWith(item.href);
              const Icon = item.icon;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        {children}
      </div>
    </DashboardLayout>
  );
}
