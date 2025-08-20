// Real API service implementation for NEXUS

import { ApiClient } from './apiClient';
import { 
  SystemStatus, 
  ChatMessage, 
  ChatSession, 
  RAGQuery, 
  RAGResponse,
  ApiResponse 
} from './api';

// Environment configuration
const API_CONFIG = {
  BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  ENDPOINTS: {
    // System endpoints
    SYSTEM_STATUS: '/api/v1/system/status',
    SYSTEM_HEALTH: '/api/v1/system/health',
    SYSTEM_METRICS: '/api/v1/system/metrics',
    
    // RAG endpoints
    RAG_QUERY: '/api/v1/rag/query',
    RAG_DOCUMENTS: '/api/v1/rag/documents',
    RAG_UPLOAD: '/api/v1/rag/upload',
    
    // Chat endpoints
    CHAT_SESSIONS: '/api/v1/chat/sessions',
    CHAT_MESSAGES: '/api/v1/chat/messages',
    CHAT_SEND: '/api/v1/chat/send',
    
    // Genome analysis endpoints
    GENOME_UPLOAD: '/api/v1/genome/upload',
    GENOME_ANALYZE: '/api/v1/genome/analyze',
    GENOME_RESULTS: '/api/v1/genome/results',
    
    // Molecular simulation endpoints
    MOLECULAR_UPLOAD: '/api/v1/molecular/upload',
    MOLECULAR_SIMULATE: '/api/v1/molecular/simulate',
    MOLECULAR_RESULTS: '/api/v1/molecular/results',
    
    // Chronicle endpoints
    CHRONICLE_NOTES: '/api/v1/chronicle/notes',
    CHRONICLE_SEARCH: '/api/v1/chronicle/search',
    
    // Authentication endpoints
    AUTH_LOGIN: '/api/v1/auth/login',
    AUTH_LOGOUT: '/api/v1/auth/logout',
    AUTH_REFRESH: '/api/v1/auth/refresh',
    AUTH_PROFILE: '/api/v1/auth/profile',
  }
};

export class RealApiService {
  private client: ApiClient;
  private isOnline: boolean = true;
  private retryQueue: Array<() => Promise<any>> = [];

  constructor() {
    this.client = new ApiClient({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
    });

    // Setup network monitoring
    this.setupNetworkMonitoring();
  }

  private setupNetworkMonitoring(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => {
        this.isOnline = true;
        this.processRetryQueue();
      });

      window.addEventListener('offline', () => {
        this.isOnline = false;
      });
    }
  }

  private async processRetryQueue(): Promise<void> {
    while (this.retryQueue.length > 0 && this.isOnline) {
      const request = this.retryQueue.shift();
      if (request) {
        try {
          await request();
        } catch (error) {
          console.error('Retry failed:', error);
        }
      }
    }
  }

  private async withRetry<T>(
    operation: () => Promise<T>,
    maxRetries: number = API_CONFIG.RETRY_ATTEMPTS
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === maxRetries) {
          throw lastError;
        }

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError!;
  }

  // System Status API
  async getSystemStatus(): Promise<ApiResponse<SystemStatus[]>> {
    try {
      const response = await this.withRetry(() =>
        this.client.get<SystemStatus[]>(API_CONFIG.ENDPOINTS.SYSTEM_STATUS)
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to get system status:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getSystemHealth(): Promise<ApiResponse<any>> {
    try {
      const response = await this.withRetry(() =>
        this.client.get(API_CONFIG.ENDPOINTS.SYSTEM_HEALTH)
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // RAG System API
  async queryRAG(query: RAGQuery): Promise<ApiResponse<RAGResponse>> {
    try {
      const response = await this.withRetry(() =>
        this.client.post<RAGResponse>(API_CONFIG.ENDPOINTS.RAG_QUERY, query)
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'RAG query failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async uploadDocument(file: File): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.withRetry(() =>
        this.client.post(API_CONFIG.ENDPOINTS.RAG_UPLOAD, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Chat API
  async getChatSessions(): Promise<ApiResponse<ChatSession[]>> {
    try {
      const response = await this.withRetry(() =>
        this.client.get<ChatSession[]>(API_CONFIG.ENDPOINTS.CHAT_SESSIONS)
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get chat sessions',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async sendChatMessage(sessionId: string, message: string): Promise<ApiResponse<ChatMessage>> {
    try {
      const response = await this.withRetry(() =>
        this.client.post<ChatMessage>(API_CONFIG.ENDPOINTS.CHAT_SEND, {
          sessionId,
          message,
        })
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send message',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Genome Analysis API
  async uploadGenomeFile(file: File): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('genome_file', file);

      const response = await this.withRetry(() =>
        this.client.post(API_CONFIG.ENDPOINTS.GENOME_UPLOAD, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Genome upload failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async startGenomeAnalysis(fileId: string, options: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.withRetry(() =>
        this.client.post(API_CONFIG.ENDPOINTS.GENOME_ANALYZE, {
          fileId,
          options,
        })
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Analysis failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Molecular Simulation API
  async uploadMolecularFile(file: File): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('structure_file', file);

      const response = await this.withRetry(() =>
        this.client.post(API_CONFIG.ENDPOINTS.MOLECULAR_UPLOAD, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Molecular upload failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async startMolecularSimulation(fileId: string, parameters: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.withRetry(() =>
        this.client.post(API_CONFIG.ENDPOINTS.MOLECULAR_SIMULATE, {
          fileId,
          parameters,
        })
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Simulation failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Authentication API
  async login(credentials: { username: string; password: string }): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.post(API_CONFIG.ENDPOINTS.AUTH_LOGIN, credentials);

      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
      }

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Login failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async logout(): Promise<ApiResponse<any>> {
    try {
      await this.client.post(API_CONFIG.ENDPOINTS.AUTH_LOGOUT);
      localStorage.removeItem('auth_token');

      return {
        success: true,
        data: { message: 'Logged out successfully' },
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      // Clear token even if logout fails
      localStorage.removeItem('auth_token');
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Logout failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getProfile(): Promise<ApiResponse<any>> {
    try {
      const response = await this.withRetry(() =>
        this.client.get(API_CONFIG.ENDPOINTS.AUTH_PROFILE)
      );

      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get profile',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch {
      return false;
    }
  }

  // Get connection status
  getConnectionStatus(): { online: boolean; queueSize: number } {
    return {
      online: this.isOnline,
      queueSize: this.retryQueue.length,
    };
  }
}

// Export singleton instance
export const realApiService = new RealApiService();