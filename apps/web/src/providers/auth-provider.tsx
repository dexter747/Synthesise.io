'use client';

import { createContext, useContext, useCallback, useEffect, useState, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { SynthesizeAPI, initAPI, getAPI } from '@synthesize/api-client';
import type { User, AuthTokens, LoginRequest, RegisterRequest, LoginResponse } from '@synthesize/types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<User | undefined>;
  setTokens: (accessToken: string, refreshToken: string) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Function to check if a path is public
function isPublicPath(pathname: string): boolean {
  const publicPaths = [
    '/',
    '/pricing',
    '/contact',
    '/team',
  ];
  
  const publicPrefixes = [
    '/auth/',
    '/features/',
    '/legal/',
    '/docs/',
    '/documentation/',
    '/help/',
    '/support/',
  ];
  
  // Check exact matches
  if (publicPaths.includes(pathname)) {
    return true;
  }
  
  // Check prefixes
  return publicPrefixes.some(prefix => pathname.startsWith(prefix));
}

export function AuthProvider({ children }: { children: ReactNode }) {
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
        if (!isPublicPath(pathname)) {
          router.push('/auth/login');
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
        setUser(currentUser);
      } catch (error) {
        // On any error (401, network, etc.), clear tokens silently
        setUser(null);
        const api = getAPI();
        api.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    // Only check if we have a token AND on private pages
    if (typeof window !== 'undefined' && localStorage.getItem('access_token')) {
      // Only validate user on protected pages to avoid 401s on landing page
      if (!isPublicPath(pathname)) {
        checkAuth();
      } else {
        // On public pages, don't validate - just set loading to false
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, [pathname]);

  // Redirect based on auth state
  useEffect(() => {
    if (isLoading) return;

    const isPublic = isPublicPath(pathname);
    const isCheckoutOrPayment = pathname.startsWith('/checkout') || pathname.startsWith('/payment');
    const isPricingPage = pathname === '/pricing';
    const isAuthPage = pathname.startsWith('/auth/');
    const validTiers = ['beginner', 'pro', 'business', 'enterprise'];

    // Don't redirect if we're already on the right page
    if (!user && isPublic) {
      return; // User not logged in, on public page - OK
    }
    
    if (!user && !isPublic) {
      // User not logged in, trying to access private page - redirect to login
      router.push('/auth/login');
      return;
    }
    
    if (user && isAuthPage) {
      // User logged in, on auth pages - redirect to pricing
      router.push('/pricing');
      return;
    }
    
    if (user && !isPublic && !isCheckoutOrPayment && !isPricingPage) {
      // User logged in, trying to access dashboard - check subscription
      // Allow access if user has a valid paid tier (beginner, pro, business, enterprise)
      // Users without subscription_tier or with 'free' tier should go to pricing
      const hasPaidSubscription = user.subscription_tier && validTiers.includes(user.subscription_tier);
      if (!hasPaidSubscription) {
        router.push('/pricing');
        return;
      }
    }
  }, [user, isLoading, pathname, router]);

  const login = useCallback(async (data: LoginRequest) => {
    const api = getAPI();
    const response = await api.login(data);
    setUser(response.user);
    // ALWAYS redirect to pricing after login - payment required
    // The pricing page will redirect to dashboard if user has active subscription
    router.push('/pricing');
  }, [router]);

  const register = useCallback(async (data: RegisterRequest) => {
    const api = getAPI();
    const response = await api.register(data);
    // Don't set user or redirect - let the caller handle it
    // Registration requires email verification before logging in
    return response;
  }, []);

  const logout = useCallback(async () => {
    const api = getAPI();
    try {
      await api.logout();
    } catch (error) {
      // Clear tokens even if logout fails
    }
    setUser(null);
    router.push('/auth/login');
  }, [router]);

  const refreshUser = useCallback(async () => {
    try {
      const api = getAPI();
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
      throw error;
    }
  }, []);

  const setTokens = useCallback((accessToken: string, refreshToken: string) => {
    const api = getAPI();
    api.setTokens({ 
      access_token: accessToken, 
      refresh_token: refreshToken,
      token_type: 'bearer',
      expires_in: 3600, // Default 1 hour, will be refreshed from server
    });
    // Refresh user data after setting tokens
    refreshUser();
  }, [refreshUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
        setTokens,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
