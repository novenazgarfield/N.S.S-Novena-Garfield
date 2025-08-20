import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Psychology,
  SmartToy,
  MenuBook,
  Biotech,
  Science,
  Refresh,
  Launch,
  TrendingUp,
  Memory,
  Storage,
  NetworkCheck,
  Speed,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppStore, SYSTEM_MODULES } from '../../services/simpleStore';
import { SystemStatus } from '../../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { systems, systemsLoading, fetchSystems } = useAppStore();
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 45,
    memory: 62,
    disk: 78,
    network: { upload: 1.2, download: 5.8 }
  });

  useEffect(() => {
    // Simulate system metrics updates
    const interval = setInterval(() => {
      setSystemMetrics({
        cpu: Math.floor(Math.random() * 100),
        memory: Math.floor(Math.random() * 100),
        disk: 78 + Math.floor(Math.random() * 10),
        network: {
          upload: Math.random() * 10,
          download: Math.random() * 20
        }
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'success';
      case 'offline': return 'error';
      case 'maintenance': return 'warning';
      default: return 'default';
    }
  };

  const getSystemIcon = (systemId: string) => {
    const iconMap: { [key: string]: React.ComponentType } = {
      dashboard: DashboardIcon,
      rag: Psychology,
      changlee: SmartToy,
      chronicle: MenuBook,
      genome: Biotech,
      molecular: Science,
    };
    return iconMap[systemId] || DashboardIcon;
  };

  const handleSystemClick = (systemId: string) => {
    const module = SYSTEM_MODULES.find(m => m.id === systemId);
    if (module) {
      navigate(module.path);
    }
  };

  const handleRefresh = async () => {
    await fetchSystems();
    console.log('System status refreshed');
  };

  const onlineSystems = systems.filter(s => s.status === 'online').length;
  const totalSystems = systems.length;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            🚀 NEXUS Command Center
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Unified interface for all Research Workstation systems
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={handleRefresh}
          disabled={systemsLoading}
        >
          Refresh Status
        </Button>
      </Box>

      {/* System Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <DashboardIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">Systems Online</Typography>
                  <Typography variant="h4" color="primary">
                    {onlineSystems}/{totalSystems}
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(onlineSystems / totalSystems) * 100} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <Speed />
                </Avatar>
                <Box>
                  <Typography variant="h6">CPU Usage</Typography>
                  <Typography variant="h4" color="success.main">
                    {systemMetrics.cpu}%
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={systemMetrics.cpu} 
                color="success"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <Memory />
                </Avatar>
                <Box>
                  <Typography variant="h6">Memory</Typography>
                  <Typography variant="h4" color="warning.main">
                    {systemMetrics.memory}%
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={systemMetrics.memory} 
                color="warning"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                  <NetworkCheck />
                </Avatar>
                <Box>
                  <Typography variant="h6">Network</Typography>
                  <Typography variant="body2" color="info.main">
                    ↑ {systemMetrics.network.upload.toFixed(1)} MB/s
                  </Typography>
                  <Typography variant="body2" color="info.main">
                    ↓ {systemMetrics.network.download.toFixed(1)} MB/s
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* System Status */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">System Status</Typography>
                {systemsLoading && <CircularProgress size={20} />}
              </Box>
              
              {systems.length === 0 ? (
                <Alert severity="info">
                  No systems detected. Click refresh to check system status.
                </Alert>
              ) : (
                <List>
                  {SYSTEM_MODULES.map((module, index) => {
                    const system = systems.find(s => s.id === module.id);
                    const status = system?.status || 'offline';
                    const IconComponent = getSystemIcon(module.id);

                    return (
                      <React.Fragment key={module.id}>
                        <ListItem
                          sx={{ 
                            cursor: 'pointer',
                            borderRadius: 2,
                            '&:hover': { bgcolor: 'action.hover' }
                          }}
                          onClick={() => handleSystemClick(module.id)}
                        >
                          <ListItemIcon>
                            <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
                              <IconComponent />
                            </Avatar>
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                  {module.name}
                                </Typography>
                                <Chip
                                  label={status}
                                  color={getStatusColor(status) as any}
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {module.description}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  Version {module.version} • {module.features.join(', ')}
                                </Typography>
                              </Box>
                            }
                          />
                          <IconButton>
                            <Launch />
                          </IconButton>
                        </ListItem>
                        {index < SYSTEM_MODULES.length - 1 && <Divider />}
                      </React.Fragment>
                    );
                  })}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions & Recent Activity */}
        <Grid item xs={12} lg={4}>
          <Grid container spacing={3}>
            {/* Quick Actions */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                      variant="outlined"
                      startIcon={<Psychology />}
                      onClick={() => navigate('/rag')}
                      fullWidth
                    >
                      Ask RAG System
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<SmartToy />}
                      onClick={() => navigate('/changlee')}
                      fullWidth
                    >
                      Chat with Changlee
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Biotech />}
                      onClick={() => navigate('/genome')}
                      fullWidth
                    >
                      Start Genome Analysis
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Science />}
                      onClick={() => navigate('/molecular')}
                      fullWidth
                    >
                      Run MD Simulation
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* System Health */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    System Health
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">CPU</Typography>
                        <Typography variant="body2">{systemMetrics.cpu}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={systemMetrics.cpu} 
                        color={systemMetrics.cpu > 80 ? 'error' : 'success'}
                      />
                    </Box>
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Memory</Typography>
                        <Typography variant="body2">{systemMetrics.memory}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={systemMetrics.memory} 
                        color={systemMetrics.memory > 80 ? 'error' : 'warning'}
                      />
                    </Box>
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Disk</Typography>
                        <Typography variant="body2">{systemMetrics.disk}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={systemMetrics.disk} 
                        color={systemMetrics.disk > 90 ? 'error' : 'info'}
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;