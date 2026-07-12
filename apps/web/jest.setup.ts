import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    };
  },
  usePathname() {
    return '/';
  },
  useSearchParams() {
    return new URLSearchParams();
  },
}));

// Mock organization provider
jest.mock('@/providers/organization-provider', () => ({
  useOrganizationContext: jest.fn(() => ({
    currentOrganization: {
      id: 'org-123',
      name: 'Test Organization',
      slug: 'test-org',
      role: 'admin',
      owner_id: 'user-123',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    organizations: [],
    isLoading: false,
    switchOrganization: jest.fn(),
    clearOrganization: jest.fn(),
    hasRole: jest.fn(() => true),
    isAdmin: true,
    isOwner: true,
    refresh: jest.fn(),
  })),
  OrganizationProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock auth provider
jest.mock('@/providers/auth-provider', () => ({
  useAuth: jest.fn(() => ({
    user: {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user',
      status: 'active',
      created_at: '2024-01-01T00:00:00Z',
    },
    isAuthenticated: true,
    isLoading: false,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  })),
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;
