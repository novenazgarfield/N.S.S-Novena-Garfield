/**
 * Changlee-Link NEXUS 通信协议定义
 * 定义智能手表与NEXUS主机之间的通信协议和数据结构
 */

// ============================================================================
// 基础类型定义
// ============================================================================

export type MessageType = 'command' | 'status' | 'notification' | 'response' | 'heartbeat';
export type SystemStatus = 'online' | 'offline' | 'restricted' | 'error' | 'maintenance';
export type CommandStatus = 'pending' | 'executing' | 'completed' | 'failed' | 'timeout';
export type NotificationPriority = 'low' | 'medium' | 'high' | 'critical';
export type HealthMetricType = 'heart_rate' | 'blood_oxygen' | 'stress_level' | 'activity_level' | 'sleep_quality';

// ============================================================================
// 消息基础结构
// ============================================================================

export interface BaseMessage {
    id: string;                    // 唯一消息ID
    type: MessageType;             // 消息类型
    timestamp: number;             // 时间戳 (Unix timestamp)
    source: string;                // 消息源标识
    target: string;                // 目标标识
    version: string;               // 协议版本
}

export interface MessageEnvelope<T = any> extends BaseMessage {
    payload: T;                    // 消息载荷
    metadata?: Record<string, any>; // 元数据
}

// ============================================================================
// 系统相关数据结构
// ============================================================================

export interface SystemInfo {
    id: string;                    // 系统唯一标识
    name: string;                  // 系统显示名称
    description: string;           // 系统描述
    status: SystemStatus;          // 当前状态
    version: string;               // 系统版本
    last_heartbeat: number;        // 最后心跳时间
    capabilities: string[];        // 系统能力列表
    metrics?: SystemMetrics;       // 系统指标
    icon?: string;                 // 系统图标
    color?: string;                // 主题色
}

export interface SystemMetrics {
    cpu_usage?: number;            // CPU使用率 (0-100)
    memory_usage?: number;         // 内存使用率 (0-100)
    disk_usage?: number;           // 磁盘使用率 (0-100)
    network_latency?: number;      // 网络延迟 (ms)
    response_time?: number;        // 响应时间 (ms)
    error_rate?: number;           // 错误率 (0-1)
    uptime?: number;               // 运行时间 (seconds)
}

export interface SystemsStatusPayload {
    systems: SystemInfo[];         // 系统列表
    summary: {
        total: number;             // 总系统数
        online: number;            // 在线系统数
        offline: number;           // 离线系统数
        restricted: number;        // 受限系统数
        error: number;             // 错误系统数
    };
    last_updated: number;          // 最后更新时间
}

// ============================================================================
// 命令执行相关
// ============================================================================

export interface CommandRequest {
    system_id: string;             // 目标系统ID
    command: string;               // 命令名称
    target?: string;               // 命令目标 (可选)
    parameters?: Record<string, any>; // 命令参数
    timeout?: number;              // 超时时间 (seconds)
    priority?: 'low' | 'normal' | 'high'; // 优先级
}

export interface CommandResponse {
    execution_id: string;          // 执行ID
    system_id: string;             // 系统ID
    command: string;               // 命令名称
    status: CommandStatus;         // 执行状态
    result?: any;                  // 执行结果
    error?: string;                // 错误信息
    started_at: number;            // 开始时间
    completed_at?: number;         // 完成时间
    duration?: number;             // 执行时长 (ms)
}

export interface CommandStatusPayload {
    execution_id: string;          // 执行ID
    status: CommandStatus;         // 当前状态
    progress?: number;             // 进度 (0-100)
    message?: string;              // 状态消息
    estimated_remaining?: number;   // 预计剩余时间 (seconds)
}

// ============================================================================
// 健康数据相关
// ============================================================================

export interface HealthMetric {
    type: HealthMetricType;        // 指标类型
    value: number;                 // 指标值
    unit: string;                  // 单位
    timestamp: number;             // 测量时间
    device_id?: string;            // 设备ID
    accuracy?: 'low' | 'medium' | 'high'; // 准确度
}

export interface HealthDataPayload {
    user_id: string;               // 用户ID
    device_id: string;             // 设备ID
    metrics: HealthMetric[];       // 健康指标数组
    session_id?: string;           // 会话ID
    location?: {                   // 位置信息 (可选)
        latitude: number;
        longitude: number;
        accuracy: number;
    };
}

export interface HealthAnalysis {
    user_id: string;               // 用户ID
    analysis_time: number;         // 分析时间
    focus_score: number;           // 专注度评分 (0-100)
    stress_level: number;          // 压力水平 (0-1)
    energy_level: number;          // 能量水平 (0-100)
    recommendations: string[];     // 建议列表
    alerts?: HealthAlert[];        // 健康警告
}

export interface HealthAlert {
    type: 'warning' | 'critical';  // 警告类型
    metric: HealthMetricType;      // 相关指标
    message: string;               // 警告消息
    threshold: number;             // 阈值
    current_value: number;         // 当前值
    suggested_action?: string;     // 建议操作
}

// ============================================================================
// 通知相关
// ============================================================================

export interface NotificationPayload {
    id: string;                    // 通知ID
    title: string;                 // 通知标题
    message: string;               // 通知内容
    priority: NotificationPriority; // 优先级
    category: string;              // 分类
    icon?: string;                 // 图标
    image_url?: string;            // 图片URL
    actions?: NotificationAction[]; // 操作按钮
    metadata?: Record<string, any>; // 元数据
    expires_at?: number;           // 过期时间
    sound?: string;                // 声音
    vibration?: number[];          // 震动模式
}

export interface NotificationAction {
    id: string;                    // 操作ID
    label: string;                 // 按钮文本
    type: 'button' | 'input' | 'navigation'; // 操作类型
    style?: 'default' | 'destructive' | 'cancel'; // 样式
    target?: string;               // 目标 (导航用)
    parameters?: Record<string, any>; // 参数
}

export interface NotificationResponse {
    notification_id: string;       // 通知ID
    action_id?: string;            // 操作ID
    user_input?: string;           // 用户输入
    timestamp: number;             // 响应时间
}

// ============================================================================
// 设备信息相关
// ============================================================================

export interface DeviceInfo {
    device_id: string;             // 设备唯一标识
    device_type: 'apple_watch' | 'wear_os' | 'harmony_os'; // 设备类型
    device_model: string;          // 设备型号
    os_version: string;            // 操作系统版本
    app_version: string;           // 应用版本
    screen_size: {                 // 屏幕尺寸
        width: number;
        height: number;
        density: number;
    };
    capabilities: DeviceCapability[]; // 设备能力
    battery_level?: number;        // 电池电量 (0-100)
    connectivity: ConnectivityInfo; // 连接信息
}

export interface DeviceCapability {
    type: string;                  // 能力类型
    supported: boolean;            // 是否支持
    version?: string;              // 版本信息
    parameters?: Record<string, any>; // 参数
}

export interface ConnectivityInfo {
    wifi_connected: boolean;       // WiFi连接状态
    cellular_connected: boolean;   // 蜂窝网络连接状态
    bluetooth_connected: boolean;  // 蓝牙连接状态
    signal_strength?: number;      // 信号强度 (0-100)
    network_type?: string;         // 网络类型
}

// ============================================================================
// 会话管理
// ============================================================================

export interface SessionInfo {
    session_id: string;            // 会话ID
    user_id: string;               // 用户ID
    device_id: string;             // 设备ID
    started_at: number;            // 会话开始时间
    last_activity: number;         // 最后活动时间
    expires_at: number;            // 会话过期时间
    permissions: string[];         // 权限列表
    metadata?: Record<string, any>; // 会话元数据
}

export interface AuthenticationRequest {
    device_id: string;             // 设备ID
    device_info: DeviceInfo;       // 设备信息
    auth_token?: string;           // 认证令牌
    biometric_data?: string;       // 生物识别数据
    challenge_response?: string;   // 挑战响应
}

export interface AuthenticationResponse {
    success: boolean;              // 认证是否成功
    session_info?: SessionInfo;    // 会话信息
    error_code?: string;           // 错误代码
    error_message?: string;        // 错误消息
    retry_after?: number;          // 重试间隔 (seconds)
}

// ============================================================================
// 配置和设置
// ============================================================================

export interface UserPreferences {
    user_id: string;               // 用户ID
    theme: 'light' | 'dark' | 'auto'; // 主题设置
    language: string;              // 语言设置
    timezone: string;              // 时区设置
    notifications: {               // 通知设置
        enabled: boolean;
        quiet_hours: {
            enabled: boolean;
            start: string;         // "22:00"
            end: string;           // "08:00"
        };
        categories: Record<string, boolean>; // 分类开关
    };
    health_monitoring: {           // 健康监测设置
        enabled: boolean;
        frequency: number;         // 监测频率 (minutes)
        metrics: HealthMetricType[]; // 监测指标
    };
    privacy: {                     // 隐私设置
        data_sharing: boolean;
        analytics: boolean;
        location_tracking: boolean;
    };
}

export interface SystemConfiguration {
    api_endpoints: {               // API端点配置
        primary: string;
        fallback: string[];
    };
    sync_settings: {               // 同步设置
        interval: number;          // 同步间隔 (seconds)
        batch_size: number;        // 批量大小
        retry_attempts: number;    // 重试次数
    };
    performance: {                 // 性能设置
        cache_size: number;        // 缓存大小 (MB)
        max_concurrent_requests: number; // 最大并发请求
        request_timeout: number;   // 请求超时 (seconds)
    };
    security: {                    // 安全设置
        encryption_enabled: boolean;
        certificate_pinning: boolean;
        token_refresh_threshold: number; // 令牌刷新阈值 (seconds)
    };
}

// ============================================================================
// 错误处理
// ============================================================================

export interface ErrorInfo {
    code: string;                  // 错误代码
    message: string;               // 错误消息
    details?: string;              // 详细信息
    timestamp: number;             // 错误时间
    context?: Record<string, any>; // 错误上下文
    stack_trace?: string;          // 堆栈跟踪
    user_message?: string;         // 用户友好消息
    recovery_suggestions?: string[]; // 恢复建议
}

export interface ApiResponse<T = any> {
    success: boolean;              // 请求是否成功
    data?: T;                      // 响应数据
    error?: ErrorInfo;             // 错误信息
    metadata?: {                   // 元数据
        request_id: string;
        timestamp: number;
        version: string;
        rate_limit?: {
            remaining: number;
            reset_time: number;
        };
    };
}

// ============================================================================
// 常量定义
// ============================================================================

export const PROTOCOL_VERSION = '1.0.0';

export const MESSAGE_TYPES = {
    COMMAND: 'command' as const,
    STATUS: 'status' as const,
    NOTIFICATION: 'notification' as const,
    RESPONSE: 'response' as const,
    HEARTBEAT: 'heartbeat' as const,
} as const;

export const SYSTEM_IDS = {
    NEXUS_REMOTE: 'nexus_remote',
    RAG_SYSTEM: 'rag_system',
    CHANGLEE: 'changlee',
    CHRONICLE: 'chronicle',
    BOVINE_INSIGHT: 'bovine_insight',
    MOLECULAR_DYNAMICS: 'molecular_dynamics',
    GENOME_JIGSAW: 'genome_jigsaw',
} as const;

export const COMMANDS = {
    // 电源管理
    POWER_ON: 'power_on',
    POWER_OFF: 'power_off',
    RESTART: 'restart',
    SLEEP: 'sleep',
    WAKE: 'wake',
    
    // 系统控制
    START_SERVICE: 'start_service',
    STOP_SERVICE: 'stop_service',
    RESTART_SERVICE: 'restart_service',
    GET_STATUS: 'get_status',
    GET_LOGS: 'get_logs',
    
    // 数据操作
    SYNC_DATA: 'sync_data',
    BACKUP_DATA: 'backup_data',
    RESTORE_DATA: 'restore_data',
    CLEAR_CACHE: 'clear_cache',
    
    // AI 相关
    ASK_QUESTION: 'ask_question',
    GENERATE_CONTENT: 'generate_content',
    ANALYZE_DATA: 'analyze_data',
    TRAIN_MODEL: 'train_model',
} as const;

export const ERROR_CODES = {
    // 认证错误
    AUTH_FAILED: 'AUTH_FAILED',
    TOKEN_EXPIRED: 'TOKEN_EXPIRED',
    PERMISSION_DENIED: 'PERMISSION_DENIED',
    
    // 网络错误
    NETWORK_ERROR: 'NETWORK_ERROR',
    TIMEOUT: 'TIMEOUT',
    CONNECTION_LOST: 'CONNECTION_LOST',
    
    // 系统错误
    SYSTEM_UNAVAILABLE: 'SYSTEM_UNAVAILABLE',
    COMMAND_FAILED: 'COMMAND_FAILED',
    INVALID_PARAMETERS: 'INVALID_PARAMETERS',
    RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
    
    // 数据错误
    INVALID_DATA: 'INVALID_DATA',
    DATA_CORRUPTION: 'DATA_CORRUPTION',
    STORAGE_FULL: 'STORAGE_FULL',
    
    // 设备错误
    DEVICE_NOT_SUPPORTED: 'DEVICE_NOT_SUPPORTED',
    CAPABILITY_NOT_AVAILABLE: 'CAPABILITY_NOT_AVAILABLE',
    BATTERY_LOW: 'BATTERY_LOW',
} as const;

// ============================================================================
// 工具函数类型
// ============================================================================

export interface MessageBuilder {
    createCommand(request: CommandRequest): MessageEnvelope<CommandRequest>;
    createResponse(response: CommandResponse): MessageEnvelope<CommandResponse>;
    createNotification(notification: NotificationPayload): MessageEnvelope<NotificationPayload>;
    createHeartbeat(deviceInfo: DeviceInfo): MessageEnvelope<DeviceInfo>;
    createError(error: ErrorInfo): MessageEnvelope<ErrorInfo>;
}

export interface MessageValidator {
    validateMessage(message: MessageEnvelope): boolean;
    validatePayload<T>(payload: T, schema: any): boolean;
    sanitizeMessage(message: MessageEnvelope): MessageEnvelope;
}

export interface MessageSerializer {
    serialize(message: MessageEnvelope): string | Uint8Array;
    deserialize(data: string | Uint8Array): MessageEnvelope;
    compress(data: string | Uint8Array): Uint8Array;
    decompress(data: Uint8Array): string | Uint8Array;
}

// ============================================================================
// 导出所有类型
// ============================================================================

export type {
    MessageType,
    SystemStatus,
    CommandStatus,
    NotificationPriority,
    HealthMetricType,
    BaseMessage,
    MessageEnvelope,
    SystemInfo,
    SystemMetrics,
    SystemsStatusPayload,
    CommandRequest,
    CommandResponse,
    CommandStatusPayload,
    HealthMetric,
    HealthDataPayload,
    HealthAnalysis,
    HealthAlert,
    NotificationPayload,
    NotificationAction,
    NotificationResponse,
    DeviceInfo,
    DeviceCapability,
    ConnectivityInfo,
    SessionInfo,
    AuthenticationRequest,
    AuthenticationResponse,
    UserPreferences,
    SystemConfiguration,
    ErrorInfo,
    ApiResponse,
    MessageBuilder,
    MessageValidator,
    MessageSerializer,
};