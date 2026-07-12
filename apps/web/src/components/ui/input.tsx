'use client';

import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-zinc-300">
            {label}
          </label>
        )}
        <input
          type={type}
          id={inputId}
          className={cn(
            'block w-full rounded border px-3 py-2 text-sm transition-colors',
            'bg-white/5 border-white/10 text-white placeholder:text-zinc-500',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            error
              ? 'border-red-500/50 focus:border-red-500 focus:ring-red-500/20'
              : 'focus:border-teal-500/50 focus:ring-teal-500/20',
            'disabled:bg-white/5 disabled:text-zinc-500 disabled:cursor-not-allowed',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="text-sm text-red-400">{error}</p>}
        {helperText && !error && <p className="text-sm text-zinc-400">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
