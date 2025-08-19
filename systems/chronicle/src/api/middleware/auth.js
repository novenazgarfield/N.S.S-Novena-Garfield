const { createModuleLogger } = require('../../shared/logger');
const config = require('../../shared/config');

const logger = createModuleLogger('auth-middleware');

/**
 * API密钥认证中间件
 */
function apiKeyAuth(req, res, next) {
  // 如果未启用API密钥认证，直接通过
  if (!config.security.apiKeyRequired) {
    return next();
  }

  const apiKey = req.headers['x-api-key'] || req.query.api_key;

  if (!apiKey) {
    logger.warn('API request without API key', { 
      ip: req.ip, 
      path: req.path,
      userAgent: req.get('User-Agent')
    });
    
    return res.status(401).json({
      error: 'API key required',
      message: 'Please provide a valid API key in the X-API-Key header or api_key query parameter'
    });
  }

  if (apiKey !== config.security.apiKey) {
    logger.warn('API request with invalid API key', { 
      ip: req.ip, 
      path: req.path,
      providedKey: apiKey.substring(0, 8) + '...',
      userAgent: req.get('User-Agent')
    });
    
    return res.status(401).json({
      error: 'Invalid API key',
      message: 'The provided API key is not valid'
    });
  }

  logger.debug('API key authentication successful', { 
    ip: req.ip, 
    path: req.path 
  });

  next();
}

/**
 * 基本认证中间件（用于管理接口）
 */
function basicAuth(req, res, next) {
  const auth = req.headers.authorization;

  if (!auth || !auth.startsWith('Basic ')) {
    res.set('WWW-Authenticate', 'Basic realm="Chronicle Admin"');
    return res.status(401).json({
      error: 'Authentication required',
      message: 'Please provide basic authentication credentials'
    });
  }

  try {
    const credentials = Buffer.from(auth.slice(6), 'base64').toString('utf-8');
    const [username, password] = credentials.split(':');

    // 简单的硬编码认证（生产环境应使用更安全的方式）
    const validUsername = process.env.ADMIN_USERNAME || 'admin';
    const validPassword = process.env.ADMIN_PASSWORD || 'chronicle123';

    if (username !== validUsername || password !== validPassword) {
      logger.warn('Failed basic authentication attempt', { 
        ip: req.ip, 
        username,
        userAgent: req.get('User-Agent')
      });
      
      return res.status(401).json({
        error: 'Invalid credentials',
        message: 'Username or password is incorrect'
      });
    }

    logger.debug('Basic authentication successful', { 
      ip: req.ip, 
      username 
    });

    req.user = { username };
    next();

  } catch (error) {
    logger.error('Basic authentication error', { 
      error: error.message,
      ip: req.ip
    });
    
    return res.status(400).json({
      error: 'Invalid authentication format',
      message: 'Please provide valid basic authentication credentials'
    });
  }
}

/**
 * 可选认证中间件
 */
function optionalAuth(req, res, next) {
  if (!config.security.apiKeyRequired) {
    return next();
  }

  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  if (apiKey && apiKey === config.security.apiKey) {
    req.authenticated = true;
    logger.debug('Optional authentication successful', { ip: req.ip });
  } else {
    req.authenticated = false;
    logger.debug('Optional authentication skipped', { ip: req.ip });
  }

  next();
}

/**
 * 角色检查中间件
 */
function requireRole(role) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'Please authenticate first'
      });
    }

    // 简单的角色检查（可以扩展为更复杂的权限系统）
    const userRole = req.user.role || 'user';
    const allowedRoles = Array.isArray(role) ? role : [role];

    if (!allowedRoles.includes(userRole) && userRole !== 'admin') {
      logger.warn('Access denied - insufficient permissions', {
        ip: req.ip,
        user: req.user.username,
        requiredRole: role,
        userRole
      });

      return res.status(403).json({
        error: 'Insufficient permissions',
        message: `This endpoint requires ${Array.isArray(role) ? role.join(' or ') : role} role`
      });
    }

    next();
  };
}

/**
 * IP白名单中间件
 */
function ipWhitelist(allowedIPs = []) {
  return (req, res, next) => {
    if (allowedIPs.length === 0) {
      return next();
    }

    const clientIP = req.ip || req.connection.remoteAddress;
    
    if (!allowedIPs.includes(clientIP) && !allowedIPs.includes('127.0.0.1')) {
      logger.warn('Access denied - IP not in whitelist', {
        ip: clientIP,
        allowedIPs,
        path: req.path
      });

      return res.status(403).json({
        error: 'Access denied',
        message: 'Your IP address is not authorized to access this service'
      });
    }

    next();
  };
}

/**
 * 请求限制中间件
 */
function requestLimit(maxRequests = 100, windowMs = 15 * 60 * 1000) {
  const requests = new Map();

  return (req, res, next) => {
    const clientIP = req.ip || req.connection.remoteAddress;
    const now = Date.now();
    const windowStart = now - windowMs;

    // 清理过期记录
    if (requests.has(clientIP)) {
      const clientRequests = requests.get(clientIP).filter(time => time > windowStart);
      requests.set(clientIP, clientRequests);
    } else {
      requests.set(clientIP, []);
    }

    const clientRequests = requests.get(clientIP);

    if (clientRequests.length >= maxRequests) {
      logger.warn('Rate limit exceeded', {
        ip: clientIP,
        requests: clientRequests.length,
        maxRequests,
        windowMs
      });

      return res.status(429).json({
        error: 'Rate limit exceeded',
        message: `Too many requests. Maximum ${maxRequests} requests per ${windowMs / 1000} seconds allowed.`,
        retryAfter: Math.ceil(windowMs / 1000)
      });
    }

    clientRequests.push(now);
    requests.set(clientIP, clientRequests);

    next();
  };
}

/**
 * 审计日志中间件
 */
function auditLog(req, res, next) {
  const startTime = Date.now();

  // 记录请求开始
  logger.audit('API request started', {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    authenticated: !!req.user,
    user: req.user?.username
  });

  // 监听响应结束
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    
    logger.audit('API request completed', {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration,
      ip: req.ip,
      user: req.user?.username
    });
  });

  next();
}

module.exports = {
  apiKeyAuth,
  basicAuth,
  optionalAuth,
  requireRole,
  ipWhitelist,
  requestLimit,
  auditLog
};