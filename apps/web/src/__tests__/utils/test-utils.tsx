/**
 * Shared test utilities for React component testing
 */
import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock organization data
export const mockOrganization = {
  id: 'org-123',
  name: 'Test Organization',
  slug: 'test-org',
  role: 'admin' as const,
  owner_id: 'user-123',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// Mock user data
export const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user' as const,
  status: 'active' as const,
  created_at: '2024-01-01T00:00:00Z',
};

// Combined providers wrapper
interface AllTheProvidersProps {
  children: React.ReactNode;
}

function AllTheProviders({ children }: AllTheProvidersProps) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// Custom render function with all providers
function customRender(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllTheProviders, ...options });
}

// Re-export everything from @testing-library/react
export * from '@testing-library/react';

// Override render method
export { customRender as render };
