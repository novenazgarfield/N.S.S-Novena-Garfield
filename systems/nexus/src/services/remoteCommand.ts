// Remote Command Execution Service - NEXUS远程指挥中心
import { WebSocketService, WebSocketMessage } from './websocket';

export interface RemoteCommand {
  command: string;
  parameters?: Record<string, any>;
  description?: string;
}

export interface TaskInfo {
  task_id: string;
  command: string;
  description: string;
  status: 'starting' | 'running' | 'completed' | 'failed' | 'error';
  start_time: string;
  end_time?: string;
  client: string;
  parameters?: Record<string, any>;
  return_code?: number;
  error?: string;
}

export interface SystemInfo {
  connected_clients: number;
  active_tasks: number;
  available_commands: Record<string, { script: string; description: string }>;
  timestamp: string;
}

export type TaskEventHandler = (taskId: string, info: TaskInfo) => void;
export type LogEventHandler = (taskId: string, output: string, timestamp: string) => void;
export type SystemEventHandler = (info: SystemInfo) => void;

export class RemoteCommandService {
  private wsService: WebSocketService;
  private activeTasks: Map<string, TaskInfo> = new Map();
  private availableCommands: Record<string, { script: string; description: string }> = {};
  private systemInfo: SystemInfo | null = null;

  // 事件处理器
  private taskStartHandlers: TaskEventHandler[] = [];
  private taskCompleteHandlers: TaskEventHandler[] = [];
  private taskErrorHandlers: TaskEventHandler[] = [];
  private logHandlers: LogEventHandler[] = [];
  private systemInfoHandlers: SystemEventHandler[] = [];

  constructor(wsUrl: string) {
    this.wsService = new WebSocketService({
      url: wsUrl,
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    // 处理欢迎消息
    this.wsService.on('welcome', (message: WebSocketMessage) => {
      console.log('🎉 连接到NEXUS远程指挥中心:', message.payload.message);
      this.availableCommands = message.payload.available_commands || {};
      
      // 请求系统信息
      this.requestSystemInfo();
    });

    // 处理任务开始
    this.wsService.on('task_started', (message: WebSocketMessage) => {
      const { task_id, command, description, timestamp } = message.payload;
      const taskInfo: TaskInfo = {
        task_id,
        command,
        description,
        status: 'starting',
        start_time: timestamp,
        client: 'remote'
      };
      
      this.activeTasks.set(task_id, taskInfo);
      this.taskStartHandlers.forEach(handler => handler(task_id, taskInfo));
    });

    // 处理任务创建确认
    this.wsService.on('task_created', (message: WebSocketMessage) => {
      const { task_id, message: msg, timestamp } = message.payload;
      console.log(`✅ 任务已创建: ${task_id} - ${msg}`);
    });

    // 处理实时日志
    this.wsService.on('task_log', (message: WebSocketMessage) => {
      const { task_id, output, timestamp } = message.payload;
      
      // 更新任务状态为运行中
      const task = this.activeTasks.get(task_id);
      if (task && task.status === 'starting') {
        task.status = 'running';
        this.activeTasks.set(task_id, task);
      }
      
      this.logHandlers.forEach(handler => handler(task_id, output, timestamp));
    });

    // 处理任务完成
    this.wsService.on('task_completed', (message: WebSocketMessage) => {
      const { task_id, status, return_code, timestamp } = message.payload;
      const task = this.activeTasks.get(task_id);
      
      if (task) {
        task.status = status;
        task.return_code = return_code;
        task.end_time = timestamp;
        this.activeTasks.set(task_id, task);
        
        this.taskCompleteHandlers.forEach(handler => handler(task_id, task));
      }
    });

    // 处理任务错误
    this.wsService.on('task_error', (message: WebSocketMessage) => {
      const { task_id, error, timestamp } = message.payload;
      const task = this.activeTasks.get(task_id);
      
      if (task) {
        task.status = 'error';
        task.error = error;
        task.end_time = timestamp;
        this.activeTasks.set(task_id, task);
        
        this.taskErrorHandlers.forEach(handler => handler(task_id, task));
      }
    });

    // 处理系统信息
    this.wsService.on('system_info', (message: WebSocketMessage) => {
      this.systemInfo = message.payload;
      this.systemInfoHandlers.forEach(handler => handler(this.systemInfo!));
    });

    // 处理错误
    this.wsService.on('error', (message: WebSocketMessage) => {
      console.error('❌ 远程指挥中心错误:', message.payload.message);
    });
  }

  // 连接到远程指挥中心
  async connect(): Promise<void> {
    try {
      await this.wsService.connect();
      console.log('🔗 已连接到NEXUS远程指挥中心');
    } catch (error) {
      console.error('❌ 连接远程指挥中心失败:', error);
      throw error;
    }
  }

  // 断开连接
  disconnect(): void {
    this.wsService.disconnect();
    console.log('🔌 已断开远程指挥中心连接');
  }

  // 执行远程命令
  async executeCommand(command: RemoteCommand): Promise<string> {
    if (!this.wsService.isConnected()) {
      throw new Error('未连接到远程指挥中心');
    }

    if (!this.availableCommands[command.command]) {
      throw new Error(`未授权的命令: ${command.command}`);
    }

    return new Promise((resolve, reject) => {
      const message = {
        type: 'execute_command',
        command: command.command,
        parameters: command.parameters || {}
      };

      // 监听任务创建确认
      const handleTaskCreated = (msg: WebSocketMessage) => {
        if (msg.type === 'task_created') {
          this.wsService.off('task_created', handleTaskCreated);
          resolve(msg.payload.task_id);
        }
      };

      const handleError = (msg: WebSocketMessage) => {
        if (msg.type === 'error') {
          this.wsService.off('error', handleError);
          reject(new Error(msg.payload.message));
        }
      };

      this.wsService.on('task_created', handleTaskCreated);
      this.wsService.on('error', handleError);

      this.wsService.send(message);

      // 超时处理
      setTimeout(() => {
        this.wsService.off('task_created', handleTaskCreated);
        this.wsService.off('error', handleError);
        reject(new Error('命令执行请求超时'));
      }, 10000);
    });
  }

  // 获取任务状态
  getTaskStatus(taskId: string): TaskInfo | null {
    return this.activeTasks.get(taskId) || null;
  }

  // 获取所有活动任务
  getActiveTasks(): TaskInfo[] {
    return Array.from(this.activeTasks.values());
  }

  // 获取可用命令
  getAvailableCommands(): Record<string, { script: string; description: string }> {
    return this.availableCommands;
  }

  // 获取系统信息
  getSystemInfo(): SystemInfo | null {
    return this.systemInfo;
  }

  // 请求系统信息
  requestSystemInfo(): void {
    if (this.wsService.isConnected()) {
      this.wsService.send({ type: 'get_system_info' });
    }
  }

  // 请求任务状态
  requestTaskStatus(taskId: string): void {
    if (this.wsService.isConnected()) {
      this.wsService.send({ 
        type: 'get_task_status',
        task_id: taskId 
      });
    }
  }

  // 事件监听器注册方法
  onTaskStart(handler: TaskEventHandler): void {
    this.taskStartHandlers.push(handler);
  }

  onTaskComplete(handler: TaskEventHandler): void {
    this.taskCompleteHandlers.push(handler);
  }

  onTaskError(handler: TaskEventHandler): void {
    this.taskErrorHandlers.push(handler);
  }

  onLog(handler: LogEventHandler): void {
    this.logHandlers.push(handler);
  }

  onSystemInfo(handler: SystemEventHandler): void {
    this.systemInfoHandlers.push(handler);
  }

  // 移除事件监听器
  offTaskStart(handler: TaskEventHandler): void {
    const index = this.taskStartHandlers.indexOf(handler);
    if (index > -1) {
      this.taskStartHandlers.splice(index, 1);
    }
  }

  offTaskComplete(handler: TaskEventHandler): void {
    const index = this.taskCompleteHandlers.indexOf(handler);
    if (index > -1) {
      this.taskCompleteHandlers.splice(index, 1);
    }
  }

  offTaskError(handler: TaskEventHandler): void {
    const index = this.taskErrorHandlers.indexOf(handler);
    if (index > -1) {
      this.taskErrorHandlers.splice(index, 1);
    }
  }

  offLog(handler: LogEventHandler): void {
    const index = this.logHandlers.indexOf(handler);
    if (index > -1) {
      this.logHandlers.splice(index, 1);
    }
  }

  offSystemInfo(handler: SystemEventHandler): void {
    const index = this.systemInfoHandlers.indexOf(handler);
    if (index > -1) {
      this.systemInfoHandlers.splice(index, 1);
    }
  }

  // 连接状态检查
  isConnected(): boolean {
    return this.wsService.isConnected();
  }

  // 获取连接状态
  getConnectionState(): string {
    return this.wsService.isConnected() ? 'connected' : 'disconnected';
  }
}

// 创建全局实例
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';
export const remoteCommandService = new RemoteCommandService(WS_URL);