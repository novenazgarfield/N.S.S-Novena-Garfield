// Testing configuration and utilities for NEXUS

export const TEST_CONFIG = {
  // Test environment
  MOCK_API_DELAY: 500, // ms
  MOCK_ERROR_RATE: 0.1, // 10% error rate for testing
  
  // Test data
  SAMPLE_QUERIES: [
    'What is the latest research on CRISPR gene editing?',
    'How do molecular dynamics simulations work?',
    'Explain bacterial genome assembly methods',
    'What are the best practices for protein folding prediction?',
  ],
  
  SAMPLE_CHAT_MESSAGES: [
    'Hello, can you help me with my research?',
    'I need assistance with data analysis',
    'What tools are available for bioinformatics?',
    'How do I interpret these results?',
  ],
  
  // Mock system status
  MOCK_SYSTEMS: [
    {
      id: 'dashboard',
      name: 'Dashboard',
      status: 'online' as const,
      uptime: 99.9,
      lastCheck: new Date(),
      description: 'System overview and monitoring',
    },
    {
      id: 'rag',
      name: 'RAG System',
      status: 'online' as const,
      uptime: 98.5,
      lastCheck: new Date(),
      description: 'AI-powered document search',
    },
    {
      id: 'changlee',
      name: 'Changlee Assistant',
      status: 'online' as const,
      uptime: 97.2,
      lastCheck: new Date(),
      description: 'AI desktop assistant',
    },
    {
      id: 'chronicle',
      name: 'Chronicle',
      status: 'offline' as const,
      uptime: 0,
      lastCheck: new Date(),
      description: 'Research documentation',
    },
    {
      id: 'genome',
      name: 'Genome Jigsaw',
      status: 'online' as const,
      uptime: 95.8,
      lastCheck: new Date(),
      description: 'Genome analysis pipeline',
    },
    {
      id: 'molecular',
      name: 'Molecular Simulation',
      status: 'online' as const,
      uptime: 94.3,
      lastCheck: new Date(),
      description: 'MD simulation toolkit',
    },
  ],
};

// Test utilities
export class TestUtils {
  static async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  static randomChoice<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }
  
  static randomBoolean(probability: number = 0.5): boolean {
    return Math.random() < probability;
  }
  
  static generateMockId(): string {
    return `mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  static simulateNetworkError(): boolean {
    return Math.random() < TEST_CONFIG.MOCK_ERROR_RATE;
  }
  
  static createMockResponse<T>(data: T, success: boolean = true): {
    success: boolean;
    data?: T;
    error?: string;
    timestamp: string;
  } {
    return {
      success,
      data: success ? data : undefined,
      error: success ? undefined : 'Mock network error',
      timestamp: new Date().toISOString(),
    };
  }
}

// Mock data generators
export class MockDataGenerator {
  static generateChatMessage(role: 'user' | 'assistant', content?: string) {
    return {
      id: TestUtils.generateMockId(),
      role,
      content: content || TestUtils.randomChoice(TEST_CONFIG.SAMPLE_CHAT_MESSAGES),
      timestamp: new Date().toISOString(),
    };
  }
  
  static generateRAGResponse(query: string) {
    return {
      answer: `Based on your query "${query}", here's a comprehensive analysis with detailed insights and recommendations from our knowledge base.`,
      confidence: 0.8 + Math.random() * 0.2, // 80-100%
      sources: [
        {
          title: 'Research Paper: Advanced Methods',
          content: 'Detailed methodology and findings...',
          relevance: 0.9 + Math.random() * 0.1,
          url: 'https://example.com/paper1',
        },
        {
          title: 'Database Entry: Related Studies',
          content: 'Comprehensive database information...',
          relevance: 0.8 + Math.random() * 0.2,
        },
      ],
      processingTime: 0.5 + Math.random() * 2, // 0.5-2.5 seconds
    };
  }
  
  static generateSystemMetrics() {
    return {
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100,
      network: Math.random() * 100,
      uptime: Math.random() * 100,
    };
  }
}

// Integration test helpers
export class IntegrationTestHelper {
  static async testSystemFlow(steps: Array<() => Promise<void>>): Promise<boolean> {
    try {
      for (const step of steps) {
        await step();
        await TestUtils.delay(100); // Small delay between steps
      }
      return true;
    } catch (error) {
      console.error('Integration test failed:', error);
      return false;
    }
  }
  
  static async testAPIEndpoint(
    endpoint: () => Promise<any>,
    expectedFields: string[]
  ): Promise<boolean> {
    try {
      const response = await endpoint();
      
      if (!response.success) {
        throw new Error(`API call failed: ${response.error}`);
      }
      
      for (const field of expectedFields) {
        if (!(field in response.data)) {
          throw new Error(`Missing field: ${field}`);
        }
      }
      
      return true;
    } catch (error) {
      console.error('API test failed:', error);
      return false;
    }
  }
  
  static async testUserInteraction(
    action: () => Promise<void>,
    validation: () => boolean
  ): Promise<boolean> {
    try {
      await action();
      await TestUtils.delay(500); // Wait for UI updates
      return validation();
    } catch (error) {
      console.error('User interaction test failed:', error);
      return false;
    }
  }
}

// Performance test utilities
export class PerformanceTestHelper {
  static async measureRenderTime(component: () => void): Promise<number> {
    const start = performance.now();
    component();
    const end = performance.now();
    return end - start;
  }
  
  static async measureAPIResponseTime(apiCall: () => Promise<any>): Promise<number> {
    const start = performance.now();
    await apiCall();
    const end = performance.now();
    return end - start;
  }
  
  static async stressTest(
    operation: () => Promise<void>,
    iterations: number = 100
  ): Promise<{ success: number; failed: number; avgTime: number }> {
    const results = { success: 0, failed: 0, avgTime: 0 };
    const times: number[] = [];
    
    for (let i = 0; i < iterations; i++) {
      try {
        const start = performance.now();
        await operation();
        const end = performance.now();
        
        times.push(end - start);
        results.success++;
      } catch (error) {
        results.failed++;
      }
    }
    
    results.avgTime = times.reduce((sum, time) => sum + time, 0) / times.length;
    return results;
  }
}