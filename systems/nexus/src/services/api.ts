// API Service Layer for NEXUS Research Workstation
// Centralized API management for all integrated systems

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface SystemStatus {
  name: string;
  status: 'online' | 'offline' | 'maintenance';
  version: string;
  lastCheck: string;
  health: number; // 0-100
}

export interface RAGQuery {
  query: string;
  context?: string;
  maxResults?: number;
}

export interface RAGResponse {
  answer: string;
  confidence: number;
  sources: Array<{
    title: string;
    content: string;
    relevance: number;
    url?: string;
  }>;
  processingTime: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  name: string;
  created: string;
  updated: string;
  messages: ChatMessage[];
}

class ApiService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.timeout = 30000; // 30 seconds
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      clearTimeout(timeoutId);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // System Status APIs
  async getSystemStatus(): Promise<ApiResponse<SystemStatus[]>> {
    return this.request<SystemStatus[]>('/api/system/status');
  }

  async getSystemHealth(systemName: string): Promise<ApiResponse<SystemStatus>> {
    return this.request<SystemStatus>(`/api/system/${systemName}/health`);
  }

  // RAG System APIs
  async queryRAG(query: RAGQuery): Promise<ApiResponse<RAGResponse>> {
    return this.request<RAGResponse>('/api/rag/query', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  async getRAGSources(): Promise<ApiResponse<string[]>> {
    return this.request<string[]>('/api/rag/sources');
  }

  // Changlee Assistant APIs
  async getChatSessions(): Promise<ApiResponse<ChatSession[]>> {
    return this.request<ChatSession[]>('/api/chat/sessions');
  }

  async createChatSession(name: string): Promise<ApiResponse<ChatSession>> {
    return this.request<ChatSession>('/api/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async sendChatMessage(
    sessionId: string,
    message: string
  ): Promise<ApiResponse<ChatMessage>> {
    return this.request<ChatMessage>(`/api/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content: message }),
    });
  }

  async getChatHistory(sessionId: string): Promise<ApiResponse<ChatMessage[]>> {
    return this.request<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`);
  }

  // Genome Analysis APIs
  async uploadGenomeFile(file: File): Promise<ApiResponse<{ fileId: string }>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<{ fileId: string }>('/api/genome/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async analyzeGenome(fileId: string, analysisType: string): Promise<ApiResponse<any>> {
    return this.request('/api/genome/analyze', {
      method: 'POST',
      body: JSON.stringify({ fileId, analysisType }),
    });
  }

  // Molecular Simulation APIs
  async createSimulation(config: any): Promise<ApiResponse<{ simulationId: string }>> {
    return this.request<{ simulationId: string }>('/api/simulation/create', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async getSimulationStatus(simulationId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/simulation/${simulationId}/status`);
  }

  async getSimulationResults(simulationId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/simulation/${simulationId}/results`);
  }

  // Chronicle System APIs
  async getChronicleEntries(): Promise<ApiResponse<any[]>> {
    return this.request('/api/chronicle/entries');
  }

  async createChronicleEntry(entry: any): Promise<ApiResponse<any>> {
    return this.request('/api/chronicle/entries', {
      method: 'POST',
      body: JSON.stringify(entry),
    });
  }

  // File Management APIs
  async uploadFile(file: File, category: string): Promise<ApiResponse<{ fileId: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    return this.request<{ fileId: string }>('/api/files/upload', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }

  async getFiles(category?: string): Promise<ApiResponse<any[]>> {
    const query = category ? `?category=${category}` : '';
    return this.request(`/api/files${query}`);
  }

  async deleteFile(fileId: string): Promise<ApiResponse<void>> {
    return this.request(`/api/files/${fileId}`, {
      method: 'DELETE',
    });
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Mock data for development (when backend is not available)
export const mockApiService = {
  async getSystemStatus(): Promise<ApiResponse<SystemStatus[]>> {
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    return {
      success: true,
      data: [
        { name: 'Dashboard', status: 'online', version: '1.0.0', lastCheck: new Date().toISOString(), health: 98 },
        { name: 'RAG System', status: 'online', version: '1.2.1', lastCheck: new Date().toISOString(), health: 95 },
        { name: 'Changlee Assistant', status: 'online', version: '2.0.0', lastCheck: new Date().toISOString(), health: 97 },
        { name: 'Chronicle', status: 'offline', version: '0.9.0', lastCheck: new Date().toISOString(), health: 0 },
        { name: 'Genome Jigsaw', status: 'online', version: '1.1.0', lastCheck: new Date().toISOString(), health: 92 },
        { name: 'Molecular Simulation', status: 'online', version: '1.3.0', lastCheck: new Date().toISOString(), health: 89 },
      ],
      timestamp: new Date().toISOString(),
    };
  },

  async queryRAG(query: RAGQuery): Promise<ApiResponse<RAGResponse>> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      success: true,
      data: {
        answer: `Based on your query "${query.query}", here's what I found: This is a comprehensive analysis of the research topic with detailed insights and recommendations.`,
        confidence: 0.87,
        sources: [
          {
            title: 'Research Paper: Advanced Analysis Methods',
            content: 'Detailed methodology and findings...',
            relevance: 0.92,
            url: 'https://example.com/paper1',
          },
          {
            title: 'Database Entry: Related Studies',
            content: 'Comprehensive database information...',
            relevance: 0.85,
          },
        ],
        processingTime: 1.2,
      },
      timestamp: new Date().toISOString(),
    };
  },

  async sendChatMessage(sessionId: string, message: string): Promise<ApiResponse<ChatMessage>> {
    await new Promise(resolve => setTimeout(resolve, 800));
    return {
      success: true,
      data: {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: `I understand you're asking about "${message}". Let me help you with that. This is a detailed response that addresses your question comprehensively.`,
        timestamp: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    };
  },
};

// Use mock service in development when backend is not available
export const activeApiService = import.meta.env.DEV ? mockApiService : apiService;