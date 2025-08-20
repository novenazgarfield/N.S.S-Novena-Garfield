// Remote Command Center - NEXUS远程指挥中心界面
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid2 as Grid,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  LinearProgress,
  Alert,
  Fab,
  Badge,
  Tooltip,
  IconButton,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Terminal,
  Computer,
  CloudQueue,
  Speed,
  Assignment,
  CheckCircle,
  Error,
  Warning,
  Info,
  Close,
  Fullscreen,
  FullscreenExit,
  PowerSettingsNew,
  WifiTethering,
  PowerOff,
  RestartAlt
} from '@mui/icons-material';
import { remoteCommandService, RemoteCommand, TaskInfo, SystemInfo } from '../../services/remoteCommand';

interface LogEntry {
  taskId: string;
  output: string;
  timestamp: string;
}

export const RemoteCommandCenter: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [activeTasks, setActiveTasks] = useState<TaskInfo[]>([]);
  const [availableCommands, setAvailableCommands] = useState<Record<string, any>>({});
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [commandDialogOpen, setCommandDialogOpen] = useState(false);
  const [logDialogOpen, setLogDialogOpen] = useState(false);
  const [isLogFullscreen, setIsLogFullscreen] = useState(false);
  const [wakeDialogOpen, setWakeDialogOpen] = useState(false);
  const [macAddress, setMacAddress] = useState('');
  const [ipAddress, setIpAddress] = useState('192.168.1.255');
  const [shutdownDialogOpen, setShutdownDialogOpen] = useState(false);
  const [shutdownType, setShutdownType] = useState('normal');
  const [shutdownDelay, setShutdownDelay] = useState(60);
  const [shutdownMessage, setShutdownMessage] = useState('NEXUS远程关机');
  const [connectionError, setConnectionError] = useState<string | null>(null);
  
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initializeRemoteConnection();
    return () => {
      remoteCommandService.disconnect();
    };
  }, []);

  useEffect(() => {
    // 自动滚动到日志底部
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const initializeRemoteConnection = async () => {
    try {
      // 设置事件监听器
      remoteCommandService.onTaskStart((taskId, info) => {
        setActiveTasks(prev => [...prev.filter(t => t.task_id !== taskId), info]);
      });

      remoteCommandService.onTaskComplete((taskId, info) => {
        setActiveTasks(prev => prev.map(t => t.task_id === taskId ? info : t));
      });

      remoteCommandService.onTaskError((taskId, info) => {
        setActiveTasks(prev => prev.map(t => t.task_id === taskId ? info : t));
      });

      remoteCommandService.onLog((taskId, output, timestamp) => {
        setLogs(prev => [...prev, { taskId, output, timestamp }]);
      });

      remoteCommandService.onSystemInfo((info) => {
        setSystemInfo(info);
        setAvailableCommands(info.available_commands);
      });

      // 连接到远程指挥中心
      await remoteCommandService.connect();
      setIsConnected(true);
      setConnectionError(null);
    } catch (error) {
      console.error('连接远程指挥中心失败:', error);
      setConnectionError(error instanceof Error ? error.message : '连接失败');
      setIsConnected(false);
    }
  };

  const handleExecuteCommand = async (command: RemoteCommand) => {
    try {
      const taskId = await remoteCommandService.executeCommand(command);
      console.log(`✅ 命令已提交，任务ID: ${taskId}`);
      setCommandDialogOpen(false);
    } catch (error) {
      console.error('执行命令失败:', error);
      alert(`执行命令失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const handleWakeComputer = async () => {
    if (!macAddress.trim()) {
      alert('请输入MAC地址');
      return;
    }
    
    const macPattern = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
    if (!macPattern.test(macAddress)) {
      alert('MAC地址格式无效，请使用格式：XX:XX:XX:XX:XX:XX');
      return;
    }

    try {
      const command: RemoteCommand = {
        type: 'execute_command',
        command: 'wake_computer',
        parameters: {
          mac_address: macAddress,
          ip_address: ipAddress
        }
      };
      
      const taskId = await remoteCommandService.executeCommand(command);
      console.log(`✅ 远程唤醒命令已提交，任务ID: ${taskId}`);
      setWakeDialogOpen(false);
    } catch (error) {
      console.error('远程唤醒失败:', error);
      alert(`远程唤醒失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const handleShutdownComputer = async () => {
    if (shutdownDelay < 10) {
      alert('延迟时间不能少于10秒，以确保安全');
      return;
    }

    const confirmMessage = `确认要${shutdownType === 'reboot' ? '重启' : '关闭'}本地电脑吗？\n\n` +
      `类型: ${shutdownType === 'normal' ? '正常关机' : shutdownType === 'force' ? '强制关机' : '重启'}\n` +
      `延迟: ${shutdownDelay}秒\n` +
      `消息: ${shutdownMessage}`;

    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      const command: RemoteCommand = {
        type: 'execute_command',
        command: 'shutdown_computer',
        parameters: {
          shutdown_type: shutdownType,
          delay_seconds: shutdownDelay,
          message: shutdownMessage
        }
      };
      
      const taskId = await remoteCommandService.executeCommand(command);
      console.log(`✅ 远程关机命令已提交，任务ID: ${taskId}`);
      setShutdownDialogOpen(false);
    } catch (error) {
      console.error('远程关机失败:', error);
      alert(`远程关机失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const handleRefreshSystemInfo = () => {
    remoteCommandService.requestSystemInfo();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': case 'error': return 'error';
      case 'starting': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Speed />;
      case 'completed': return <CheckCircle />;
      case 'failed': case 'error': return <Error />;
      case 'starting': return <Warning />;
      default: return <Info />;
    }
  };

  const getTaskLogs = (taskId: string) => {
    return logs.filter(log => log.taskId === taskId);
  };

  const ShutdownComputerDialog = () => (
    <Dialog
      open={shutdownDialogOpen}
      onClose={() => setShutdownDialogOpen(false)}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <PowerOff />
          远程关机/重启
        </Box>
      </DialogTitle>
      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>警告：</strong>此操作将关闭或重启本地电脑！请确保已保存所有工作。
          </Typography>
        </Alert>
        
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>操作类型</InputLabel>
          <Select
            value={shutdownType}
            onChange={(e) => setShutdownType(e.target.value)}
            label="操作类型"
          >
            <MenuItem value="normal">
              <Box display="flex" alignItems="center" gap={1}>
                <PowerOff fontSize="small" />
                正常关机
              </Box>
            </MenuItem>
            <MenuItem value="force">
              <Box display="flex" alignItems="center" gap={1}>
                <Stop fontSize="small" />
                强制关机
              </Box>
            </MenuItem>
            <MenuItem value="reboot">
              <Box display="flex" alignItems="center" gap={1}>
                <RestartAlt fontSize="small" />
                重启电脑
              </Box>
            </MenuItem>
          </Select>
        </FormControl>
        
        <TextField
          fullWidth
          type="number"
          label="延迟时间（秒）"
          value={shutdownDelay}
          onChange={(e) => setShutdownDelay(Number(e.target.value))}
          helperText="建议至少60秒，给用户保存工作的时间"
          sx={{ mb: 2 }}
          inputProps={{ min: 10, max: 3600 }}
        />
        
        <TextField
          fullWidth
          label="关机消息"
          value={shutdownMessage}
          onChange={(e) => setShutdownMessage(e.target.value)}
          helperText="将显示给用户的关机提示消息"
          sx={{ mb: 2 }}
        />
        
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>操作说明：</strong><br/>
            • 正常关机：安全关闭所有程序<br/>
            • 强制关机：立即关机，可能丢失数据<br/>
            • 重启电脑：关机后自动重新启动<br/>
            • 关机后可使用远程唤醒功能重新开机
          </Typography>
        </Alert>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShutdownDialogOpen(false)}>
          取消
        </Button>
        <Button 
          variant="contained" 
          color={shutdownType === 'reboot' ? 'warning' : 'error'}
          onClick={handleShutdownComputer}
          startIcon={shutdownType === 'reboot' ? <RestartAlt /> : <PowerOff />}
          disabled={!isConnected}
        >
          {shutdownType === 'reboot' ? '重启电脑' : '关闭电脑'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const WakeComputerDialog = () => (
    <Dialog
      open={wakeDialogOpen}
      onClose={() => setWakeDialogOpen(false)}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <PowerSettingsNew />
          远程唤醒电脑
        </Box>
      </DialogTitle>
      <DialogContent>
        <Alert severity="info" sx={{ mb: 2 }}>
          使用Wake-on-LAN技术远程唤醒目标电脑。请确保目标电脑已启用WOL功能。
        </Alert>
        
        <TextField
          fullWidth
          label="MAC地址"
          placeholder="XX:XX:XX:XX:XX:XX"
          value={macAddress}
          onChange={(e) => setMacAddress(e.target.value)}
          helperText="目标电脑的网卡MAC地址"
          sx={{ mb: 2 }}
          required
        />
        
        <TextField
          fullWidth
          label="IP地址"
          placeholder="192.168.1.255"
          value={ipAddress}
          onChange={(e) => setIpAddress(e.target.value)}
          helperText="目标网络的广播地址"
          sx={{ mb: 2 }}
        />
        
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>使用前请确认：</strong><br/>
            1. 目标电脑BIOS中已启用Wake-on-LAN<br/>
            2. 网卡驱动已启用WOL功能<br/>
            3. 电脑处于关机或睡眠状态<br/>
            4. 网络连接正常
          </Typography>
        </Alert>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setWakeDialogOpen(false)}>
          取消
        </Button>
        <Button 
          variant="contained" 
          onClick={handleWakeComputer}
          startIcon={<WifiTethering />}
          disabled={!isConnected || !macAddress.trim()}
        >
          发送唤醒信号
        </Button>
      </DialogActions>
    </Dialog>
  );

  const CommandExecutionDialog = () => (
    <Dialog 
      open={commandDialogOpen} 
      onClose={() => setCommandDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Terminal />
          执行远程命令
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          {Object.entries(availableCommands).map(([cmdName, cmdInfo]) => (
            <Grid size={{ xs: 12, md: 6 }} key={cmdName}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {cmdName}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {cmdInfo.description}
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={() => handleExecuteCommand({ command: cmdName })}
                    fullWidth
                  >
                    执行
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setCommandDialogOpen(false)}>
          取消
        </Button>
      </DialogActions>
    </Dialog>
  );

  const LogViewerDialog = () => (
    <Dialog 
      open={logDialogOpen} 
      onClose={() => setLogDialogOpen(false)}
      maxWidth={isLogFullscreen ? false : "lg"}
      fullWidth
      fullScreen={isLogFullscreen}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            <Terminal />
            实时日志监控
            {selectedTask && (
              <Chip 
                label={`任务: ${selectedTask.substring(0, 8)}...`} 
                size="small" 
                color="primary" 
              />
            )}
          </Box>
          <Box>
            <IconButton onClick={() => setIsLogFullscreen(!isLogFullscreen)}>
              {isLogFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
            <IconButton onClick={() => setLogDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent sx={{ p: 0 }}>
        <Paper 
          ref={logContainerRef}
          sx={{ 
            height: isLogFullscreen ? 'calc(100vh - 120px)' : '400px',
            overflow: 'auto',
            bgcolor: '#1e1e1e',
            color: '#ffffff',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            p: 2
          }}
        >
          {(selectedTask ? getTaskLogs(selectedTask) : logs).map((log, index) => (
            <Box key={index} sx={{ mb: 0.5 }}>
              <Typography 
                component="span" 
                sx={{ 
                  color: '#888',
                  fontSize: '0.75rem',
                  mr: 1
                }}
              >
                [{new Date(log.timestamp).toLocaleTimeString()}]
              </Typography>
              <Typography component="span" sx={{ fontFamily: 'monospace' }}>
                {log.output}
              </Typography>
            </Box>
          ))}
          {logs.length === 0 && (
            <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
              暂无日志输出
            </Typography>
          )}
        </Paper>
      </DialogContent>
    </Dialog>
  );

  if (!isConnected && connectionError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={initializeRemoteConnection}>
              重试连接
            </Button>
          }
        >
          无法连接到NEXUS远程指挥中心: {connectionError}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 标题栏 */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <Computer color="primary" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h4" component="h1">
              NEXUS 远程指挥中心
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              多设备协同 · 远程命令执行 · 实时监控
            </Typography>
          </Box>
        </Box>
        <Box display="flex" gap={1}>
          <Chip 
            icon={<CloudQueue />}
            label={isConnected ? "已连接" : "连接中..."} 
            color={isConnected ? "success" : "warning"}
            variant="outlined"
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefreshSystemInfo}
            disabled={!isConnected}
          >
            刷新状态
          </Button>
        </Box>
      </Box>

      {/* 系统状态卡片 */}
      {systemInfo && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="text.secondary" gutterBottom>
                  连接设备数
                </Typography>
                <Typography variant="h4" color="primary">
                  {systemInfo.connected_clients}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="text.secondary" gutterBottom>
                  活动任务数
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {systemInfo.active_tasks}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="text.secondary" gutterBottom>
                  可用命令数
                </Typography>
                <Typography variant="h4" color="success.main">
                  {Object.keys(systemInfo.available_commands).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="text.secondary" gutterBottom>
                  系统状态
                </Typography>
                <Chip 
                  label="正常运行" 
                  color="success" 
                  icon={<CheckCircle />}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 活动任务列表 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">
              活动任务
            </Typography>
            <Badge badgeContent={activeTasks.length} color="primary">
              <Assignment />
            </Badge>
          </Box>
          
          {activeTasks.length === 0 ? (
            <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
              暂无活动任务
            </Typography>
          ) : (
            <List>
              {activeTasks.map((task, index) => (
                <React.Fragment key={task.task_id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(task.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1">
                            {task.description}
                          </Typography>
                          <Chip 
                            label={task.status} 
                            color={getStatusColor(task.status)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            任务ID: {task.task_id}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            开始时间: {new Date(task.start_time).toLocaleString()}
                          </Typography>
                          {task.status === 'running' && (
                            <LinearProgress sx={{ mt: 1 }} />
                          )}
                        </Box>
                      }
                    />
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Terminal />}
                      onClick={() => {
                        setSelectedTask(task.task_id);
                        setLogDialogOpen(true);
                      }}
                    >
                      查看日志
                    </Button>
                  </ListItem>
                  {index < activeTasks.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* 浮动操作按钮 */}
      <Box sx={{ position: 'fixed', bottom: 24, right: 24, display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Tooltip title="远程唤醒电脑">
          <Fab 
            color="success" 
            onClick={() => setWakeDialogOpen(true)}
            disabled={!isConnected}
          >
            <PowerSettingsNew />
          </Fab>
        </Tooltip>
        <Tooltip title="远程关机/重启">
          <Fab 
            color="error" 
            onClick={() => setShutdownDialogOpen(true)}
            disabled={!isConnected}
          >
            <PowerOff />
          </Fab>
        </Tooltip>
        <Tooltip title="执行远程命令">
          <Fab 
            color="primary" 
            onClick={() => setCommandDialogOpen(true)}
            disabled={!isConnected}
          >
            <PlayArrow />
          </Fab>
        </Tooltip>
        <Tooltip title="查看所有日志">
          <Fab 
            color="secondary" 
            onClick={() => {
              setSelectedTask(null);
              setLogDialogOpen(true);
            }}
          >
            <Badge badgeContent={logs.length} color="error" max={99}>
              <Terminal />
            </Badge>
          </Fab>
        </Tooltip>
      </Box>

      {/* 对话框 */}
      <ShutdownComputerDialog />
      <WakeComputerDialog />
      <CommandExecutionDialog />
      <LogViewerDialog />
    </Box>
  );
};