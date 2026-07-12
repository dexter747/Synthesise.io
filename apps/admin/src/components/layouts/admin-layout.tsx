'use client';

import { ReactNode, useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAdminAuth } from '@/providers/auth-provider';
import {
  LayoutDashboard,
  Users,
  CreditCard,
  BarChart3,
  Flag,
  FileText,
  Activity,
  LogOut,
  Menu,
  X,
  Shield,
  Bell,
  Search,
  ChevronRight,
  Settings,
  HelpCircle,
  Zap,
  Database,
  Server,
  MessageSquare,
  Gauge,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  badgeColor?: 'teal' | 'amber' | 'red';
}

const mainNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'Users', href: '/users', icon: Users },
  { label: 'Subscriptions', href: '/subscriptions', icon: CreditCard },
  { label: 'Jobs Queue', href: '/jobs', icon: Zap, badge: 'Live', badgeColor: 'teal' },
  { label: 'Customer Queries', href: '/queries', icon: MessageSquare },
  { label: 'Analytics', href: '/analytics', icon: BarChart3 },
];

const systemNavItems: NavItem[] = [
  { label: 'Feature Flags', href: '/feature-flags', icon: Flag },
  { label: 'Audit Logs', href: '/audit-logs', icon: FileText },
  { label: 'Server Logs', href: '/logs', icon: Server },
  { label: 'Monitoring', href: '/monitoring', icon: Gauge, badge: 'New', badgeColor: 'teal' },
  { label: 'System Health', href: '/health', icon: Activity },
  { label: 'Database', href: '/database', icon: Database },
];

function NavBadge({ text, color = 'teal' }: { text: string; color?: 'teal' | 'amber' | 'red' }) {
  const colors = {
    teal: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
    amber: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    red: 'bg-red-500/20 text-red-400 border-red-500/30',
  };
  
  return (
    <span className={cn(
      'ml-auto px-2 py-0.5 text-[10px] font-medium rounded-full border',
      colors[color]
    )}>
      {text}
    </span>
  );
}

function NavSection({ title, items, pathname }: { title: string; items: NavItem[]; pathname: string }) {
  return (
    <div className="mb-6">
      <p className="px-4 mb-3 text-[10px] font-medium uppercase tracking-widest text-gray-500">{title}</p>
      <div className="space-y-1">
        {items.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 group relative',
                isActive
                  ? 'bg-gradient-to-r from-teal-500/20 to-emerald-500/20 text-white border border-teal-500/30 shadow-lg shadow-teal-500/10'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              )}
            >
              {/* Active indicator bar */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-teal-400 to-emerald-400 rounded-r-full" />
              )}
              
              <div className={cn(
                'p-2 rounded-lg transition-all duration-200',
                isActive 
                  ? 'bg-teal-500/20 text-teal-400' 
                  : 'bg-white/5 text-gray-500 group-hover:bg-white/10 group-hover:text-gray-300'
              )}>
                <item.icon className="w-4 h-4" />
              </div>
              
              <span className="flex-1">{item.label}</span>
              
              {item.badge && <NavBadge text={item.badge} color={item.badgeColor} />}
              
              {isActive && (
                <div className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function QuickStats() {
  return (
    <div className="mx-4 mb-6 p-4 rounded-xl bg-gradient-to-br from-teal-500/10 to-emerald-500/10 border border-teal-500/20">
      <div className="flex items-center gap-2 mb-3">
        <Server className="w-4 h-4 text-teal-400" />
        <span className="text-xs font-medium text-white">Quick Stats</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center">
          <p className="text-lg font-medium text-white">2.4k</p>
          <p className="text-[10px] text-gray-400">Active Users</p>
        </div>
        <div className="text-center">
          <p className="text-lg font-medium text-emerald-400">99.9%</p>
          <p className="text-[10px] text-gray-400">Uptime</p>
        </div>
      </div>
    </div>
  );
}

export function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAdminAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      }));
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-black">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden animate-fade-in"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-72 bg-[#0a0a0a] border-r border-white/10 transform transition-transform duration-300 lg:translate-x-0 flex flex-col',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-5 border-b border-white/10 bg-black/50">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-10 h-10 rounded-lg bg-black flex items-center justify-center group-hover:scale-105 transition-all duration-300 p-1.5">
                <Image
                  src="/logo.svg"
                  alt="Synthesize.io"
                  width={32}
                  height={32}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-[#0a0a0a] animate-pulse" />
            </div>
            <div>
              <span className="font-semibold text-white text-base tracking-tight">Synthesize.io</span>
              <span className="block text-[9px] font-medium text-teal-400 uppercase tracking-wider">Admin</span>
            </div>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="ml-auto lg:hidden p-2 hover:bg-white/10 rounded-lg text-gray-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-6 overflow-y-auto scrollbar-thin">
          <NavSection title="Main" items={mainNavItems} pathname={pathname} />
          <NavSection title="System" items={systemNavItems} pathname={pathname} />
          <QuickStats />
        </nav>

        {/* User info at bottom */}
        <div className="p-4 border-t border-white/10 bg-black/30">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/10 hover:bg-white/[0.05] transition-all duration-200">
            <div className="relative">
              <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center text-white font-medium shadow-lg shadow-teal-500/20">
                {user?.name?.charAt(0).toUpperCase() || 'A'}
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-[#0a0a0a]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'Admin'}</p>
              <p className="text-[11px] text-gray-500 truncate">{user?.email || 'admin@synthesise.io'}</p>
            </div>
            <button
              onClick={logout}
              className="p-2.5 hover:bg-red-500/10 rounded-xl text-gray-400 hover:text-red-400 transition-all duration-200 group"
              title="Sign out"
            >
              <LogOut className="w-4 h-4 group-hover:scale-110 transition-transform" />
            </button>
          </div>
          
          {/* Help link */}
          <Link
            href="/settings"
            className="flex items-center gap-2 mt-3 px-3 py-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Settings & Help</span>
            <ChevronRight className="w-3 h-3 ml-auto" />
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Mobile menu button - floating */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-4 left-4 z-30 p-2.5 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-lg text-gray-400 hover:text-white hover:border-teal-500/30 transition-all"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Page content with enhanced background */}
        <main className="min-h-screen p-6 lg:p-8 relative">
          {/* Background effects */}
          <div className="fixed inset-0 pointer-events-none overflow-hidden">
            <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-teal-500/5 rounded-full blur-[120px]" />
            <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[100px]" />
            <div className="absolute top-1/2 right-0 w-[400px] h-[400px] bg-cyan-500/3 rounded-full blur-[80px]" />
          </div>
          
          {/* Grid overlay effect */}
          <div 
            className="fixed inset-0 pointer-events-none opacity-[0.02]"
            style={{
              backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
              backgroundSize: '60px 60px'
            }}
          />
          
          <div className="relative z-10 animate-fade-in">
            {children}
          </div>
        </main>
        
        {/* Footer */}
        <footer className="border-t border-white/5 py-4 px-6 lg:px-8">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>© 2024 Synthesize.io — Admin Portal v2.0</span>
            <div className="flex items-center gap-4">
              <Link href="/docs" className="hover:text-gray-400 transition-colors">Documentation</Link>
              <Link href="/support" className="hover:text-gray-400 transition-colors">Support</Link>
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                All systems operational
              </span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
