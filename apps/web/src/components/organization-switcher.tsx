'use client';

import { useState, useRef, useEffect } from 'react';
import { useOrganizationContext } from '@/providers/organization-provider';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Building2,
  ChevronDown,
  Check,
  Plus,
  User,
  Crown,
  Shield,
  Users,
  Eye,
} from 'lucide-react';
import Link from 'next/link';

const roleIcons = {
  owner: Crown,
  admin: Shield,
  member: Users,
  viewer: Eye,
};

const roleColors = {
  owner: 'text-amber-400',
  admin: 'text-emerald-400',
  member: 'text-blue-400',
  viewer: 'text-zinc-400',
};

export function OrganizationSwitcher() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const {
    currentOrganization,
    organizations,
    switchOrganization,
    clearOrganization,
    isLoading,
  } = useOrganizationContext();

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close on escape
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsOpen(false);
    }
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const displayName = currentOrganization?.name || 'Personal Workspace';
  const initial = currentOrganization 
    ? currentOrganization.name.charAt(0).toUpperCase()
    : null;

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="ghost"
        className="flex items-center gap-2 px-3 py-2 h-auto hover:bg-white/5"
        onClick={() => setIsOpen(!isOpen)}
      >
        {currentOrganization ? (
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
            <span className="text-xs font-medium text-white">{initial}</span>
          </div>
        ) : (
          <div className="w-7 h-7 rounded-lg bg-zinc-800 flex items-center justify-center">
            <User className="w-4 h-4 text-zinc-400" />
          </div>
        )}
        <span className="text-sm font-medium text-white max-w-[120px] truncate">
          {displayName}
        </span>
        <ChevronDown className={`w-4 h-4 text-zinc-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 bg-zinc-900 border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="p-2 border-b border-white/10">
            <p className="text-xs font-medium text-zinc-500 px-2 py-1">Switch Workspace</p>
          </div>

          <div className="max-h-64 overflow-y-auto p-1">
            {/* Personal Workspace Option */}
            <button
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                !currentOrganization
                  ? 'bg-teal-500/10 border border-teal-500/30'
                  : 'hover:bg-white/5'
              }`}
              onClick={() => {
                clearOrganization();
                setIsOpen(false);
              }}
            >
              <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-zinc-400" />
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-medium text-white">Personal Workspace</p>
                <p className="text-xs text-zinc-500">Your individual account</p>
              </div>
              {!currentOrganization && (
                <Check className="w-4 h-4 text-teal-400 flex-shrink-0" />
              )}
            </button>

            {/* Organizations */}
            {organizations.length > 0 && (
              <>
                <div className="my-1 border-t border-white/5" />
                {organizations.map((org: any) => {
                  const RoleIcon = roleIcons[org.role as keyof typeof roleIcons] || Users;
                  const roleColor = roleColors[org.role as keyof typeof roleColors] || 'text-zinc-400';
                  const isActive = currentOrganization?.id === org.id;

                  return (
                    <button
                      key={org.id}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                        isActive
                          ? 'bg-teal-500/10 border border-teal-500/30'
                          : 'hover:bg-white/5'
                      }`}
                      onClick={() => {
                        switchOrganization(org.id);
                        setIsOpen(false);
                      }}
                    >
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-medium text-white">
                          {org.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0 text-left">
                        <p className="text-sm font-medium text-white truncate">{org.name}</p>
                        <div className="flex items-center gap-1.5 text-xs">
                          <RoleIcon className={`w-3 h-3 ${roleColor}`} />
                          <span className={roleColor}>
                            {org.role.charAt(0).toUpperCase() + org.role.slice(1)}
                          </span>
                          <span className="text-zinc-600">•</span>
                          <span className="text-zinc-500">{org.member_count || 1} members</span>
                        </div>
                      </div>
                      {isActive && (
                        <Check className="w-4 h-4 text-teal-400 flex-shrink-0" />
                      )}
                    </button>
                  );
                })}
              </>
            )}
          </div>

          <div className="p-2 border-t border-white/10">
            <Link href="/organizations" onClick={() => setIsOpen(false)}>
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 transition-colors">
                <Plus className="w-4 h-4" />
                <span className="text-sm">Create or Join Organization</span>
              </button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
