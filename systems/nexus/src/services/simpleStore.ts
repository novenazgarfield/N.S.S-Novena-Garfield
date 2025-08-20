import { create } from 'zustand';
import { SystemStatus, ThemeConfig } from '../types';

// Simplified App Store
interface AppState {
  // UI state
  sidebarOpen: boolean;
  currentSystem: string;
  theme: ThemeConfig;
  
  // System state
  systems: SystemStatus[];
  systemsLoading: boolean;
  
  // Actions
  setSidebarOpen: (open: boolean) => void;
  setCurrentSystem: (system: string) => void;
  setTheme: (theme: Partial<ThemeConfig>) => void;
  fetchSystems: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
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
  systems: [],
  systemsLoading: false,

  // Actions
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setCurrentSystem: (system) => set({ currentSystem: system }),
  setTheme: (themeUpdate) => set((state) => ({ 
    theme: { ...state.theme, ...themeUpdate } 
  })),

  // System actions
  fetchSystems: async () => {
    set({ systemsLoading: true });
    
    // Mock system data for now
    const mockSystems: SystemStatus[] = [
      {
        id: 'dashboard',
        name: 'Dashboard',
        status: 'online',
        uptime: 99.9,
        lastCheck: new Date(),
        description: 'System overview and monitoring',
      },
      {
        id: 'rag',
        name: 'RAG System',
        status: 'online',
        uptime: 98.5,
        lastCheck: new Date(),
        description: 'AI-powered document search',
      },
      {
        id: 'changlee',
        name: 'Changlee Assistant',
        status: 'online',
        uptime: 97.2,
        lastCheck: new Date(),
        description: 'AI desktop assistant',
      },
      {
        id: 'chronicle',
        name: 'Chronicle',
        status: 'offline',
        uptime: 0,
        lastCheck: new Date(),
        description: 'Research documentation',
      },
      {
        id: 'genome',
        name: 'Genome Jigsaw',
        status: 'online',
        uptime: 95.8,
        lastCheck: new Date(),
        description: 'Genome analysis pipeline',
      },
      {
        id: 'molecular',
        name: 'Molecular Simulation',
        status: 'online',
        uptime: 94.3,
        lastCheck: new Date(),
        description: 'MD simulation toolkit',
      },
    ];

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    set({ systems: mockSystems, systemsLoading: false });
  },
}));

// System Modules Configuration
export const SYSTEM_MODULES = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    description: 'System overview and monitoring',
    icon: 'Dashboard',
    path: '/',
    status: 'online' as const,
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
    status: 'online' as const,
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
    status: 'online' as const,
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
    status: 'offline' as const,
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
    status: 'online' as const,
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
    status: 'online' as const,
    features: ['MD Simulations', 'Trajectory Analysis', 'Visualization'],
    version: '1.0.0',
    lastUpdated: new Date(),
  },
];