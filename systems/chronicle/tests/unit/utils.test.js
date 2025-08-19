const {
  generateId,
  generateSessionId,
  safeJsonParse,
  safeJsonStringify,
  formatBytes,
  formatDuration,
  truncateText,
  cleanText,
  extractErrorInfo,
  calculateSimilarity,
  retry,
  withTimeout
} = require('../../src/shared/utils');

describe('Utils', () => {
  describe('generateId', () => {
    test('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
      expect(id1).toMatch(/^[a-z0-9_]+$/);
    });

    test('should generate IDs with prefix', () => {
      const id = generateId('test');
      expect(id).toMatch(/^test_[a-z0-9_]+$/);
    });
  });

  describe('generateSessionId', () => {
    test('should generate session IDs with correct prefix', () => {
      const sessionId = generateSessionId();
      expect(sessionId).toMatch(/^session_[a-z0-9_]+$/);
    });
  });

  describe('safeJsonParse', () => {
    test('should parse valid JSON', () => {
      const result = safeJsonParse('{"key": "value"}');
      expect(result).toEqual({ key: 'value' });
    });

    test('should return default value for invalid JSON', () => {
      const result = safeJsonParse('invalid json', { default: true });
      expect(result).toEqual({ default: true });
    });

    test('should return null for invalid JSON without default', () => {
      const result = safeJsonParse('invalid json');
      expect(result).toBeNull();
    });
  });

  describe('safeJsonStringify', () => {
    test('should stringify valid objects', () => {
      const result = safeJsonStringify({ key: 'value' });
      expect(result).toBe('{"key":"value"}');
    });

    test('should handle circular references', () => {
      const obj = { key: 'value' };
      obj.circular = obj;
      const result = safeJsonStringify(obj);
      expect(result).toBe('{}');
    });
  });

  describe('formatBytes', () => {
    test('should format bytes correctly', () => {
      expect(formatBytes(0)).toBe('0 Bytes');
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1024 * 1024)).toBe('1 MB');
      expect(formatBytes(1024 * 1024 * 1024)).toBe('1 GB');
    });

    test('should handle decimal places', () => {
      expect(formatBytes(1536, 1)).toBe('1.5 KB');
      expect(formatBytes(1536, 0)).toBe('2 KB');
    });
  });

  describe('formatDuration', () => {
    test('should format durations correctly', () => {
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(1500)).toBe('1.5s');
      expect(formatDuration(65000)).toBe('1.1m');
      expect(formatDuration(3665000)).toBe('1.0h');
    });
  });

  describe('truncateText', () => {
    test('should truncate long text', () => {
      const text = 'This is a very long text that should be truncated';
      const result = truncateText(text, 20);
      expect(result).toBe('This is a very lo...');
      expect(result.length).toBe(20);
    });

    test('should not truncate short text', () => {
      const text = 'Short text';
      const result = truncateText(text, 20);
      expect(result).toBe(text);
    });

    test('should use custom suffix', () => {
      const text = 'This is a long text';
      const result = truncateText(text, 10, ' [more]');
      expect(result).toBe('Thi [more]');
    });
  });

  describe('cleanText', () => {
    test('should remove ANSI escape sequences', () => {
      const text = '\x1b[31mRed text\x1b[0m';
      const result = cleanText(text);
      expect(result).toBe('Red text');
    });

    test('should trim whitespace', () => {
      const text = '  \n  Text with whitespace  \n  ';
      const result = cleanText(text);
      expect(result).toBe('Text with whitespace');
    });
  });

  describe('extractErrorInfo', () => {
    test('should extract error messages', () => {
      const text = `
        Error: Something went wrong
        Exception: Another error occurred
        Failed: Operation failed
      `;
      const errors = extractErrorInfo(text);
      expect(errors).toContain('Something went wrong');
      expect(errors).toContain('Another error occurred');
      expect(errors).toContain('Operation failed');
    });

    test('should return empty array for no errors', () => {
      const text = 'Everything is working fine';
      const errors = extractErrorInfo(text);
      expect(errors).toEqual([]);
    });
  });

  describe('calculateSimilarity', () => {
    test('should calculate similarity correctly', () => {
      expect(calculateSimilarity('hello', 'hello')).toBe(1);
      expect(calculateSimilarity('hello', 'world')).toBeLessThan(0.5);
      expect(calculateSimilarity('', '')).toBe(1);
    });

    test('should handle different length strings', () => {
      const similarity = calculateSimilarity('hello', 'hello world');
      expect(similarity).toBeGreaterThan(0.4);
      expect(similarity).toBeLessThan(1);
    });
  });

  describe('retry', () => {
    test('should retry failed operations', async () => {
      let attempts = 0;
      const operation = jest.fn(() => {
        attempts++;
        if (attempts < 3) {
          throw new Error('Operation failed');
        }
        return 'success';
      });

      const result = await retry(operation, 3, 10);
      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(3);
    });

    test('should throw error after max attempts', async () => {
      const operation = jest.fn(() => {
        throw new Error('Always fails');
      });

      await expect(retry(operation, 2, 10)).rejects.toThrow('Always fails');
      expect(operation).toHaveBeenCalledTimes(2);
    });
  });

  describe('withTimeout', () => {
    test('should resolve if promise completes in time', async () => {
      const promise = new Promise(resolve => setTimeout(() => resolve('success'), 50));
      const result = await withTimeout(promise, 100);
      expect(result).toBe('success');
    });

    test('should reject if promise times out', async () => {
      const promise = new Promise(resolve => setTimeout(() => resolve('success'), 200));
      await expect(withTimeout(promise, 100)).rejects.toThrow('Operation timed out');
    });
  });
});