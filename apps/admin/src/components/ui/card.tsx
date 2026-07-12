'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  className?: string;
  children: ReactNode;
}

export function Card({ className, children }: CardProps) {
  return (
    <div className={cn(
      'bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 shadow-xl shadow-black/10',
      'transition-all duration-300',
      className
    )}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  className?: string;
  children: ReactNode;
}

export function CardHeader({ className, children }: CardHeaderProps) {
  return (
    <div className={cn('px-6 py-5 border-b border-white/10', className)}>
      {children}
    </div>
  );
}

interface CardTitleProps {
  className?: string;
  children: ReactNode;
}

export function CardTitle({ className, children }: CardTitleProps) {
  return (
    <h3 className={cn('text-lg font-medium text-white tracking-tight', className)}>
      {children}
    </h3>
  );
}

interface CardDescriptionProps {
  className?: string;
  children: ReactNode;
}

export function CardDescription({ className, children }: CardDescriptionProps) {
  return (
    <p className={cn('text-sm text-gray-400 mt-1.5', className)}>
      {children}
    </p>
  );
}

interface CardContentProps {
  className?: string;
  children: ReactNode;
}

export function CardContent({ className, children }: CardContentProps) {
  return <div className={cn('px-6 py-5', className)}>{children}</div>;
}

interface CardFooterProps {
  className?: string;
  children: ReactNode;
}

export function CardFooter({ className, children }: CardFooterProps) {
  return (
    <div className={cn(
      'px-6 py-4 border-t border-white/10 bg-white/[0.02] rounded-b-xl',
      className
    )}>
      {children}
    </div>
  );
}
