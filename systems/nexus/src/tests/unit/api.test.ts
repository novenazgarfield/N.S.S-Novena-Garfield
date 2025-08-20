// Unit tests for API services

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock ApiClient before importing RealApiService
vi.mock('../../services/apiClient', () => ({
  ApiClient: vi.fn().mockImplementation(() => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }))
}));

import { RealApiService } from '../../services/realApi';

// Mock fetch for testing
global.fetch = vi.fn();

describe('RealApiService', () => {
  let apiService: RealApiService;

  beforeEach(() => {
    apiService = new RealApiService();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getSystemStatus', () => {
    it('should return system status successfully', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ([
          {
            id: 'test-system',
            name: 'Test System',
            status: 'online',
            uptime: 99.9,
            lastCheck: new Date(),
            description: 'Test system description'
          }
        ])
      };

      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const result = await apiService.getSystemStatus();

      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data[0].name).toBe('Test System');
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const result = await apiService.getSystemStatus();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Network error');
    });
  });

  describe('authentication', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          token: 'test_token_123',
          user: { id: 1, username: 'testuser' }
        })
      };

      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const result = await apiService.login({
        username: 'testuser',
        password: 'password123'
      });

      expect(result.success).toBe(true);
      expect(result.data.token).toBe('test_token_123');
    });
  });
});