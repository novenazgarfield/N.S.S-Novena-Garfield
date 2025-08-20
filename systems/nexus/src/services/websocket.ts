// WebSocket service for real-time features

export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
  id?: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export type WebSocketEventHandler = (message: WebSocketMessage) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private reconnectTimer: number | null = null;
  private heartbeatTimer: number | null = null;
  private isConnecting = false;
  private isManualClose = false;

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...config,
    };
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'));
        return;
      }

      this.isConnecting = true;
      this.isManualClose = false;

      try {
        this.ws = new WebSocket(this.config.url);

        this.ws.onopen = () => {
          console.log('🔗 WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.emit('connection', { status: 'connected' });
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          this.emit('connection', { status: 'disconnected', code: event.code, reason: event.reason });

          if (!this.isManualClose && this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnecting = false;
          this.emit('error', { error: 'WebSocket connection error' });
          reject(new Error('WebSocket connection failed'));
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.isManualClose = true;
    this.clearReconnectTimer();
    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  send(type: string, payload: any): boolean {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send message');
      return false;
    }

    const message: WebSocketMessage = {
      type,
      payload,
      timestamp: new Date().toISOString(),
      id: this.generateMessageId(),
    };

    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }

  on(eventType: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    // Handle system messages
    if (message.type === 'heartbeat') {
      this.send('heartbeat_ack', { timestamp: new Date().toISOString() });
      return;
    }

    // Emit to registered handlers
    this.emit(message.type, message.payload);
  }

  private emit(eventType: string, payload: any): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler({ type: eventType, payload, timestamp: new Date().toISOString() });
        } catch (error) {
          console.error('WebSocket event handler error:', error);
        }
      });
    }
  }

  private scheduleReconnect(): void {
    this.clearReconnectTimer();
    this.reconnectAttempts++;

    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );

    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimer = window.setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = window.setInterval(() => {
      this.send('heartbeat', { timestamp: new Date().toISOString() });
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'unknown';
    }
  }

  getReconnectInfo(): { attempts: number; maxAttempts: number; isReconnecting: boolean } {
    return {
      attempts: this.reconnectAttempts,
      maxAttempts: this.config.maxReconnectAttempts,
      isReconnecting: this.reconnectTimer !== null,
    };
  }
}

// Real-time event types
export const REALTIME_EVENTS = {
  // System events
  SYSTEM_STATUS_UPDATE: 'system_status_update',
  SYSTEM_ALERT: 'system_alert',
  SYSTEM_MAINTENANCE: 'system_maintenance',
  
  // Chat events
  CHAT_MESSAGE: 'chat_message',
  CHAT_TYPING: 'chat_typing',
  CHAT_SESSION_UPDATE: 'chat_session_update',
  
  // RAG events
  RAG_PROCESSING: 'rag_processing',
  RAG_RESULT: 'rag_result',
  RAG_ERROR: 'rag_error',
  
  // Analysis events
  GENOME_ANALYSIS_START: 'genome_analysis_start',
  GENOME_ANALYSIS_PROGRESS: 'genome_analysis_progress',
  GENOME_ANALYSIS_COMPLETE: 'genome_analysis_complete',
  
  MOLECULAR_SIMULATION_START: 'molecular_simulation_start',
  MOLECULAR_SIMULATION_PROGRESS: 'molecular_simulation_progress',
  MOLECULAR_SIMULATION_COMPLETE: 'molecular_simulation_complete',
  
  // User events
  USER_ACTIVITY: 'user_activity',
  USER_NOTIFICATION: 'user_notification',
  
  // Connection events
  CONNECTION: 'connection',
  ERROR: 'error',
} as const;

// WebSocket service factory
export function createWebSocketService(baseUrl: string = 'ws://localhost:8000'): WebSocketService {
  const wsUrl = baseUrl.replace(/^http/, 'ws') + '/ws';
  
  return new WebSocketService({
    url: wsUrl,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,
  });
}

// Global WebSocket service instance
export const globalWebSocketService = createWebSocketService(
  process.env.VITE_API_BASE_URL || 'ws://localhost:8000'
);