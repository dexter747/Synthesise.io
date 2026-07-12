'use client';

import { createContext, useContext, useCallback, useEffect, useState, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { SynthesizeAPI, initAPI, getAPI } from '@synthesize/api-client';
import type { User, AuthTokens, LoginRequest } from '@synthesize/types';

interface AdminAuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AdminAuthContext = createContext<AdminAuthContextType | null>(null);

const PUBLIC_PATHS = ['/login'];

export function AdminAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Initialize API client
  useEffect(() => {
    initAPI({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      onTokenRefresh: (tokens: AuthTokens) => {
        // Tokens are already stored by the API client
      },
      onUnauthorized: () => {
        setUser(null);
        if (!PUBLIC_PATHS.includes(pathname)) {
          router.push('/login');
        }
      },
    });
  }, [pathname, router]);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const api = getAPI();
        const currentUser = await api.getCurrentUser();
        
        // Check if user is admin
        if (currentUser.role !== 'admin' && currentUser.role !== 'super_admin') {
          throw new Error('Not authorized');
        }
        
        setUser(currentUser);
      } catch (error) {
        setUser(null);
        const api = getAPI();
        api.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    // Only run on client side
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (token) {
      checkAuth();
    } else {
      setIsLoading(false);
    }
  }, []);

  // Redirect based on auth state
  useEffect(() => {
    if (isLoading) return;

    const isPublicPath = PUBLIC_PATHS.includes(pathname);

    if (!user && !isPublicPath) {
      router.push('/login');
    } else if (user && pathname === '/login') {
      router.push('/');
    }
  }, [user, isLoading, pathname, router]);

  const login = useCallback(async (data: LoginRequest) => {
    const api = getAPI();
    const response = await api.login(data);
    
    // Check if user is admin
    if (response.user.role !== 'admin' && response.user.role !== 'super_admin') {
      api.clearTokens();
      throw new Error('You do not have admin access');
    }
    
    setUser(response.user);
    router.push('/');
  }, [router]);

  const logout = useCallback(async () => {
    const api = getAPI();
    try {
      await api.logout();
    } catch (error) {
      // Clear tokens even if logout fails
    }
    setUser(null);
    router.push('/login');
  }, [router]);

  const refreshUser = useCallback(async () => {
    const api = getAPI();
    const currentUser = await api.getCurrentUser();
    setUser(currentUser);
  }, []);

  return (
    <AdminAuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin' || user?.role === 'super_admin',
        login,
        logout,
        refreshUser,
      }}
    >
      {isLoading && !PUBLIC_PATHS.includes(pathname) ? (
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-teal-500/30 border-t-teal-500 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Loading admin portal...</p>
          </div>
        </div>
      ) : (
        children
      )}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const context = useContext(AdminAuthContext);
  if (!context) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider');
  }
  return context;
}
