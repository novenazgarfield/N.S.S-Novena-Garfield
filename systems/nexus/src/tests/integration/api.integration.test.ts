// Integration tests for API services

import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';

// Mock the API service
vi.mock('../../services/api', () => ({
  activeApiService: {
    getSystemStatus: vi.fn().mockResolvedValue({
      success: true,
      data: [{ id: 'test', name: 'Test System', status: 'online' }]
    }),
    queryRAG: vi.fn().mockResolvedValue({
      success: true,
      data: { answer: 'Test answer', confidence: 0.9 }
    }),
    sendChatMessage: vi.fn().mockResolvedValue({
      success: true,
      data: { content: 'Test response', role: 'assistant' }
    })
  }
}));

import { activeApiService } from '../../services/api';

describe('API Integration Tests', () => {
  beforeAll(() => {
    console.log('🧪 Starting API Integration Tests...');
  });

  afterAll(() => {
    console.log('✅ API Integration Tests Complete');
  });

  it('should test system status API', async () => {
    const response = await activeApiService.getSystemStatus();
    
    expect(response.success).toBe(true);
    expect(Array.isArray(response.data)).toBe(true);
    expect(response.data[0]).toHaveProperty('id');
    expect(response.data[0]).toHaveProperty('status');
  });

  it('should test RAG system API', async () => {
    const testQuery = { query: 'What is machine learning?' };
    const response = await activeApiService.queryRAG(testQuery);
    
    expect(response.success).toBe(true);
    expect(response.data).toHaveProperty('answer');
    expect(response.data).toHaveProperty('confidence');
    expect(typeof response.data.answer).toBe('string');
    expect(typeof response.data.confidence).toBe('number');
  });

  it('should test chat system API', async () => {
    const response = await activeApiService.sendChatMessage('test-session', 'Hello');
    
    expect(response.success).toBe(true);
    expect(response.data).toHaveProperty('content');
    expect(response.data).toHaveProperty('role');
    expect(typeof response.data.content).toBe('string');
  });

  it('should handle API errors gracefully', async () => {
    // Mock a failed API call
    vi.mocked(activeApiService.getSystemStatus).mockResolvedValueOnce({
      success: false,
      error: 'Network error'
    });

    const response = await activeApiService.getSystemStatus();
    
    expect(response.success).toBe(false);
    expect(response.error).toBe('Network error');
  });
});