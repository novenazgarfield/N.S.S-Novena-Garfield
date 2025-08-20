import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, SystemStatus, SystemMetrics } from '../types';

// API Configuration
const API_CONFIG = {
  baseURL: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : window.location.origin,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// System endpoints configuration
const SYSTEM_ENDPOINTS = {
  rag: {
    baseURL: 'http://localhost:8501',
    endpoints: {
      query: '/api/query',
      documents: '/api/documents',
      status: '/api/status',
    }
  },
  changlee: {
    baseURL: 'http://localhost:3000',
    endpoints: {
      chat: '/api/chat',
      sessions: '/api/sessions',
      status: '/api/status',
    }
  },
  chronicle: {
    baseURL: 'http://localhost:3001',
    endpoints: {
      entries: '/api/entries',
      search: '/api/search',
      status: '/api/status',
    }
  },
  genome: {
    baseURL: 'http://localhost:8080',
    endpoints: {
      analyses: '/api/analyses',
      upload: '/api/upload',
      status: '/api/status',
    }
  },
  molecular: {
    baseURL: 'http://localhost:8081',
    endpoints: {
      simulations: '/api/simulations',
      results: '/api/results',
      status: '/api/status',
    }
  }
};

class ApiClient {
  private client: AxiosInstance;
  private systemClients: Map<string, AxiosInstance> = new Map();

  constructor() {
    // Create main API client
    this.client = axios.create(API_CONFIG);
    
    // Setup interceptors
    this.setupInterceptors();
    
    // Initialize system-specific clients
    this.initializeSystemClients();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Add timestamp
        config.headers['X-Request-Time'] = new Date().toISOString();
        
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('❌ Response Error:', error.response?.status, error.response?.data);
        
        // Handle common errors
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      }
    );
  }

  private initializeSystemClients() {
    Object.entries(SYSTEM_ENDPOINTS).forEach(([system, config]) => {
      const client = axios.create({
        baseURL: config.baseURL,
        timeout: API_CONFIG.timeout,
        headers: API_CONFIG.headers,
      });
      
      // Apply same interceptors
      // Copy interceptors from main client
      client.interceptors.request.use(
        (config) => {
          const token = localStorage.getItem('auth_token');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
          return config;
        }
      );
      client.interceptors.response.use(
        (response) => response,
        (error) => {
          if (error.response?.status === 401) {
            localStorage.removeItem('auth_token');
          }
          return Promise.reject(error);
        }
      );
      
      this.systemClients.set(system, client);
    });
  }

  // Generic API methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get(url, config);
      return this.formatResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post(url, data, config);
      return this.formatResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put(url, data, config);
      return this.formatResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete(url, config);
      return this.formatResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // System-specific methods
  async getSystemStatus(system: string): Promise<ApiResponse<SystemStatus>> {
    const client = this.systemClients.get(system);
    if (!client) {
      return {
        success: false,
        error: `Unknown system: ${system}`,
        timestamp: new Date(),
      };
    }

    try {
      const response = await client.get('/api/status');
      return this.formatResponse(response);
    } catch (error) {
      return {
        success: false,
        error: `System ${system} is offline`,
        timestamp: new Date(),
      };
    }
  }

  async getAllSystemsStatus(): Promise<ApiResponse<SystemStatus[]>> {
    const systems = Object.keys(SYSTEM_ENDPOINTS);
    const statusPromises = systems.map(system => this.getSystemStatus(system));
    
    try {
      const results = await Promise.allSettled(statusPromises);
      const statuses: SystemStatus[] = results.map((result, index) => {
        const systemName = systems[index];
        
        if (result.status === 'fulfilled' && result.value.success) {
          return result.value.data!;
        } else {
          return {
            id: systemName,
            name: systemName.charAt(0).toUpperCase() + systemName.slice(1),
            status: 'offline' as const,
            uptime: 0,
            lastCheck: new Date(),
            description: `${systemName} system`,
          };
        }
      });

      return {
        success: true,
        data: statuses,
        timestamp: new Date(),
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  // RAG System methods
  async ragQuery(query: string): Promise<ApiResponse<any>> {
    const client = this.systemClients.get('rag');
    if (!client) return this.systemOfflineError('RAG');

    return this.makeSystemRequest(client, 'post', '/api/query', { query });
  }

  async ragGetDocuments(): Promise<ApiResponse<any[]>> {
    const client = this.systemClients.get('rag');
    if (!client) return this.systemOfflineError('RAG');

    return this.makeSystemRequest(client, 'get', '/api/documents');
  }

  // Changlee methods
  async changleeChat(message: string, sessionId?: string): Promise<ApiResponse<any>> {
    const client = this.systemClients.get('changlee');
    if (!client) return this.systemOfflineError('Changlee');

    return this.makeSystemRequest(client, 'post', '/api/chat', { message, sessionId });
  }

  async changleeGetSessions(): Promise<ApiResponse<any[]>> {
    const client = this.systemClients.get('changlee');
    if (!client) return this.systemOfflineError('Changlee');

    return this.makeSystemRequest(client, 'get', '/api/sessions');
  }

  // Chronicle methods
  async chronicleGetEntries(): Promise<ApiResponse<any[]>> {
    const client = this.systemClients.get('chronicle');
    if (!client) return this.systemOfflineError('Chronicle');

    return this.makeSystemRequest(client, 'get', '/api/entries');
  }

  async chronicleCreateEntry(entry: any): Promise<ApiResponse<any>> {
    const client = this.systemClients.get('chronicle');
    if (!client) return this.systemOfflineError('Chronicle');

    return this.makeSystemRequest(client, 'post', '/api/entries', entry);
  }

  // Genome Jigsaw methods
  async genomeGetAnalyses(): Promise<ApiResponse<any[]>> {
    const client = this.systemClients.get('genome');
    if (!client) return this.systemOfflineError('Genome Jigsaw');

    return this.makeSystemRequest(client, 'get', '/api/analyses');
  }

  async genomeStartAnalysis(data: any): Promise<ApiResponse<any>> {
    const client = this.systemClients.get('genome');
    if (!client) return this.systemOfflineError('Genome Jigsaw');

    return this.makeSystemRequest(client, 'post', '/api/analyses', data);
  }

  // Molecular Simulation methods
  async molecularGetSimulations(): Promise<ApiResponse<any[]>> {
    const client = this.systemClients.get('molecular');
    if (!client) return this.systemOfflineError('Molecular Simulation');

    return this.makeSystemRequest(client, 'get', '/api/simulations');
  }

  async molecularStartSimulation(data: any): Promise<ApiResponse<any>> {
    const client = this.systemClients.get('molecular');
    if (!client) return this.systemOfflineError('Molecular Simulation');

    return this.makeSystemRequest(client, 'post', '/api/simulations', data);
  }

  // Helper methods
  private async makeSystemRequest<T>(
    client: AxiosInstance, 
    method: 'get' | 'post' | 'put' | 'delete', 
    url: string, 
    data?: any
  ): Promise<ApiResponse<T>> {
    try {
      const response = method === 'get' || method === 'delete' 
        ? await client[method](url)
        : await client[method](url, data);
      
      return this.formatResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  private formatResponse<T>(response: AxiosResponse): ApiResponse<T> {
    return {
      success: true,
      data: response.data,
      timestamp: new Date(),
    };
  }

  private handleError(error: any): ApiResponse {
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Unknown error',
      timestamp: new Date(),
    };
  }

  private systemOfflineError(systemName: string): ApiResponse {
    return {
      success: false,
      error: `${systemName} system is not available`,
      timestamp: new Date(),
    };
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
export default apiClient;