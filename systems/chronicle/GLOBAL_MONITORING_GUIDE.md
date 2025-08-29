# 🌍 Chronicle全系统监控使用指南

## 📋 概述

Chronicle全系统监控是一个强大的监控和自动修复系统，能够：

- 🔍 监控 `/workspace/systems` 下的所有项目
- 📋 监控本机系统日志和资源使用情况
- 🔗 进行跨项目故障关联分析
- 🛠️ 自动修复常见问题
- 🏥 与Genesis中央医院系统集成

## 🚀 快速开始

### 1. 启动全系统监控

```bash
# 启动完整的监控系统（API + 监控）
node scripts/start-global-monitor.js

# 仅启动API服务器
node scripts/start-global-monitor.js --api-only

# 仅启动监控（无API）
node scripts/start-global-monitor.js --monitor-only

# 指定端口
node scripts/start-global-monitor.js --port 8080

# 详细日志输出
node scripts/start-global-monitor.js --verbose

# 试运行（检查环境）
node scripts/start-global-monitor.js --dry-run
```

### 2. 使用API接口

#### 启动监控
```bash
curl -X POST http://localhost:3000/api/global/start \
  -H "X-API-Key: your-api-key"
```

#### 查看监控状态
```bash
curl http://localhost:3000/api/global/status \
  -H "X-API-Key: your-api-key"
```

#### 获取项目列表
```bash
curl http://localhost:3000/api/global/projects \
  -H "X-API-Key: your-api-key"
```

#### 查看系统健康状态
```bash
curl http://localhost:3000/api/global/system-health \
  -H "X-API-Key: your-api-key"
```

## 🔍 监控功能详解

### 📁 项目监控

Chronicle会自动发现并监控 `/workspace/systems` 下的所有项目：

#### 支持的项目类型
- **Node.js项目**: 检测 `package.json`，支持Express、React、Vue等框架
- **Python项目**: 检测 `requirements.txt`，支持Streamlit、Flask、Django等框架

#### 监控内容
- 📝 **关键文件变化**: `package.json`, `requirements.txt`, `main.py`, `index.js` 等
- 📋 **日志文件监控**: 自动监控 `logs/` 和 `log/` 目录
- 🏥 **健康检查**: 定期检查项目服务状态
- 🔄 **进程监控**: 监控项目相关进程

#### 自动修复功能
- 🔧 **文件恢复**: 关键文件被删除时自动恢复
- 🔄 **服务重启**: 健康检查失败时自动重启
- 🧹 **资源清理**: 内存泄漏时自动清理

### 🖥️ 系统级监控

#### 系统日志监控
- **Linux**: `/var/log/syslog`, `/var/log/messages`, `/var/log/kern.log`
- **macOS**: `/var/log/system.log`, `/var/log/kernel.log`
- **Windows**: 事件日志（计划中）

#### 资源监控
- 💾 **内存使用率**: 阈值 85%
- 💿 **磁盘使用率**: 阈值 90%
- ⚡ **CPU使用率**: 阈值 80%

#### 进程和服务监控
- 🔄 **关键进程**: `sshd`, `systemd`, `networkd`
- 🛠️ **系统服务**: `ssh`, `networking`, `cron`

### 🔗 跨项目关联分析

Chronicle能够分析多个项目之间的故障关联：

#### 故障模式识别
- **相似错误**: 多个项目出现相同类型错误
- **连锁故障**: 一个项目故障导致其他项目故障
- **资源竞争**: 多个项目争夺系统资源

#### 智能修复策略
- 🔄 **批量重启**: 按依赖顺序重启相关项目
- 🧹 **资源优化**: 统一清理系统资源
- 🔧 **根因修复**: 修复共同的根本原因

## 🏥 与Genesis中央医院集成

Chronicle全系统监控与Genesis中央医院系统无缝集成：

### 故障上报
```javascript
// 项目中的错误会自动上报到Chronicle
try {
  // 你的代码
} catch (error) {
  // Chronicle会自动捕获并记录这个错误
  console.error('Error occurred:', error);
}
```

### 治疗请求
```bash
# 请求治疗方案
curl -X POST http://localhost:3000/api/request_healing \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "source": "PROJECT",
    "function_name": "process_data",
    "error_type": "ConnectionError",
    "error_message": "Database connection failed"
  }'
```

### 免疫系统
```bash
# 建立免疫
curl -X POST http://localhost:3000/api/build_immunity \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "source": "PROJECT",
    "function_name": "connect_database",
    "error_type": "ConnectionError",
    "prevention_strategy": "connection_pool"
  }'
```

## 📊 API接口详解

### 🌍 全系统监控API

#### POST /api/global/start
启动全系统监控

**响应示例**:
```json
{
  "success": true,
  "message": "Chronicle全系统监控已启动",
  "data": {
    "monitored_projects": ["rag-system", "nexus", "changlee"],
    "system_monitors": ["resource_monitor", "system_log_syslog"],
    "monitoring_config": {
      "projectsPath": "/workspace/systems",
      "monitorInterval": 30000,
      "resourceThresholds": {
        "cpu": 80,
        "memory": 85,
        "disk": 90
      }
    }
  }
}
```

#### GET /api/global/status
获取监控状态

**响应示例**:
```json
{
  "success": true,
  "message": "全系统监控状态",
  "data": {
    "monitoring_status": {
      "isMonitoring": true,
      "monitoredProjects": ["rag-system", "nexus", "changlee"],
      "projectWatchers": ["rag-system", "nexus"],
      "systemWatchers": ["resource_monitor", "cross_project_analysis"],
      "systemInfo": {
        "platform": "linux",
        "arch": "x64",
        "totalMemory": 8589934592,
        "freeMemory": 2147483648,
        "uptime": 86400
      }
    }
  }
}
```

#### GET /api/global/projects
获取项目列表

**响应示例**:
```json
{
  "success": true,
  "message": "项目列表",
  "data": {
    "total_projects": 6,
    "monitored_projects": 4,
    "projects": [
      {
        "name": "rag-system",
        "type": "python",
        "language": "python",
        "framework": "streamlit",
        "path": "/workspace/systems/rag-system",
        "criticalFiles": ["requirements.txt", "main.py", "app.py"],
        "logPaths": ["/workspace/systems/rag-system/logs"],
        "healthCheckEndpoint": "http://localhost:8501/_stcore/health",
        "monitoringEnabled": true,
        "isMonitored": true
      }
    ]
  }
}
```

#### GET /api/global/system-health
获取系统健康状态

**响应示例**:
```json
{
  "success": true,
  "message": "系统健康状态",
  "data": {
    "overall_health": {
      "score": 85,
      "status": "good",
      "level": "yellow"
    },
    "system_resources": {
      "cpu": 45,
      "memory": 65,
      "disk": 78
    },
    "monitoring_status": {
      "is_monitoring": true,
      "monitored_projects": 4,
      "active_watchers": 8
    },
    "recommendations": [
      {
        "type": "disk",
        "priority": "medium",
        "message": "磁盘使用率较高，建议清理临时文件",
        "action": "cleanup_disk"
      }
    ]
  }
}
```

#### POST /api/global/project/:name/restart
重启指定项目

**请求示例**:
```bash
curl -X POST http://localhost:3000/api/global/project/rag-system/restart \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"force": false}'
```

**响应示例**:
```json
{
  "success": true,
  "message": "项目 rag-system 重启成功",
  "data": {
    "projectName": "rag-system",
    "projectType": "python",
    "framework": "streamlit",
    "restartTime": "2025-08-29T10:30:00.000Z",
    "force": false
  }
}
```

#### POST /api/global/optimize-resources
优化系统资源

**请求示例**:
```bash
curl -X POST http://localhost:3000/api/global/optimize-resources \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "resourceType": "memory",
    "force": false
  }'
```

#### GET /api/global/analytics
获取监控分析数据

**响应示例**:
```json
{
  "success": true,
  "message": "监控分析数据",
  "data": {
    "time_range": "1h",
    "failure_analysis": {
      "total_failures": 12,
      "failure_by_source": {
        "PROJECT": 8,
        "SYSTEM": 3,
        "CHRONICLE": 1
      },
      "failure_by_type": {
        "ConnectionError": 5,
        "MemoryError": 3,
        "FileNotFound": 4
      }
    },
    "healing_analysis": {
      "total_healing_attempts": 10,
      "successful_healings": 8,
      "healing_success_rate": 0.8
    },
    "trends": {
      "failure_trend": "stable",
      "healing_trend": "good",
      "system_trend": "stable"
    }
  }
}
```

## 🔧 配置说明

### 配置文件位置
- 主配置: `config/global-monitor.json`
- 日志配置: `src/shared/config.js`

### 主要配置项

#### 监控配置
```json
{
  "globalMonitoring": {
    "enabled": true,
    "projectsPath": "/workspace/systems",
    "monitorInterval": 30000,
    "resourceThresholds": {
      "cpu": 80,
      "memory": 85,
      "disk": 90
    }
  }
}
```

#### 自动修复配置
```json
{
  "autoRecovery": {
    "enabled": true,
    "maxRetries": 3,
    "retryDelay": 5000,
    "strategies": {
      "file_recovery": {
        "enabled": true,
        "backupPaths": [".backup", ".git"],
        "templateGeneration": true
      },
      "process_restart": {
        "enabled": true,
        "gracefulTimeout": 10000,
        "forceKillTimeout": 30000
      }
    }
  }
}
```

## 🛠️ 故障排除

### 常见问题

#### 1. 监控启动失败
```bash
# 检查权限
sudo chown -R $USER:$USER /workspace/systems/chronicle

# 检查依赖
npm install

# 检查系统日志权限
sudo chmod +r /var/log/syslog
```

#### 2. 项目监控失效
```bash
# 检查项目路径
ls -la /workspace/systems/

# 检查项目配置文件
cat /workspace/systems/your-project/package.json
```

#### 3. 系统资源监控异常
```bash
# 检查系统命令可用性
which df
which free
which ps

# 检查权限
sudo -l
```

### 日志查看

#### Chronicle日志
```bash
# 查看主日志
tail -f logs/chronicle.log

# 查看错误日志
tail -f logs/error.log

# 查看全系统监控日志
tail -f logs/global-monitor.log
```

#### 系统日志
```bash
# 查看系统日志
sudo tail -f /var/log/syslog

# 查看内核日志
sudo tail -f /var/log/kern.log
```

## 🚀 高级用法

### 1. 自定义项目监控

```javascript
// 在项目中添加Chronicle集成
const chronicle = require('@chronicle/client');

// 自定义健康检查
chronicle.healthCheck('/custom-health', () => {
  return {
    status: 'healthy',
    timestamp: new Date(),
    custom_metrics: {
      active_connections: getActiveConnections(),
      queue_size: getQueueSize()
    }
  };
});

// 自定义错误处理
chronicle.onError((error, context) => {
  // 自定义错误处理逻辑
  console.log('Chronicle captured error:', error);
});
```

### 2. 扩展监控规则

```javascript
// 添加自定义监控规则
const customRules = {
  'high_error_rate': {
    condition: (metrics) => metrics.errorRate > 0.1,
    action: 'restart_service',
    severity: 'HIGH'
  },
  'memory_leak': {
    condition: (metrics) => metrics.memoryGrowthRate > 0.05,
    action: 'memory_cleanup',
    severity: 'MEDIUM'
  }
};

globalMonitor.addCustomRules(customRules);
```

### 3. 集成外部监控系统

```javascript
// Prometheus集成
const prometheus = require('prom-client');

const chronicleMetrics = new prometheus.Gauge({
  name: 'chronicle_system_health',
  help: 'Chronicle system health score',
  labelNames: ['component']
});

globalMonitor.on('healthUpdate', (health) => {
  chronicleMetrics.set({ component: 'overall' }, health.score);
});
```

## 📈 性能优化

### 1. 监控性能调优

```json
{
  "performance": {
    "maxConcurrentWatchers": 50,
    "fileWatcherOptions": {
      "depth": 3,
      "ignoreInitial": true
    },
    "logAnalysisOptions": {
      "maxLogLines": 100,
      "analysisTimeout": 5000
    }
  }
}
```

### 2. 资源使用优化

```bash
# 限制Chronicle进程资源使用
systemd-run --scope -p MemoryLimit=1G -p CPUQuota=50% \
  node scripts/start-global-monitor.js
```

## 🔒 安全考虑

### 1. 权限控制

```json
{
  "security": {
    "allowedPaths": [
      "/workspace/systems",
      "/var/log"
    ],
    "restrictedPaths": [
      "/etc/passwd",
      "/root"
    ],
    "allowedCommands": [
      "ps", "top", "df", "systemctl"
    ]
  }
}
```

### 2. API安全

```bash
# 生成API密钥
openssl rand -hex 32

# 设置环境变量
export CHRONICLE_API_KEY="your-secure-api-key"
```

## 📚 更多资源

- [Chronicle架构文档](./CHRONICLE_ARCHITECTURE_ANALYSIS.md)
- [Genesis中央医院API](./src/api/routes/genesis.js)
- [故障排除指南](./docs/troubleshooting.md)
- [开发者指南](./docs/development.md)

---

**🌍 Chronicle全系统监控 - 让你的整个系统都在Chronicle的守护之下！** 🛡️

**版本**: v2.0.0 Global Federation  
**更新日期**: 2025-08-29  
**作者**: N.S.S-Novena-Garfield Project