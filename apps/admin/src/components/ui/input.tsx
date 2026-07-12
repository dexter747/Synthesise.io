'use client';

import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="space-y-2">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-300">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none">
              {leftIcon}
            </div>
          )}
          <input
            type={type}
            id={inputId}
            className={cn(
              'block w-full rounded-xl border bg-white/5 text-white transition-all duration-200',
              'placeholder:text-gray-500',
              'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-offset-black',
              error
                ? 'border-red-500/50 focus:border-red-500 focus:ring-red-500/20'
                : 'border-white/10 focus:border-teal-500/50 focus:ring-teal-500/20',
              'disabled:bg-white/[0.02] disabled:text-gray-500 disabled:cursor-not-allowed',
              'hover:border-white/20',
              leftIcon ? 'pl-11' : 'pl-4',
              rightIcon ? 'pr-11' : 'pr-4',
              'py-3 text-sm',
              className
            )}
            ref={ref}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="text-sm text-red-400 flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-red-400" />
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
