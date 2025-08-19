const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { createModuleLogger } = require('../shared/logger');
const { generateId, cleanText, truncateText } = require('../shared/utils');
const config = require('../shared/config');
const database = require('./database');

const logger = createModuleLogger('command-monitor');

class CommandMonitor {
  constructor() {
    this.sessions = new Map(); // sessionId -> monitoring info
    this.isEnabled = config.monitoring.command.enabled;
    this.supportedShells = config.monitoring.command.shells;
    this.maxOutputLength = config.monitoring.command.maxOutputLength;
    this.captureEnvironment = config.monitoring.command.captureEnvironment;
    this.hookScripts = new Map(); // sessionId -> hook script paths
  }

  /**
   * 启动命令行监控
   */
  async startMonitoring(sessionId, projectPath, options = {}) {
    if (!this.isEnabled) {
      logger.warn('Command monitoring is disabled');
      return false;
    }

    try {
      // 如果已经在监控，先停止
      if (this.sessions.has(sessionId)) {
        await this.stopMonitoring(sessionId);
      }

      // 检测可用的shell
      const availableShells = await this.detectAvailableShells();
      if (availableShells.length === 0) {
        logger.warn('No supported shells found');
        return false;
      }

      // 创建监控会话
      const sessionInfo = {
        projectPath,
        startTime: Date.now(),
        availableShells,
        activeHooks: new Map(),
        commandHistory: [],
        isActive: true,
        options
      };

      this.sessions.set(sessionId, sessionInfo);

      // 为每个可用的shell设置监控钩子
      for (const shell of availableShells) {
        try {
          await this.setupShellHook(sessionId, shell, projectPath);
        } catch (error) {
          logger.warn('Failed to setup shell hook', { 
            sessionId, 
            shell, 
            error: error.message 
          });
        }
      }

      logger.info('Command monitoring started', { 
        sessionId, 
        projectPath, 
        availableShells 
      });

      return true;

    } catch (error) {
      logger.error('Failed to start command monitoring', { 
        sessionId, 
        projectPath, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 停止命令行监控
   */
  async stopMonitoring(sessionId) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) {
      logger.warn('No command monitoring found for session', { sessionId });
      return false;
    }

    try {
      // 清理所有shell钩子
      for (const [shell, hookInfo] of sessionInfo.activeHooks) {
        await this.cleanupShellHook(sessionId, shell, hookInfo);
      }

      // 移除会话
      this.sessions.delete(sessionId);

      const duration = Date.now() - sessionInfo.startTime;
      logger.info('Command monitoring stopped', { 
        sessionId, 
        duration 
      });

      return true;

    } catch (error) {
      logger.error('Failed to stop command monitoring', { 
        sessionId, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 检测可用的shell
   */
  async detectAvailableShells() {
    const shells = [];
    const platform = process.platform;

    // 根据平台检测shell
    if (platform === 'win32') {
      // Windows
      if (await this.isCommandAvailable('powershell')) {
        shells.push('powershell');
      }
      if (await this.isCommandAvailable('cmd')) {
        shells.push('cmd');
      }
      // WSL
      if (await this.isCommandAvailable('wsl')) {
        shells.push('wsl-bash');
      }
    } else {
      // Unix-like systems
      const unixShells = ['bash', 'zsh', 'fish', 'sh'];
      for (const shell of unixShells) {
        if (await this.isCommandAvailable(shell)) {
          shells.push(shell);
        }
      }
    }

    return shells.filter(shell => this.supportedShells.includes(shell) || shell.startsWith('wsl-'));
  }

  /**
   * 检查命令是否可用
   */
  async isCommandAvailable(command) {
    return new Promise((resolve) => {
      const testCommand = process.platform === 'win32' ? 'where' : 'which';
      exec(`${testCommand} ${command}`, (error) => {
        resolve(!error);
      });
    });
  }

  /**
   * 为shell设置监控钩子
   */
  async setupShellHook(sessionId, shell, projectPath) {
    const platform = process.platform;
    
    if (platform === 'win32') {
      return await this.setupWindowsShellHook(sessionId, shell, projectPath);
    } else {
      return await this.setupUnixShellHook(sessionId, shell, projectPath);
    }
  }

  /**
   * 设置Windows shell钩子
   */
  async setupWindowsShellHook(sessionId, shell, projectPath) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) return false;

    try {
      if (shell === 'powershell') {
        // PowerShell钩子
        const hookScript = await this.createPowerShellHook(sessionId, projectPath);
        sessionInfo.activeHooks.set(shell, { type: 'powershell', script: hookScript });
        
      } else if (shell === 'cmd') {
        // CMD钩子 - 使用doskey
        const hookScript = await this.createCmdHook(sessionId, projectPath);
        sessionInfo.activeHooks.set(shell, { type: 'cmd', script: hookScript });
        
      } else if (shell === 'wsl-bash') {
        // WSL Bash钩子
        const hookScript = await this.createWSLBashHook(sessionId, projectPath);
        sessionInfo.activeHooks.set(shell, { type: 'wsl-bash', script: hookScript });
      }

      return true;
    } catch (error) {
      logger.error('Failed to setup Windows shell hook', { 
        sessionId, 
        shell, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 设置Unix shell钩子
   */
  async setupUnixShellHook(sessionId, shell, projectPath) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) return false;

    try {
      // 创建钩子脚本
      const hookScript = await this.createUnixShellHook(sessionId, shell, projectPath);
      sessionInfo.activeHooks.set(shell, { 
        type: 'unix', 
        shell, 
        script: hookScript 
      });

      return true;
    } catch (error) {
      logger.error('Failed to setup Unix shell hook', { 
        sessionId, 
        shell, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 创建PowerShell钩子
   */
  async createPowerShellHook(sessionId, projectPath) {
    const hookDir = path.join(os.tmpdir(), 'chronicle', sessionId);
    await fs.promises.mkdir(hookDir, { recursive: true });

    const hookScript = path.join(hookDir, 'powershell-hook.ps1');
    const logFile = path.join(hookDir, 'commands.log');

    const scriptContent = `
# Chronicle PowerShell Hook
$ChronicleSessionId = "${sessionId}"
$ChronicleLogFile = "${logFile.replace(/\\/g, '\\\\')}"
$ChronicleProjectPath = "${projectPath.replace(/\\/g, '\\\\')}"

function Invoke-ChronicleCommand {
    param([string]$Command)
    
    $StartTime = Get-Date
    $WorkingDir = Get-Location
    
    # 执行命令并捕获输出
    try {
        $Output = Invoke-Expression $Command 2>&1
        $ExitCode = $LASTEXITCODE
        $Success = $true
    } catch {
        $Output = $_.Exception.Message
        $ExitCode = 1
        $Success = $false
    }
    
    $EndTime = Get-Date
    $Duration = ($EndTime - $StartTime).TotalMilliseconds
    
    # 记录命令信息
    $CommandInfo = @{
        sessionId = $ChronicleSessionId
        command = $Command
        shell = "powershell"
        workingDirectory = $WorkingDir.Path
        startTime = [int64]($StartTime - [datetime]'1970-01-01').TotalMilliseconds
        endTime = [int64]($EndTime - [datetime]'1970-01-01').TotalMilliseconds
        duration = [int]$Duration
        exitCode = $ExitCode
        stdout = ($Output | Out-String)
        stderr = ""
        success = $Success
    }
    
    # 写入日志文件
    $CommandInfo | ConvertTo-Json -Compress | Add-Content -Path $ChronicleLogFile
    
    return $Output
}

# 重写常用命令
function cd { Set-Location @args; Invoke-ChronicleCommand "cd $args" }
function ls { Get-ChildItem @args; Invoke-ChronicleCommand "ls $args" }
function dir { Get-ChildItem @args; Invoke-ChronicleCommand "dir $args" }
`;

    await fs.promises.writeFile(hookScript, scriptContent, 'utf8');
    
    // 启动日志监控
    this.startLogFileMonitoring(sessionId, logFile);
    
    return hookScript;
  }

  /**
   * 创建Unix shell钩子
   */
  async createUnixShellHook(sessionId, shell, projectPath) {
    const hookDir = path.join(os.tmpdir(), 'chronicle', sessionId);
    await fs.promises.mkdir(hookDir, { recursive: true });

    const hookScript = path.join(hookDir, `${shell}-hook.sh`);
    const logFile = path.join(hookDir, 'commands.log');

    const scriptContent = `#!/bin/bash
# Chronicle ${shell} Hook
export CHRONICLE_SESSION_ID="${sessionId}"
export CHRONICLE_LOG_FILE="${logFile}"
export CHRONICLE_PROJECT_PATH="${projectPath}"

chronicle_log_command() {
    local cmd="$1"
    local start_time=$(date +%s%3N)
    local working_dir="$(pwd)"
    local stdout_file=$(mktemp)
    local stderr_file=$(mktemp)
    
    # 执行命令并捕获输出
    eval "$cmd" > "$stdout_file" 2> "$stderr_file"
    local exit_code=$?
    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))
    
    # 读取输出
    local stdout_content=$(cat "$stdout_file" 2>/dev/null || echo "")
    local stderr_content=$(cat "$stderr_file" 2>/dev/null || echo "")
    
    # 清理临时文件
    rm -f "$stdout_file" "$stderr_file"
    
    # 构建JSON记录
    local json_record=$(cat <<EOF
{
  "sessionId": "$CHRONICLE_SESSION_ID",
  "command": "$cmd",
  "shell": "$shell",
  "workingDirectory": "$working_dir",
  "startTime": $start_time,
  "endTime": $end_time,
  "duration": $duration,
  "exitCode": $exit_code,
  "stdout": $(echo "$stdout_content" | jq -R -s .),
  "stderr": $(echo "$stderr_content" | jq -R -s .),
  "environment": {}
}
EOF
)
    
    # 写入日志文件
    echo "$json_record" >> "$CHRONICLE_LOG_FILE"
    
    # 显示输出
    [ -n "$stdout_content" ] && echo "$stdout_content"
    [ -n "$stderr_content" ] && echo "$stderr_content" >&2
    
    return $exit_code
}

# 设置PROMPT_COMMAND钩子
if [ "$shell" = "bash" ]; then
    export PROMPT_COMMAND="chronicle_log_command '\$(history 1 | sed \"s/^[ ]*[0-9]*[ ]*//\")'; $PROMPT_COMMAND"
fi
`;

    await fs.promises.writeFile(hookScript, scriptContent, 'utf8');
    await fs.promises.chmod(hookScript, '755');
    
    // 启动日志监控
    this.startLogFileMonitoring(sessionId, logFile);
    
    return hookScript;
  }

  /**
   * 启动日志文件监控
   */
  startLogFileMonitoring(sessionId, logFile) {
    const fs = require('fs');
    
    // 确保日志文件存在
    if (!fs.existsSync(logFile)) {
      fs.writeFileSync(logFile, '', 'utf8');
    }

    // 监控日志文件变化
    const watcher = fs.watchFile(logFile, { interval: 500 }, () => {
      this.processLogFile(sessionId, logFile);
    });

    // 存储监控器引用
    const sessionInfo = this.sessions.get(sessionId);
    if (sessionInfo) {
      if (!sessionInfo.logWatchers) {
        sessionInfo.logWatchers = [];
      }
      sessionInfo.logWatchers.push({ file: logFile, watcher });
    }
  }

  /**
   * 处理日志文件
   */
  async processLogFile(sessionId, logFile) {
    try {
      const content = await fs.promises.readFile(logFile, 'utf8');
      const lines = content.trim().split('\n').filter(line => line.trim());
      
      const sessionInfo = this.sessions.get(sessionId);
      if (!sessionInfo) return;

      // 处理新的日志行
      const processedCount = sessionInfo.processedLogLines || 0;
      const newLines = lines.slice(processedCount);

      for (const line of newLines) {
        try {
          const commandInfo = JSON.parse(line);
          await this.recordCommandEvent(sessionId, commandInfo);
        } catch (error) {
          logger.warn('Failed to parse log line', { sessionId, line, error: error.message });
        }
      }

      // 更新处理计数
      sessionInfo.processedLogLines = lines.length;

    } catch (error) {
      logger.error('Failed to process log file', { 
        sessionId, 
        logFile, 
        error: error.message 
      });
    }
  }

  /**
   * 记录命令事件
   */
  async recordCommandEvent(sessionId, commandInfo) {
    try {
      // 清理和截断输出
      const cleanStdout = cleanText(commandInfo.stdout || '');
      const cleanStderr = cleanText(commandInfo.stderr || '');
      
      const truncatedStdout = truncateText(cleanStdout, this.maxOutputLength);
      const truncatedStderr = truncateText(cleanStderr, this.maxOutputLength);

      // 构建命令信息
      const eventData = {
        command: commandInfo.command,
        shell: commandInfo.shell,
        workingDirectory: commandInfo.workingDirectory,
        exitCode: commandInfo.exitCode,
        startTime: commandInfo.startTime,
        endTime: commandInfo.endTime,
        duration: commandInfo.duration,
        stdout: truncatedStdout,
        stderr: truncatedStderr,
        environment: this.captureEnvironment ? (commandInfo.environment || {}) : {}
      };

      // 记录到数据库
      const eventId = await database.recordCommandEvent(sessionId, eventData);

      // 更新会话历史
      const sessionInfo = this.sessions.get(sessionId);
      if (sessionInfo) {
        sessionInfo.commandHistory.push({
          eventId,
          command: commandInfo.command,
          exitCode: commandInfo.exitCode,
          timestamp: commandInfo.startTime
        });

        // 限制历史记录长度
        if (sessionInfo.commandHistory.length > 100) {
          sessionInfo.commandHistory = sessionInfo.commandHistory.slice(-50);
        }
      }

      logger.debug('Command event recorded', { 
        sessionId, 
        eventId, 
        command: commandInfo.command.substring(0, 50),
        exitCode: commandInfo.exitCode
      });

      // 触发事件回调
      this.emit('commandEvent', {
        sessionId,
        eventId,
        commandInfo: eventData
      });

      return eventId;

    } catch (error) {
      logger.error('Failed to record command event', { 
        sessionId, 
        error: error.message 
      });
      return null;
    }
  }

  /**
   * 清理shell钩子
   */
  async cleanupShellHook(sessionId, shell, hookInfo) {
    try {
      // 停止日志文件监控
      const sessionInfo = this.sessions.get(sessionId);
      if (sessionInfo && sessionInfo.logWatchers) {
        for (const { file, watcher } of sessionInfo.logWatchers) {
          fs.unwatchFile(file);
        }
      }

      // 删除钩子脚本
      if (hookInfo.script && fs.existsSync(hookInfo.script)) {
        await fs.promises.unlink(hookInfo.script);
      }

      // 清理临时目录
      const hookDir = path.dirname(hookInfo.script);
      if (fs.existsSync(hookDir)) {
        await fs.promises.rmdir(hookDir, { recursive: true });
      }

      logger.debug('Shell hook cleaned up', { sessionId, shell });

    } catch (error) {
      logger.error('Failed to cleanup shell hook', { 
        sessionId, 
        shell, 
        error: error.message 
      });
    }
  }

  /**
   * 获取监控状态
   */
  getMonitoringStatus(sessionId) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) {
      return null;
    }

    return {
      sessionId,
      projectPath: sessionInfo.projectPath,
      startTime: sessionInfo.startTime,
      duration: Date.now() - sessionInfo.startTime,
      availableShells: sessionInfo.availableShells,
      activeHooks: Array.from(sessionInfo.activeHooks.keys()),
      commandHistoryCount: sessionInfo.commandHistory.length,
      isActive: sessionInfo.isActive
    };
  }

  /**
   * 获取命令历史
   */
  getCommandHistory(sessionId, limit = 10) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) {
      return [];
    }

    return sessionInfo.commandHistory
      .slice(-limit)
      .reverse();
  }

  /**
   * 停止所有监控
   */
  async stopAllMonitoring() {
    const sessionIds = Array.from(this.sessions.keys());
    const results = await Promise.allSettled(
      sessionIds.map(sessionId => this.stopMonitoring(sessionId))
    );

    const successful = results.filter(r => r.status === 'fulfilled' && r.value).length;
    logger.info('Stopped all command monitoring', { 
      total: sessionIds.length, 
      successful 
    });

    return successful;
  }

  /**
   * 事件发射器功能
   */
  emit(eventName, data) {
    if (this.listeners && this.listeners[eventName]) {
      this.listeners[eventName].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          logger.error('Event listener error', { 
            eventName, 
            error: error.message 
          });
        }
      });
    }
  }

  on(eventName, callback) {
    if (!this.listeners) {
      this.listeners = {};
    }
    if (!this.listeners[eventName]) {
      this.listeners[eventName] = [];
    }
    this.listeners[eventName].push(callback);
  }

  off(eventName, callback) {
    if (this.listeners && this.listeners[eventName]) {
      const index = this.listeners[eventName].indexOf(callback);
      if (index > -1) {
        this.listeners[eventName].splice(index, 1);
      }
    }
  }
}

// 创建单例实例
const commandMonitor = new CommandMonitor();

module.exports = commandMonitor;