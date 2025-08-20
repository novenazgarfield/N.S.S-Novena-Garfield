// Core system types for NEXUS
export interface SystemStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'error' | 'maintenance';
  uptime: number;
  lastCheck: Date;
  url?: string;
  description: string;
  version?: string;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: {
    upload: number;
    download: number;
  };
  timestamp: Date;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'researcher' | 'user';
  avatar?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
  defaultSystem?: string;
}

export interface ApiEndpoint {
  id: string;
  name: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  description: string;
  system: string;
}

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  description?: string;
  badge?: string | number;
  children?: NavigationItem[];
}

export interface SystemModule {
  id: string;
  name: string;
  description: string;
  icon: string;
  path: string;
  status: SystemStatus['status'];
  features: string[];
  version: string;
  lastUpdated: Date;
}

// RAG System Types
export interface RAGQuery {
  id: string;
  query: string;
  response: string;
  timestamp: Date;
  sources: string[];
  confidence: number;
}

export interface RAGDocument {
  id: string;
  title: string;
  content: string;
  type: string;
  uploadDate: Date;
  size: number;
  indexed: boolean;
}

// Changlee Types
export interface ChangleeMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: string[];
}

export interface ChangleeSession {
  id: string;
  title: string;
  messages: ChangleeMessage[];
  createdAt: Date;
  updatedAt: Date;
}

// Chronicle Types
export interface ChronicleEntry {
  id: string;
  title: string;
  content: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  author: string;
  category: string;
}

// Genome Jigsaw Types
export interface GenomeAnalysis {
  id: string;
  sampleName: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: Date;
  endTime?: Date;
  results?: GenomeResults;
}

export interface GenomeResults {
  assemblyStats: {
    contigs: number;
    n50: number;
    totalLength: number;
    gcContent: number;
  };
  annotationStats: {
    genes: number;
    proteins: number;
    rRNAs: number;
    tRNAs: number;
  };
  qualityMetrics: {
    completeness: number;
    contamination: number;
  };
}

// Molecular Simulation Types
export interface SimulationJob {
  id: string;
  name: string;
  type: 'md' | 'minimization' | 'equilibration';
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: Date;
  endTime?: Date;
  inputFiles: string[];
  outputFiles: string[];
  parameters: Record<string, any>;
}

export interface SimulationResults {
  rmsd: number[];
  rmsf: number[];
  energy: number[];
  temperature: number[];
  pressure: number[];
  volume: number[];
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Theme Types
export interface ThemeConfig {
  mode: 'light' | 'dark';
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
}

// Notification Types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  read: boolean;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: string;
  primary?: boolean;
}