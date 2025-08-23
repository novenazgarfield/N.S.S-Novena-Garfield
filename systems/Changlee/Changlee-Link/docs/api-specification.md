# Changlee-Link API 接口规范

## 🌐 通信协议概览

Changlee-Link 采用三层通信架构：
1. **智能手表 ↔ 智能手机**：平台原生通信协议
2. **智能手机 ↔ NEXUS主机**：WebSocket + HTTP RESTful API
3. **数据同步**：实时推送 + 定时同步混合模式

## 📱 平台间通信协议

### Apple Watch ↔ iPhone (WatchConnectivity)

#### 1. 即时消息 (Interactive Messages)
```swift
// 发送即时指令
let message = [
    "action": "execute_command",
    "system": "nexus_remote",
    "command": "power_on",
    "target": "workstation_01",
    "timestamp": Date().timeIntervalSince1970
]

session.sendMessage(message, replyHandler: { reply in
    // 处理NEXUS主机响应
    let status = reply["status"] as? String
    let result = reply["result"] as? [String: Any]
}) { error in
    // 错误处理
}
```

#### 2. 应用上下文同步 (Application Context)
```swift
// 同步系统状态
let context = [
    "nexus_status": [
        "online_systems": 5,
        "offline_systems": 1,
        "restricted_systems": 3,
        "last_update": Date().timeIntervalSince1970
    ],
    "user_health": [
        "heart_rate": 72,
        "stress_level": "low",
        "focus_score": 85
    ]
]

try session.updateApplicationContext(context)
```

### Wear OS ↔ Android (Wearable Data Layer)

#### 1. 消息传递 (Message API)
```kotlin
// 发送RPC调用
val message = mapOf(
    "action" to "execute_command",
    "system" to "nexus_remote",
    "command" to "power_on",
    "target" to "workstation_01",
    "timestamp" to System.currentTimeMillis()
)

Wearable.getMessageClient(context).sendMessage(
    nodeId,
    "/nexus/command",
    message.toByteArray()
).addOnSuccessListener { messageId ->
    // 消息发送成功
}
```

#### 2. 数据同步 (Data API)
```kotlin
// 同步状态数据
val dataMap = DataMap().apply {
    putInt("online_systems", 5)
    putInt("offline_systems", 1)
    putInt("restricted_systems", 3)
    putLong("last_update", System.currentTimeMillis())
}

val request = PutDataMapRequest.create("/nexus/status").apply {
    dataMap = dataMap
}

Wearable.getDataClient(context).putDataItem(request.asPutDataRequest())
```

### HarmonyOS 分布式通信

#### 1. 远程过程调用 (RPC)
```typescript
// 调用手机端服务
const result = await RemoteProcedureCall.invoke(
    phoneDeviceId,
    'executeNexusCommand',
    {
        action: 'execute_command',
        system: 'nexus_remote',
        command: 'power_on',
        target: 'workstation_01'
    }
);
```

#### 2. 分布式数据管理
```typescript
// 同步分布式数据
const distributedData = {
    nexus_status: {
        online_systems: 5,
        offline_systems: 1,
        restricted_systems: 3
    }
};

await DistributedDataManager.putData('nexus_status', distributedData);
```

## 🔗 NEXUS主机通信协议

### WebSocket 实时通信

#### 连接建立
```javascript
const ws = new WebSocket('wss://nexus-host:8443/ws');

ws.onopen = function(event) {
    // 发送认证信息
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your-auth-token',
        device: 'changlee-link-mobile'
    }));
};
```

#### 消息格式规范
```json
{
    "id": "unique-message-id",
    "type": "command|status|notification|response",
    "timestamp": 1692518400000,
    "source": "changlee-link",
    "target": "nexus-core",
    "payload": {
        // 具体数据内容
    }
}
```

### HTTP RESTful API

#### 基础端点
```
Base URL: https://nexus-host:8443/api/v1
```

#### 1. 系统状态查询
```http
GET /systems/status
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "online_systems": [
            {
                "id": "nexus_remote",
                "name": "NEXUS Remote Control",
                "status": "online",
                "last_heartbeat": "2025-08-20T14:30:00Z"
            }
        ],
        "offline_systems": [...],
        "restricted_systems": [...]
    }
}
```

#### 2. 执行远程命令
```http
POST /systems/{system_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
    "command": "power_on",
    "target": "workstation_01",
    "parameters": {
        "force": false,
        "timeout": 30
    }
}

Response:
{
    "success": true,
    "execution_id": "exec-12345",
    "status": "executing",
    "estimated_duration": 15
}
```

#### 3. 健康数据上传
```http
POST /health/data
Authorization: Bearer <token>
Content-Type: application/json

{
    "device_id": "apple-watch-series-8",
    "timestamp": "2025-08-20T14:30:00Z",
    "metrics": {
        "heart_rate": 72,
        "blood_oxygen": 98,
        "stress_level": 0.2,
        "activity_level": "moderate"
    }
}
```

## 📊 数据模型定义

### 系统状态模型
```typescript
interface SystemStatus {
    id: string;
    name: string;
    status: 'online' | 'offline' | 'restricted' | 'error';
    last_heartbeat: string;
    metrics?: {
        cpu_usage?: number;
        memory_usage?: number;
        response_time?: number;
    };
    capabilities: string[];
}
```

### 用户健康模型
```typescript
interface HealthMetrics {
    device_id: string;
    timestamp: string;
    heart_rate?: number;
    blood_oxygen?: number;
    stress_level?: number; // 0-1 范围
    activity_level?: 'low' | 'moderate' | 'high';
    sleep_quality?: number; // 0-100 范围
    focus_score?: number; // 0-100 范围
}
```

### 命令执行模型
```typescript
interface CommandExecution {
    id: string;
    system_id: string;
    command: string;
    target?: string;
    parameters: Record<string, any>;
    status: 'pending' | 'executing' | 'completed' | 'failed';
    created_at: string;
    completed_at?: string;
    result?: any;
    error?: string;
}
```

## 🔔 通知推送协议

### 实时通知格式
```json
{
    "type": "notification",
    "priority": "high|medium|low",
    "category": "system|health|security|info",
    "title": "系统告警",
    "message": "服务器CPU使用率过高 (85%)",
    "actions": [
        {
            "id": "view_details",
            "label": "查看详情",
            "type": "navigation",
            "target": "/systems/monitoring"
        },
        {
            "id": "ignore",
            "label": "忽略",
            "type": "dismiss"
        }
    ],
    "metadata": {
        "system_id": "nexus_remote",
        "metric": "cpu_usage",
        "value": 85,
        "threshold": 80
    }
}
```

### 智能通知规则
```typescript
interface NotificationRule {
    id: string;
    name: string;
    conditions: {
        system_id?: string;
        metric?: string;
        operator: 'gt' | 'lt' | 'eq' | 'ne';
        value: number | string;
    }[];
    actions: {
        type: 'push' | 'email' | 'sms';
        template: string;
        priority: 'high' | 'medium' | 'low';
    }[];
    schedule?: {
        enabled: boolean;
        quiet_hours: {
            start: string; // "22:00"
            end: string;   // "08:00"
        };
    };
}
```

## 🔐 安全认证协议

### JWT Token 格式
```json
{
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "sub": "changlee-link-user",
        "device_id": "apple-watch-12345",
        "permissions": [
            "system:read",
            "system:execute",
            "health:write"
        ],
        "exp": 1692604800,
        "iat": 1692518400
    }
}
```

### API 密钥管理
```http
POST /auth/api-keys
Authorization: Bearer <admin-token>

{
    "name": "Changlee-Link Apple Watch",
    "permissions": ["system:read", "system:execute"],
    "expires_at": "2025-12-31T23:59:59Z"
}

Response:
{
    "api_key": "cl_ak_1234567890abcdef",
    "secret": "cl_sk_abcdef1234567890",
    "expires_at": "2025-12-31T23:59:59Z"
}
```

## 📈 性能优化建议

### 1. 数据压缩
- 使用 gzip 压缩 HTTP 响应
- WebSocket 消息使用 MessagePack 序列化
- 图片资源使用 WebP 格式

### 2. 缓存策略
- 系统状态缓存 5 秒
- 用户配置缓存 1 小时
- 静态资源缓存 24 小时

### 3. 批量操作
- 健康数据批量上传（每分钟一次）
- 日志数据批量同步（每5分钟一次）
- 状态更新合并发送

### 4. 错误重试机制
```typescript
const retryConfig = {
    maxRetries: 3,
    backoffMultiplier: 2,
    initialDelay: 1000, // 1秒
    maxDelay: 10000     // 10秒
};
```

---

**API版本**：v1.0  
**最后更新**：2025-08-20  
**兼容性**：向后兼容，新版本通过版本号区分