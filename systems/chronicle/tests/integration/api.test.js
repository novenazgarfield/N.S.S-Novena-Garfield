const request = require('supertest');
const path = require('path');
const fs = require('fs');
const apiServer = require('../../src/api/server');
const database = require('../../src/collector/database');

describe('API Integration Tests', () => {
  let app;
  let testSessionId;
  const testProjectPath = path.join(__dirname, '../fixtures/test-project');

  beforeAll(async () => {
    // 创建测试项目目录
    if (!fs.existsSync(testProjectPath)) {
      fs.mkdirSync(testProjectPath, { recursive: true });
      fs.writeFileSync(path.join(testProjectPath, 'test.txt'), 'Test file content');
    }

    // 初始化API服务器
    await apiServer.init();
    app = apiServer.getApp();
  });

  afterAll(async () => {
    // 清理测试数据
    if (testSessionId) {
      try {
        await database.run('DELETE FROM sessions WHERE id = ?', [testSessionId]);
      } catch (error) {
        // 忽略清理错误
      }
    }

    // 关闭服务器
    await apiServer.stop();

    // 清理测试目录
    if (fs.existsSync(testProjectPath)) {
      fs.rmSync(testProjectPath, { recursive: true, force: true });
    }
  });

  describe('Health Check', () => {
    test('GET /health should return healthy status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toMatchObject({
        status: 'healthy',
        version: '1.0.0'
      });
      expect(response.body.timestamp).toBeDefined();
      expect(response.body.uptime).toBeGreaterThanOrEqual(0);
    });
  });

  describe('API Info', () => {
    test('GET /info should return API information', async () => {
      const response = await request(app)
        .get('/info')
        .expect(200);

      expect(response.body).toMatchObject({
        name: 'Chronicle API',
        version: '1.0.0',
        description: 'AI-Driven Automated Experiment Recorder API'
      });
      expect(response.body.endpoints).toBeDefined();
    });

    test('GET /docs should return API documentation', async () => {
      const response = await request(app)
        .get('/docs')
        .expect(200);

      expect(response.body.title).toBe('Chronicle API Documentation');
      expect(response.body.endpoints).toBeDefined();
    });
  });

  describe('Sessions API', () => {
    test('POST /sessions/start should create a new session', async () => {
      const sessionData = {
        project_name: 'Test Project',
        project_path: testProjectPath,
        metadata: { test: true },
        options: {
          file_monitoring: true,
          window_monitoring: false,
          command_monitoring: false
        }
      };

      const response = await request(app)
        .post('/sessions/start')
        .send(sessionData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.sessionId).toMatch(/^session_/);
      expect(response.body.project.name).toBe(sessionData.project_name);
      expect(response.body.project.path).toBe(testProjectPath);

      testSessionId = response.body.sessionId;
    });

    test('POST /sessions/start should fail with invalid project path', async () => {
      const sessionData = {
        project_name: 'Invalid Project',
        project_path: '/nonexistent/path'
      };

      const response = await request(app)
        .post('/sessions/start')
        .send(sessionData)
        .expect(400);

      expect(response.body.error).toBe('Invalid project path');
    });

    test('GET /sessions/:sessionId should return session info', async () => {
      const response = await request(app)
        .get(`/sessions/${testSessionId}`)
        .expect(200);

      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.project.name).toBe('Test Project');
      expect(response.body.status).toBe('active');
      expect(response.body.stats).toBeDefined();
    });

    test('GET /sessions should return sessions list', async () => {
      const response = await request(app)
        .get('/sessions')
        .expect(200);

      expect(response.body.sessions).toBeInstanceOf(Array);
      expect(response.body.pagination).toBeDefined();
      expect(response.body.activeSessions).toBeGreaterThanOrEqual(1);

      // 检查我们的测试会话是否在列表中
      const testSession = response.body.sessions.find(s => s.sessionId === testSessionId);
      expect(testSession).toBeDefined();
    });

    test('GET /sessions/:sessionId/events should return session events', async () => {
      const response = await request(app)
        .get(`/sessions/${testSessionId}/events`)
        .expect(200);

      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.events).toBeInstanceOf(Array);
      expect(response.body.total).toBeGreaterThanOrEqual(0);
    });

    test('GET /sessions/:sessionId/stats should return session statistics', async () => {
      const response = await request(app)
        .get(`/sessions/${testSessionId}/stats`)
        .expect(200);

      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.basicStats).toBeDefined();
      expect(response.body.monitoringStats).toBeDefined();
    });

    test('POST /sessions/:sessionId/stop should stop the session', async () => {
      const response = await request(app)
        .post(`/sessions/${testSessionId}/stop`)
        .send({})
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.duration).toBeDefined();
    });

    test('GET /sessions/:sessionId should show stopped status', async () => {
      const response = await request(app)
        .get(`/sessions/${testSessionId}`)
        .expect(200);

      expect(response.body.status).toBe('completed');
      expect(response.body.timeRange.end).not.toBeNull();
    });
  });

  describe('Reports API', () => {
    test('GET /reports/:sessionId should generate a report', async () => {
      const response = await request(app)
        .get(`/reports/${testSessionId}`)
        .query({ type: 'summary', format: 'json' })
        .expect(200);

      expect(response.body.reportId).toMatch(/^report_/);
      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.report).toBeDefined();
      expect(response.body.report.title).toContain('Test Project');
    });

    test('GET /reports/:sessionId/raw should return raw session data', async () => {
      const response = await request(app)
        .get(`/reports/${testSessionId}/raw`)
        .expect(200);

      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.session).toBeDefined();
      expect(response.body.stats).toBeDefined();
      expect(response.body.events).toBeInstanceOf(Array);
    });

    test('GET /reports/:sessionId/summary should return session summary', async () => {
      const response = await request(app)
        .get(`/reports/${testSessionId}/summary`)
        .expect(200);

      expect(response.body.sessionId).toBe(testSessionId);
      expect(response.body.project.name).toBe('Test Project');
      expect(response.body.status).toBe('completed');
      expect(response.body.health).toBeDefined();
    });

    test('GET /reports should return reports list', async () => {
      const response = await request(app)
        .get('/reports')
        .expect(200);

      expect(response.body.reports).toBeInstanceOf(Array);
      expect(response.body.pagination).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    test('should return 404 for non-existent session', async () => {
      const response = await request(app)
        .get('/sessions/session_nonexistent')
        .expect(404);

      expect(response.body.error).toBe('Session not found');
    });

    test('should return 400 for invalid session ID format', async () => {
      const response = await request(app)
        .get('/sessions/invalid-id')
        .expect(400);

      expect(response.body.error).toBe('Invalid path parameter');
    });

    test('should return 404 for non-existent endpoint', async () => {
      const response = await request(app)
        .get('/nonexistent')
        .expect(404);

      expect(response.body.error).toBe('Not Found');
    });

    test('should validate request body', async () => {
      const response = await request(app)
        .post('/sessions/start')
        .send({ invalid: 'data' })
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toBeInstanceOf(Array);
    });
  });

  describe('Admin Routes', () => {
    test('GET /admin/status should return system status', async () => {
      const response = await request(app)
        .get('/admin/status')
        .expect(200);

      expect(response.body.system).toBeDefined();
      expect(response.body.database).toBeDefined();
      expect(response.body.monitoring).toBeDefined();
    });

    test('GET /admin/config should return configuration', async () => {
      const response = await request(app)
        .get('/admin/config')
        .expect(200);

      expect(response.body.server).toBeDefined();
      expect(response.body.monitoring).toBeDefined();
      expect(response.body.security.apiKey).toBe(null); // Should be masked
    });
  });
});