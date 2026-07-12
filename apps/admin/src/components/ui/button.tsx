'use client';

import { ReactNode, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'teal';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading,
      disabled,
      leftIcon,
      rightIcon,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = cn(
      'inline-flex items-center justify-center font-medium',
      'transition-all duration-200',
      'focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-black',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
      'rounded-xl'
    );

    const variants = {
      primary: cn(
        'bg-gradient-to-r from-teal-500 to-emerald-500 text-white',
        'shadow-lg shadow-teal-500/25',
        'hover:shadow-teal-500/40 hover:scale-[1.02]',
        'active:scale-[0.98]'
      ),
      teal: cn(
        'bg-teal-500/10 text-teal-400 border border-teal-500/30',
        'hover:bg-teal-500/20 hover:border-teal-500/50',
        'active:scale-[0.98]'
      ),
      secondary: cn(
        'bg-white/5 text-white border border-white/10',
        'hover:bg-white/10 hover:border-white/20',
        'active:scale-[0.98]'
      ),
      outline: cn(
        'border border-white/10 bg-transparent text-gray-300',
        'hover:bg-white/5 hover:border-white/20 hover:text-white',
        'active:scale-[0.98]'
      ),
      ghost: cn(
        'text-gray-400 bg-transparent',
        'hover:bg-white/10 hover:text-white',
        'active:scale-[0.98]'
      ),
      danger: cn(
        'bg-red-500/10 text-red-400 border border-red-500/30',
        'hover:bg-red-500/20 hover:border-red-500/50',
        'active:scale-[0.98]'
      ),
    };

    const sizes = {
      sm: 'text-xs px-3 py-2 gap-1.5',
      md: 'text-sm px-4 py-2.5 gap-2',
      lg: 'text-base px-6 py-3 gap-2',
      icon: 'p-2.5',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          leftIcon && <span className="flex-shrink-0">{leftIcon}</span>
        )}
        {children}
        {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
