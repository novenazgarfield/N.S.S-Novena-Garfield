import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  SystemStatus, 
  User, 
  UserPreferences, 
  Notification, 
  SystemModule,
  ThemeConfig 
} from '../types';
import { apiClient } from './apiClient';

// Main App Store
interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  
  // System state
  systems: SystemStatus[];
  systemsLoading: boolean;
  
  // UI state
  sidebarOpen: boolean;
  currentSystem: string;
  theme: ThemeConfig;
  
  // Notifications
  notifications: Notification[];
  unreadCount: number;
  
  // Actions
  setUser: (user: User | null) => void;
  setSidebarOpen: (open: boolean) => void;
  setCurrentSystem: (system: string) => void;
  setTheme: (theme: Partial<ThemeConfig>) => void;
  
  // System actions
  fetchSystems: () => Promise<void>;
  updateSystemStatus: (systemId: string, status: SystemStatus) => void;
  
  // Notification actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      systems: [],
      systemsLoading: false,
      sidebarOpen: true,
      currentSystem: 'dashboard',
      theme: {
        mode: 'dark',
        primary: '#1976d2',
        secondary: '#dc004e',
        background: '#0f1419',
        surface: '#1a1a1a',
        text: '#ffffff',
      },
      notifications: [],
      unreadCount: 0,

      // User actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      
      // UI actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setCurrentSystem: (system) => set({ currentSystem: system }),
      setTheme: (themeUpdate) => set((state) => ({ 
        theme: { ...state.theme, ...themeUpdate } 
      })),

      // System actions
      fetchSystems: async () => {
        set({ systemsLoading: true });
        try {
          const response = await apiClient.getAllSystemsStatus();
          if (response.success && response.data) {
            set({ systems: response.data, systemsLoading: false });
          } else {
            console.error('Failed to fetch systems:', response.error);
            set({ systemsLoading: false });
          }
        } catch (error) {
          console.error('Error fetching systems:', error);
          set({ systemsLoading: false });
        }
      },

      updateSystemStatus: (systemId, status) => set((state) => ({
        systems: state.systems.map(system => 
          system.id === systemId ? { ...system, ...status } : system
        )
      })),

      // Notification actions
      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: Date.now().toString(),
          timestamp: new Date(),
          read: false,
        };
        
        set((state) => ({
          notifications: [newNotification, ...state.notifications],
          unreadCount: state.unreadCount + 1,
        }));
      },

      markNotificationRead: (id) => set((state) => ({
        notifications: state.notifications.map(n => 
          n.id === id ? { ...n, read: true } : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      })),

      clearNotifications: () => set({ notifications: [], unreadCount: 0 }),
    }),
    {
      name: 'nexus-app-store',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        sidebarOpen: state.sidebarOpen,
        currentSystem: state.currentSystem,
        theme: state.theme,
      }),
    }
  )
);

// RAG System Store
interface RAGState {
  queries: any[];
  documents: any[];
  currentQuery: string;
  isLoading: boolean;
  
  setCurrentQuery: (query: string) => void;
  addQuery: (query: any) => void;
  fetchDocuments: () => Promise<void>;
  submitQuery: (query: string) => Promise<void>;
}

export const useRAGStore = create<RAGState>((set, get) => ({
  queries: [],
  documents: [],
  currentQuery: '',
  isLoading: false,

  setCurrentQuery: (query) => set({ currentQuery: query }),
  
  addQuery: (query) => set((state) => ({ 
    queries: [query, ...state.queries] 
  })),

  fetchDocuments: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.ragGetDocuments();
      if (response.success && response.data) {
        set({ documents: response.data, isLoading: false });
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      set({ isLoading: false });
    }
  },

  submitQuery: async (query) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.ragQuery(query);
      if (response.success && response.data) {
        get().addQuery(response.data);
        set({ currentQuery: '', isLoading: false });
      }
    } catch (error) {
      console.error('Error submitting query:', error);
      set({ isLoading: false });
    }
  },
}));

// Changlee Store
interface ChangleeState {
  sessions: any[];
  currentSession: any | null;
  messages: any[];
  isTyping: boolean;
  
  setCurrentSession: (session: any) => void;
  addMessage: (message: any) => void;
  sendMessage: (content: string) => Promise<void>;
  fetchSessions: () => Promise<void>;
}

export const useChangleeStore = create<ChangleeState>((set, get) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  isTyping: false,

  setCurrentSession: (session) => set({ 
    currentSession: session,
    messages: session?.messages || []
  }),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  sendMessage: async (content) => {
    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    
    get().addMessage(userMessage);
    set({ isTyping: true });

    try {
      const response = await apiClient.changleeChat(content, get().currentSession?.id);
      if (response.success && response.data) {
        get().addMessage(response.data);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      set({ isTyping: false });
    }
  },

  fetchSessions: async () => {
    try {
      const response = await apiClient.changleeGetSessions();
      if (response.success && response.data) {
        set({ sessions: response.data });
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  },
}));

// System Modules Configuration
export const SYSTEM_MODULES: SystemModule[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    description: 'System overview and monitoring',
    icon: 'Dashboard',
    path: '/',
    status: 'online',
    features: ['System Status', 'Metrics', 'Quick Actions'],
    version: '1.0.0',
    lastUpdated: new Date(),
  },
  {
    id: 'rag',
    name: 'RAG System',
    description: 'Retrieval-Augmented Generation AI',
    icon: 'Psychology',
    path: '/rag',
    status: 'online',
    features: ['Document Search', 'AI Responses', 'Knowledge Base'],
    version: '2.1.0',
    lastUpdated: new Date(),
  },
  {
    id: 'changlee',
    name: 'Changlee Assistant',
    description: 'AI Desktop Assistant',
    icon: 'SmartToy',
    path: '/changlee',
    status: 'online',
    features: ['Chat Interface', 'Voice Commands', 'Task Automation'],
    version: '3.0.0',
    lastUpdated: new Date(),
  },
  {
    id: 'chronicle',
    name: 'Chronicle',
    description: 'Research Documentation System',
    icon: 'MenuBook',
    path: '/chronicle',
    status: 'online',
    features: ['Note Taking', 'Research Logs', 'Knowledge Management'],
    version: '1.5.0',
    lastUpdated: new Date(),
  },
  {
    id: 'genome',
    name: 'Genome Jigsaw',
    description: 'Bacterial Genome Analysis Pipeline',
    icon: 'Biotech',
    path: '/genome',
    status: 'online',
    features: ['Genome Assembly', 'Annotation', 'Phylogenetic Analysis'],
    version: '1.0.0',
    lastUpdated: new Date(),
  },
  {
    id: 'molecular',
    name: 'Molecular Simulation',
    description: 'Molecular Dynamics Simulation Toolkit',
    icon: 'Science',
    path: '/molecular',
    status: 'online',
    features: ['MD Simulations', 'Trajectory Analysis', 'Visualization'],
    version: '1.0.0',
    lastUpdated: new Date(),
  },
];