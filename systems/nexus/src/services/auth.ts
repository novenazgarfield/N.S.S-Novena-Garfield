// Authentication and authorization service

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { realApiService } from './realApi';

export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  permissions: Permission[];
  avatar?: string;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserRole {
  id: string;
  name: string;
  description: string;
  level: number; // 1=admin, 2=researcher, 3=user, 4=guest
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string; // create, read, update, delete, execute
}

export interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  updateProfile: (updates: Partial<User>) => Promise<boolean>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<boolean>;
  
  // Permission checks
  hasPermission: (resource: string, action: string) => boolean;
  hasRole: (roleName: string) => boolean;
  canAccess: (feature: string) => boolean;
  
  // Utility
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearAuth: () => void;
}

export interface LoginCredentials {
  username: string;
  password: string;
  rememberMe?: boolean;
}

// Default permissions for different roles
const DEFAULT_PERMISSIONS = {
  admin: [
    'system:*', 'users:*', 'data:*', 'settings:*'
  ],
  researcher: [
    'system:read', 'data:*', 'analysis:*', 'rag:*', 'chat:*'
  ],
  user: [
    'system:read', 'data:read', 'analysis:read', 'rag:read', 'chat:*'
  ],
  guest: [
    'system:read', 'data:read'
  ]
};

// Feature access mapping
const FEATURE_ACCESS = {
  dashboard: ['admin', 'researcher', 'user', 'guest'],
  rag: ['admin', 'researcher', 'user'],
  chat: ['admin', 'researcher', 'user'],
  genome: ['admin', 'researcher'],
  molecular: ['admin', 'researcher'],
  chronicle: ['admin', 'researcher', 'user'],
  settings: ['admin'],
  'user-management': ['admin'],
  'system-monitoring': ['admin', 'researcher'],
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login action
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });

        try {
          const response = await realApiService.login(credentials);

          if (response.success && response.data) {
            const { token, user } = response.data;

            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });

            // Store token in localStorage for API requests
            localStorage.setItem('auth_token', token);

            return true;
          } else {
            set({
              isLoading: false,
              error: response.error || 'Login failed',
            });
            return false;
          }
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Login failed',
          });
          return false;
        }
      },

      // Logout action
      logout: async () => {
        set({ isLoading: true });

        try {
          await realApiService.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear state regardless of API response
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });

          localStorage.removeItem('auth_token');
        }
      },

      // Refresh token
      refreshToken: async () => {
        const { token } = get();
        if (!token) return false;

        try {
          const response = await realApiService.getProfile();

          if (response.success && response.data) {
            set({
              user: response.data,
              error: null,
            });
            return true;
          } else {
            // Token might be expired, clear auth
            get().clearAuth();
            return false;
          }
        } catch (error) {
          get().clearAuth();
          return false;
        }
      },

      // Update profile
      updateProfile: async (updates: Partial<User>) => {
        const { user } = get();
        if (!user) return false;

        set({ isLoading: true, error: null });

        try {
          // This would call a real API endpoint
          // const response = await realApiService.updateProfile(updates);
          
          // For now, simulate success
          const updatedUser = { ...user, ...updates };
          
          set({
            user: updatedUser,
            isLoading: false,
          });

          return true;
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Update failed',
          });
          return false;
        }
      },

      // Change password
      changePassword: async (oldPassword: string, newPassword: string) => {
        set({ isLoading: true, error: null });

        try {
          // This would call a real API endpoint
          // const response = await realApiService.changePassword(oldPassword, newPassword);
          
          // For now, simulate success
          set({ isLoading: false });
          return true;
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Password change failed',
          });
          return false;
        }
      },

      // Permission checks
      hasPermission: (resource: string, action: string) => {
        const { user } = get();
        if (!user) return false;

        // Admin has all permissions
        if (user.role.name === 'admin') return true;

        // Check specific permissions
        return user.permissions.some(
          p => (p.resource === resource || p.resource === '*') &&
               (p.action === action || p.action === '*')
        );
      },

      hasRole: (roleName: string) => {
        const { user } = get();
        return user?.role.name === roleName;
      },

      canAccess: (feature: string) => {
        const { user } = get();
        if (!user) return false;

        const allowedRoles = FEATURE_ACCESS[feature as keyof typeof FEATURE_ACCESS];
        return allowedRoles?.includes(user.role.name) || false;
      },

      // Utility actions
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      
      setError: (error: string | null) => set({ error }),

      clearAuth: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
        localStorage.removeItem('auth_token');
      },
    }),
    {
      name: 'nexus-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Auth utilities
export class AuthUtils {
  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  static getTokenPayload(token: string): any {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch {
      return null;
    }
  }

  static formatUserName(user: User): string {
    return `${user.firstName} ${user.lastName}`.trim() || user.username;
  }

  static getUserInitials(user: User): string {
    const firstName = user.firstName?.[0] || '';
    const lastName = user.lastName?.[0] || '';
    return (firstName + lastName).toUpperCase() || user.username[0]?.toUpperCase() || 'U';
  }

  static getRoleColor(role: UserRole): string {
    switch (role.name) {
      case 'admin': return '#f44336';
      case 'researcher': return '#2196f3';
      case 'user': return '#4caf50';
      case 'guest': return '#9e9e9e';
      default: return '#757575';
    }
  }
}

// Auth hooks
export const useAuth = () => {
  const auth = useAuthStore();
  
  return {
    ...auth,
    isAdmin: auth.hasRole('admin'),
    isResearcher: auth.hasRole('researcher'),
    canManageUsers: auth.hasPermission('users', 'create'),
    canAccessSettings: auth.canAccess('settings'),
  };
};

// Protected route wrapper
export const withAuth = <T extends object>(
  Component: React.ComponentType<T>,
  requiredRole?: string,
  requiredPermission?: { resource: string; action: string }
) => {
  return (props: T) => {
    const { isAuthenticated, hasRole, hasPermission } = useAuth();

    if (!isAuthenticated) {
      return <div>Please log in to access this feature.</div>;
    }

    if (requiredRole && !hasRole(requiredRole)) {
      return <div>You don't have permission to access this feature.</div>;
    }

    if (requiredPermission && !hasPermission(requiredPermission.resource, requiredPermission.action)) {
      return <div>You don't have permission to perform this action.</div>;
    }

    return <Component {...props} />;
  };
};

// Initialize auth on app start
export const initializeAuth = async () => {
  const { token, refreshToken, clearAuth } = useAuthStore.getState();

  if (token) {
    if (AuthUtils.isTokenExpired(token)) {
      clearAuth();
    } else {
      // Try to refresh user data
      await refreshToken();
    }
  }
};