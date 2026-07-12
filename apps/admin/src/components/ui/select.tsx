'use client';

import { forwardRef, SelectHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  icon?: React.ReactNode;
  error?: boolean;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, icon, error, ...props }, ref) => {
    return (
      <div className="relative">
        <select
          ref={ref}
          className={cn(
            'w-full appearance-none px-4 py-2.5 pr-10 rounded-xl',
            'bg-white/5 border border-white/10 text-white text-sm',
            'focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'transition-all duration-200',
            error && 'border-red-500/50 focus:ring-red-500/50',
            className
          )}
          {...props}
        >
          {children}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none flex items-center gap-1">
          {icon}
          <ChevronDown className="w-4 h-4 text-gray-400" />
        </div>
      </div>
    );
  }
);
Select.displayName = 'Select';

export interface SelectOptionProps {
  value: string;
  children: React.ReactNode;
  disabled?: boolean;
}

function SelectOption({ value, children, disabled }: SelectOptionProps) {
  return (
    <option value={value} disabled={disabled} className="bg-gray-900 text-white">
      {children}
    </option>
  );
}

export { Select, SelectOption };
