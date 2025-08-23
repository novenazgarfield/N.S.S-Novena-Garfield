import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  Fab,
  Badge
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Download,
  Settings,
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh,
  FolderOpen,
  Terminal,
  CloudDownload,
  Build,
  Launch,
  ExpandMore,
  Add,
  Delete,
  Edit
} from '@mui/icons-material';

import { systemsConfig } from './systems.json';
import { EnvironmentChecker } from '../../services/env_checker';
import { DeploymentService } from '../../services/deployment_service';

interface SystemStatus {
  name: string;
  status: 'missing_deps' | 'not_installed' | 'installed' | 'running' | 'error';
  dependencies: DependencyStatus[];
  installPath?: string;
  version?: string;
  lastUpdated?: Date;
}

interface DependencyStatus {
  name: string;
  required: boolean;
  installed: boolean;
  version?: string;
  installPath?: string;
}

interface InstallWizardStep {
  title: string;
  description: string;
  component: React.ReactNode;
  completed: boolean;
}

export const SystemManager: React.FC = () => {
  const [systems, setSystems] = useState<SystemStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  const [installDialogOpen, setInstallDialogOpen] = useState(false);
  const [dependencyDialogOpen, setDependencyDialogOpen] = useState(false);
  const [selectedDependency, setSelectedDependency] = useState<string | null>(null);
  const [customInstallPath, setCustomInstallPath] = useState('');
  const [installProgress, setInstallProgress] = useState(0);
  const [installLogs, setInstallLogs] = useState<string[]>([]);
  const [activeStep, setActiveStep] = useState(0);

  const envChecker = new EnvironmentChecker();
  const deploymentService = new DeploymentService();

  useEffect(() => {
    checkAllSystems();
  }, []);

  const checkAllSystems = async () => {
    setLoading(true);
    try {
      const systemStatuses: SystemStatus[] = [];
      
      for (const system of systemsConfig.systems) {
        const dependencies = await Promise.all(
          system.dependencies.map(async (dep) => ({
            name: dep.name,
            required: dep.required,
            installed: await envChecker.checkDependency(dep.name),
            version: await envChecker.getDependencyVersion(dep.name),
            installPath: await envChecker.getDependencyPath(dep.name)
          }))
        );

        const missingRequiredDeps = dependencies.filter(dep => dep.required && !dep.installed);
        const isInstalled = await deploymentService.isSystemInstalled(system.name);
        
        let status: SystemStatus['status'] = 'not_installed';
        if (missingRequiredDeps.length > 0) {
          status = 'missing_deps';
        } else if (isInstalled) {
          const isRunning = await deploymentService.isSystemRunning(system.name);
          status = isRunning ? 'running' : 'installed';
        }

        systemStatuses.push({
          name: system.name,
          status,
          dependencies,
          installPath: await deploymentService.getSystemPath(system.name),
          version: await deploymentService.getSystemVersion(system.name),
          lastUpdated: await deploymentService.getLastUpdated(system.name)
        });
      }

      setSystems(systemStatuses);
    } catch (error) {
      console.error('检查系统状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: SystemStatus['status']) => {
    switch (status) {
      case 'running': return 'success';
      case 'installed': return 'info';
      case 'not_installed': return 'default';
      case 'missing_deps': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: SystemStatus['status']) => {
    switch (status) {
      case 'running': return '运行中';
      case 'installed': return '已安装';
      case 'not_installed': return '未安装';
      case 'missing_deps': return '依赖缺失';
      case 'error': return '错误';
      default: return '未知';
    }
  };

  const getStatusIcon = (status: SystemStatus['status']) => {
    switch (status) {
      case 'running': return <CheckCircle color="success" />;
      case 'installed': return <Info color="info" />;
      case 'not_installed': return <CloudDownload color="disabled" />;
      case 'missing_deps': return <Warning color="warning" />;
      case 'error': return <Error color="error" />;
      default: return <Info />;
    }
  };

  const handleInstallDependency = async (dependencyName: string, installPath: string) => {
    try {
      setInstallProgress(0);
      setInstallLogs([]);
      
      const success = await deploymentService.ensureDependency(
        dependencyName,
        installPath,
        (progress) => setInstallProgress(progress),
        (log) => setInstallLogs(prev => [...prev, log])
      );

      if (success) {
        setDependencyDialogOpen(false);
        await checkAllSystems();
      }
    } catch (error) {
      console.error('安装依赖失败:', error);
      setInstallLogs(prev => [...prev, `错误: ${error}`]);
    }
  };

  const handleInstallSystem = async (systemName: string) => {
    try {
      setInstallProgress(0);
      setInstallLogs([]);
      
      const success = await deploymentService.installSystem(
        systemName,
        (progress) => setInstallProgress(progress),
        (log) => setInstallLogs(prev => [...prev, log])
      );

      if (success) {
        setInstallDialogOpen(false);
        await checkAllSystems();
      }
    } catch (error) {
      console.error('安装系统失败:', error);
      setInstallLogs(prev => [...prev, `错误: ${error}`]);
    }
  };

  const handleLaunchSystem = async (systemName: string) => {
    try {
      await deploymentService.launchSystem(systemName);
      await checkAllSystems();
    } catch (error) {
      console.error('启动系统失败:', error);
    }
  };

  const handleStopSystem = async (systemName: string) => {
    try {
      await deploymentService.stopSystem(systemName);
      await checkAllSystems();
    } catch (error) {
      console.error('停止系统失败:', error);
    }
  };

  const DependencyInstallWizard = () => {
    const steps: InstallWizardStep[] = [
      {
        title: '选择安装路径',
        description: '请选择依赖项的安装位置',
        component: (
          <Box>
            <TextField
              fullWidth
              label="安装路径"
              value={customInstallPath}
              onChange={(e) => setCustomInstallPath(e.target.value)}
              placeholder="例如: C:\\Tools\\Conda"
              InputProps={{
                endAdornment: (
                  <IconButton onClick={() => {
                    // 触发文件夹选择对话框
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.webkitdirectory = true;
                    input.onchange = (e) => {
                      const files = (e.target as HTMLInputElement).files;
                      if (files && files.length > 0) {
                        setCustomInstallPath(files[0].webkitRelativePath.split('/')[0]);
                      }
                    };
                    input.click();
                  }}>
                    <FolderOpen />
                  </IconButton>
                )
              }}
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                建议选择一个专用的工具目录，避免与系统文件混合。
                安装过程可能需要管理员权限。
              </Typography>
            </Alert>
          </Box>
        ),
        completed: customInstallPath.length > 0
      },
      {
        title: '确认安装',
        description: '确认安装信息并开始安装',
        component: (
          <Box>
            <Typography variant="h6" gutterBottom>
              安装信息确认
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="依赖项"
                  secondary={selectedDependency}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="安装路径"
                  secondary={customInstallPath}
                />
              </ListItem>
            </List>
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                安装过程将自动下载并配置所需的依赖项。
                请确保网络连接正常，并准备好提供管理员权限。
              </Typography>
            </Alert>
          </Box>
        ),
        completed: true
      }
    ];

    return (
      <Dialog
        open={dependencyDialogOpen}
        onClose={() => setDependencyDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Build />
            依赖安装向导 - {selectedDependency}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.title}>
                <StepLabel>
                  {step.title}
                </StepLabel>
                <StepContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {step.description}
                  </Typography>
                  {step.component}
                  <Box sx={{ mb: 2, mt: 2 }}>
                    <Button
                      variant="contained"
                      onClick={() => {
                        if (index === steps.length - 1) {
                          handleInstallDependency(selectedDependency!, customInstallPath);
                        } else {
                          setActiveStep(index + 1);
                        }
                      }}
                      disabled={!step.completed}
                      sx={{ mr: 1 }}
                    >
                      {index === steps.length - 1 ? '开始安装' : '下一步'}
                    </Button>
                    <Button
                      disabled={index === 0}
                      onClick={() => setActiveStep(index - 1)}
                    >
                      上一步
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>

          {installProgress > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                安装进度: {installProgress}%
              </Typography>
              <LinearProgress variant="determinate" value={installProgress} />
              
              <Box sx={{ mt: 2, maxHeight: 200, overflow: 'auto' }}>
                {installLogs.map((log, index) => (
                  <Typography
                    key={index}
                    variant="body2"
                    component="pre"
                    sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                  >
                    {log}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDependencyDialogOpen(false)}>
            取消
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const SystemInstallDialog = () => (
    <Dialog
      open={installDialogOpen}
      onClose={() => setInstallDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Download />
          安装系统 - {selectedSystem}
        </Box>
      </DialogTitle>
      <DialogContent>
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            系统将自动从GitHub克隆代码并安装所有依赖项。
            请确保网络连接正常，安装过程可能需要几分钟时间。
          </Typography>
        </Alert>

        {installProgress > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              安装进度: {installProgress}%
            </Typography>
            <LinearProgress variant="determinate" value={installProgress} />
          </Box>
        )}

        <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
          {installLogs.map((log, index) => (
            <Typography
              key={index}
              variant="body2"
              component="pre"
              sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
            >
              {log}
            </Typography>
          ))}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setInstallDialogOpen(false)}>
          取消
        </Button>
        <Button
          variant="contained"
          onClick={() => handleInstallSystem(selectedSystem!)}
          disabled={installProgress > 0}
        >
          开始安装
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Box textAlign="center">
          <LinearProgress sx={{ mb: 2, width: 200 }} />
          <Typography>正在检查系统状态...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          系统部署与管理
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={checkAllSystems}
        >
          刷新状态
        </Button>
      </Box>

      <Box display="grid" gridTemplateColumns="repeat(auto-fill, minmax(400px, 1fr))" gap={3}>
        {systems.map((system) => (
          <Card key={system.name} elevation={2}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {system.name}
                  </Typography>
                  <Chip
                    icon={getStatusIcon(system.status)}
                    label={getStatusText(system.status)}
                    color={getStatusColor(system.status)}
                    size="small"
                  />
                </Box>
                <Box display="flex" gap={1}>
                  {system.status === 'missing_deps' && (
                    <Tooltip title="环境初始化">
                      <IconButton
                        color="warning"
                        onClick={() => {
                          setSelectedSystem(system.name);
                          // 找到第一个缺失的必需依赖
                          const missingDep = system.dependencies.find(dep => dep.required && !dep.installed);
                          if (missingDep) {
                            setSelectedDependency(missingDep.name);
                            setCustomInstallPath('');
                            setActiveStep(0);
                            setDependencyDialogOpen(true);
                          }
                        }}
                      >
                        <Build />
                      </IconButton>
                    </Tooltip>
                  )}
                  {system.status === 'not_installed' && (
                    <Tooltip title="安装系统">
                      <IconButton
                        color="primary"
                        onClick={() => {
                          setSelectedSystem(system.name);
                          setInstallDialogOpen(true);
                        }}
                      >
                        <Download />
                      </IconButton>
                    </Tooltip>
                  )}
                  {system.status === 'installed' && (
                    <Tooltip title="启动系统">
                      <IconButton
                        color="success"
                        onClick={() => handleLaunchSystem(system.name)}
                      >
                        <Launch />
                      </IconButton>
                    </Tooltip>
                  )}
                  {system.status === 'running' && (
                    <Tooltip title="停止系统">
                      <IconButton
                        color="error"
                        onClick={() => handleStopSystem(system.name)}
                      >
                        <Stop />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Box>

              {system.version && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  版本: {system.version}
                </Typography>
              )}

              {system.installPath && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  路径: {system.installPath}
                </Typography>
              )}

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="body2">
                    依赖项 ({system.dependencies.filter(dep => dep.installed).length}/{system.dependencies.length})
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {system.dependencies.map((dep) => (
                      <ListItem key={dep.name}>
                        <ListItemIcon>
                          {dep.installed ? (
                            <CheckCircle color="success" fontSize="small" />
                          ) : (
                            <Error color={dep.required ? 'error' : 'disabled'} fontSize="small" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={dep.name}
                          secondary={dep.version || (dep.required ? '必需' : '可选')}
                        />
                        {!dep.installed && dep.required && (
                          <ListItemSecondaryAction>
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedDependency(dep.name);
                                setCustomInstallPath('');
                                setActiveStep(0);
                                setDependencyDialogOpen(true);
                              }}
                            >
                              <Download fontSize="small" />
                            </IconButton>
                          </ListItemSecondaryAction>
                        )}
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* 浮动操作按钮 */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => {
          // 打开系统添加对话框
        }}
      >
        <Add />
      </Fab>

      <DependencyInstallWizard />
      <SystemInstallDialog />
    </Box>
  );
};