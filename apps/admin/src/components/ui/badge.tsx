'use client';

import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'teal' | 'purple' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Badge({ children, variant = 'default', size = 'md', className }: BadgeProps) {
  const variants = {
    default: 'bg-white/5 text-gray-300 border-white/10',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    error: 'bg-red-500/10 text-red-400 border-red-500/20',
    info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    teal: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    secondary: 'bg-white/5 text-gray-400 border-white/10',
    outline: 'bg-transparent text-gray-400 border-gray-600',
  };

  const sizes = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full border transition-all duration-200',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const variantMap: Record<string, BadgeProps['variant']> = {
    active: 'success',
    verified: 'success',
    suspended: 'error',
    pending: 'warning',
    deleted: 'error',
    healthy: 'success',
    degraded: 'warning',
    down: 'error',
    processing: 'info',
    completed: 'success',
    failed: 'error',
    queued: 'warning',
  };

  return <Badge variant={variantMap[status] || 'default'}>{status}</Badge>;
}

// Status dot component for inline status indicators
export function StatusDot({ 
  status 
}: { 
  status: 'online' | 'offline' | 'busy' | 'away' | 'error' 
}) {
  const colors = {
    online: 'bg-emerald-400',
    offline: 'bg-gray-500',
    busy: 'bg-red-400',
    away: 'bg-amber-400',
    error: 'bg-red-500',
  };

  return (
    <span className={cn(
      'w-2 h-2 rounded-full',
      colors[status],
      status === 'online' && 'animate-pulse'
    )} />
  );
}
