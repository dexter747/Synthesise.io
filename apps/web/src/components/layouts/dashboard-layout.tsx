'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { PricingGate } from '@/components/pricing-gate';
import {
  LayoutDashboard,
  Database,
  Play,
  Settings,
  Users,
  CreditCard,
  Key,
  Webhook,
  LogOut,
  ChevronDown,
  Building2,
  Menu,
  X,
  Shield,
  BarChart3,
  HelpCircle,
  FileText,
  ChevronLeft,
  Crown,
  MessageSquare,
} from 'lucide-react';
import { useState } from 'react';
import { OrganizationSwitcher } from '@/components/organization-switcher';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { label: 'Chat History', href: '/chat-history', icon: MessageSquare },
      { label: 'Generation Jobs', href: '/jobs', icon: Play },
      { label: 'Datasets', href: '/datasets', icon: Database },
      { label: 'Analytics', href: '/analytics', icon: BarChart3 },
    ],
  },
  {
    title: 'Organization',
    items: [
      { label: 'Team', href: '/settings/team', icon: Users },
      { label: 'Organizations', href: '/organizations', icon: Building2 },
    ],
  },
  {
    title: 'Developer',
    items: [
      { label: 'API Keys', href: '/settings/api-keys', icon: Key },
      { label: 'Webhooks', href: '/settings/webhooks', icon: Webhook },
    ],
  },
];

const bottomNavItems: NavItem[] = [
  { label: 'Documentation', href: '/docs', icon: FileText },
  { label: 'Help & Support', href: '/support', icon: HelpCircle },
];

export function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const userInitials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U';

  // Role-based navigation filtering
  const getFilteredNavSections = () => {
    const tier = user?.subscription_tier || 'beginner';
    
    return navSections.map(section => {
      // Filter items based on subscription tier
      const filteredItems = section.items.filter(item => {
        // Team features only for Business/Enterprise
        if (item.href.includes('/team') || item.href.includes('/organizations')) {
          return tier === 'business' || tier === 'enterprise';
        }
        
        // Analytics only for Professional and above
        if (item.href.includes('/analytics')) {
          return tier === 'professional' || tier === 'business' || tier === 'enterprise';
        }
        
        // API Keys and Webhooks for Professional and above
        if (item.href.includes('/api-keys') || item.href.includes('/webhooks')) {
          return tier === 'professional' || tier === 'business' || tier === 'enterprise';
        }
        
        return true;
      });

      return {
        ...section,
        items: filteredItems
      };
    }).filter(section => section.items.length > 0); // Remove empty sections
  };

  const filteredNavSections = getFilteredNavSections();

  return (
    <PricingGate>
      <div className="min-h-screen bg-black">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 bg-zinc-950 border-r border-white/5 transform transition-all duration-200 lg:translate-x-0 flex flex-col',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-3 border-b border-white/5 relative">
          <Link href="/dashboard" className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden">
              <Image
                src="/logo.svg"
                alt="Synthesize.io Logo"
                width={32}
                height={32}
                className="object-contain"
              />
            </div>
            {!sidebarCollapsed && <span className="font-medium text-white">Synthesize</span>}
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="ml-auto lg:hidden p-2 hover:bg-white/5 rounded-lg text-zinc-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Organization Switcher */}
        {!sidebarCollapsed && (
          <div className="px-2 py-3 border-b border-white/5">
            <OrganizationSwitcher />
          </div>
        )}

        {/* Collapse Toggle - Outside on right */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className={cn(
            'hidden lg:flex absolute -right-3 top-20 z-50 w-6 h-6 items-center justify-center bg-zinc-900 border border-white/10 rounded-full text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors',
            sidebarCollapsed && 'rotate-180'
          )}
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        {/* Navigation */}
        <ScrollArea className="flex-1 px-3 py-4">
          <div className="space-y-6">
            {filteredNavSections.map((section) => (
              <div key={section.title}>
                {!sidebarCollapsed && (
                  <p className="px-3 mb-2 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    {section.title}
                  </p>
                )}
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                          isActive
                            ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                            : 'text-zinc-400 hover:bg-white/5 hover:text-white',
                          sidebarCollapsed && 'justify-center'
                        )}
                        title={sidebarCollapsed ? item.label : undefined}
                      >
                        <item.icon className={cn('w-5 h-5 flex-shrink-0', isActive && 'text-teal-400')} />
                        {!sidebarCollapsed && item.label}
                        {!sidebarCollapsed && item.badge && (
                          <span className="ml-auto px-2 py-0.5 text-xs font-medium bg-teal-500/20 text-teal-400 rounded-full">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Bottom section */}
        <div className="border-t border-white/5 p-3 space-y-1">
          {bottomNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400 hover:bg-white/5 hover:text-white transition-colors',
                sidebarCollapsed && 'justify-center'
              )}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!sidebarCollapsed && item.label}
            </Link>
          ))}

          {/* Upgrade Plan Button (for beginner users) */}
          {user?.subscription_tier === 'free' && (
            <Link
              href="/pricing"
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium bg-gradient-to-r from-teal-500/10 to-emerald-500/10 text-teal-400 hover:from-teal-500/20 hover:to-emerald-500/20 border border-teal-500/20 transition-all',
                sidebarCollapsed && 'justify-center'
              )}
              title={sidebarCollapsed ? 'Upgrade Plan' : undefined}
            >
              <Crown className="w-5 h-5 flex-shrink-0" />
              {!sidebarCollapsed && <span>Upgrade Plan</span>}
            </Link>
          )}
        </div>

        {/* User info at bottom */}
        <div className="p-3 border-t border-white/5">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className={cn(
                'w-full flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors',
                sidebarCollapsed && 'justify-center'
              )}>
                <Avatar className="w-9 h-9 bg-gradient-to-br from-teal-400 to-emerald-500 flex-shrink-0">
                  <AvatarFallback className="bg-transparent text-white text-sm font-medium">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
                {!sidebarCollapsed && (
                  <>
                    <div className="flex-1 min-w-0 text-left">
                      <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
                      <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
                    </div>
                    <ChevronDown className="w-4 h-4 text-zinc-500 flex-shrink-0" />
                  </>
                )}
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-zinc-900 border-white/10">
              <DropdownMenuLabel className="text-zinc-400">My Account</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem asChild className="text-zinc-300 focus:bg-white/5 focus:text-white">
                <Link href="/settings">
                  <Settings className="w-4 h-4 mr-2" />
                  Profile & Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="text-zinc-300 focus:bg-white/5 focus:text-white">
                <Link href="/settings/billing">
                  <CreditCard className="w-4 h-4 mr-2" />
                  Billing
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem 
                onClick={logout}
                className="text-red-400 focus:bg-red-500/10 focus:text-red-400"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>

      {/* Main content */}
      <div className={cn('transition-all duration-200', sidebarCollapsed ? 'lg:pl-16' : 'lg:pl-64')}>
        {/* Mobile menu button */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-4 left-4 z-20 p-2 bg-zinc-900 border border-white/10 hover:bg-white/5 rounded-lg text-zinc-400"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Page content */}
        <main className="p-4 lg:p-6">{children}</main>
      </div>
      </div>
    </PricingGate>
  );
}
