'use client';

import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import { useOrganizations } from '@/hooks/use-api';
import type { Organization, OrganizationRole } from '@synthesize/types';

interface OrganizationMembership extends Organization {
  role: OrganizationRole;
}

interface OrganizationContextType {
  // Current active organization
  currentOrganization: OrganizationMembership | null;
  // All organizations the user belongs to
  organizations: OrganizationMembership[];
  // Is data loading
  isLoading: boolean;
  // Switch to a different organization
  switchOrganization: (orgId: string) => void;
  // Clear organization selection (go to personal workspace)
  clearOrganization: () => void;
  // Check if user has a specific role in current org
  hasRole: (role: OrganizationRole | OrganizationRole[]) => boolean;
  // Check if user is at least admin
  isAdmin: boolean;
  // Check if user is owner
  isOwner: boolean;
  // Refresh organizations list
  refresh: () => void;
}

const OrganizationContext = createContext<OrganizationContextType | null>(null);

const STORAGE_KEY = 'synthesize_active_org';

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const [currentOrgId, setCurrentOrgId] = useState<string | null>(null);
  const { data: organizations = [], isLoading, refetch } = useOrganizations();

  // Load saved organization from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedOrgId = localStorage.getItem(STORAGE_KEY);
      if (savedOrgId) {
        setCurrentOrgId(savedOrgId);
      }
    }
  }, []);

  // Validate current org exists in user's orgs
  useEffect(() => {
    if (!isLoading && currentOrgId) {
      const orgExists = organizations.some((org: any) => org.id === currentOrgId);
      if (!orgExists) {
        // User no longer has access to this org
        setCurrentOrgId(null);
        if (typeof window !== 'undefined') {
          localStorage.removeItem(STORAGE_KEY);
        }
      }
    }
  }, [organizations, currentOrgId, isLoading]);

  const currentOrganization = currentOrgId
    ? (organizations.find((org: any) => org.id === currentOrgId) as OrganizationMembership | undefined) || null
    : null;

  const switchOrganization = useCallback((orgId: string) => {
    setCurrentOrgId(orgId);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, orgId);
    }
  }, []);

  const clearOrganization = useCallback(() => {
    setCurrentOrgId(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const hasRole = useCallback(
    (role: OrganizationRole | OrganizationRole[]): boolean => {
      if (!currentOrganization) return false;
      const roles = Array.isArray(role) ? role : [role];
      return roles.includes(currentOrganization.role);
    },
    [currentOrganization]
  );

  const isAdmin = currentOrganization
    ? currentOrganization.role === 'admin' || currentOrganization.role === 'owner'
    : false;

  const isOwner = currentOrganization?.role === 'owner';

  const refresh = useCallback(() => {
    refetch();
  }, [refetch]);

  return (
    <OrganizationContext.Provider
      value={{
        currentOrganization,
        organizations: organizations as OrganizationMembership[],
        isLoading,
        switchOrganization,
        clearOrganization,
        hasRole,
        isAdmin,
        isOwner,
        refresh,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganizationContext() {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganizationContext must be used within an OrganizationProvider');
  }
  return context;
}

// Safe hook that doesn't throw if outside provider
export function useOrganizationContextSafe() {
  return useContext(OrganizationContext);
}
