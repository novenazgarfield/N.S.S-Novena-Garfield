// Performance optimization configuration for NEXUS

export const PERFORMANCE_CONFIG = {
  // Code splitting configuration
  LAZY_LOAD_DELAY: 100, // ms
  CHUNK_SIZE_LIMIT: 500000, // 500KB
  
  // API configuration
  API_TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
  
  // Cache configuration
  CACHE_TTL: 300000, // 5 minutes
  MAX_CACHE_SIZE: 100, // entries
  
  // UI performance
  DEBOUNCE_DELAY: 300, // ms
  THROTTLE_DELAY: 100, // ms
  VIRTUAL_LIST_THRESHOLD: 100, // items
  
  // Memory management
  MAX_CHAT_MESSAGES: 1000,
  MAX_LOG_ENTRIES: 500,
  CLEANUP_INTERVAL: 60000, // 1 minute
};

// Performance monitoring utilities
export class PerformanceMonitor {
  private static metrics: Map<string, number[]> = new Map();
  
  static startTiming(label: string): () => void {
    const start = performance.now();
    
    return () => {
      const end = performance.now();
      const duration = end - start;
      
      if (!this.metrics.has(label)) {
        this.metrics.set(label, []);
      }
      
      const times = this.metrics.get(label)!;
      times.push(duration);
      
      // Keep only last 100 measurements
      if (times.length > 100) {
        times.shift();
      }
      
      console.debug(`⏱️ ${label}: ${duration.toFixed(2)}ms`);
    };
  }
  
  static getAverageTime(label: string): number {
    const times = this.metrics.get(label);
    if (!times || times.length === 0) return 0;
    
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }
  
  static getAllMetrics(): Record<string, { avg: number; count: number }> {
    const result: Record<string, { avg: number; count: number }> = {};
    
    for (const [label, times] of this.metrics.entries()) {
      result[label] = {
        avg: this.getAverageTime(label),
        count: times.length,
      };
    }
    
    return result;
  }
  
  static clearMetrics(): void {
    this.metrics.clear();
  }
}

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number = PERFORMANCE_CONFIG.DEBOUNCE_DELAY
): (...args: Parameters<T>) => void {
  let timeoutId: number;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => func(...args), delay);
  };
}

// Throttle utility
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number = PERFORMANCE_CONFIG.THROTTLE_DELAY
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

// Cache implementation
export class SimpleCache<T> {
  private cache = new Map<string, { data: T; timestamp: number }>();
  private maxSize: number;
  private ttl: number;
  
  constructor(
    maxSize: number = PERFORMANCE_CONFIG.MAX_CACHE_SIZE,
    ttl: number = PERFORMANCE_CONFIG.CACHE_TTL
  ) {
    this.maxSize = maxSize;
    this.ttl = ttl;
  }
  
  set(key: string, data: T): void {
    // Remove oldest entries if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }
  
  get(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    // Check if entry has expired
    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }
  
  has(key: string): boolean {
    return this.get(key) !== null;
  }
  
  delete(key: string): boolean {
    return this.cache.delete(key);
  }
  
  clear(): void {
    this.cache.clear();
  }
  
  size(): number {
    return this.cache.size;
  }
}