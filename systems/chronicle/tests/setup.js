// Jest setup file
const path = require('path');

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.DB_PATH = path.join(__dirname, '../data/test.db');
process.env.LOG_LEVEL = 'error';
process.env.API_KEY_REQUIRED = 'false';
process.env.AI_PROVIDER = 'mock';

// Mock console methods in tests
global.console = {
  ...console,
  // Uncomment to suppress console output in tests
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
};

// Global test timeout
jest.setTimeout(30000);

// Clean up after tests
afterAll(async () => {
  // Clean up test database
  const fs = require('fs');
  const testDbPath = process.env.DB_PATH;
  if (fs.existsSync(testDbPath)) {
    fs.unlinkSync(testDbPath);
  }
});