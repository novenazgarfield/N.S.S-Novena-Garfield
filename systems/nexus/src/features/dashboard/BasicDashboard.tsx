import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Refresh,
  Memory,
  Speed,
  CheckCircle,
  Error,
  Warning,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppStore, SYSTEM_MODULES } from '../../services/simpleStore';

const BasicDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { systems, systemsLoading, fetchSystems } = useAppStore();
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 45,
    memory: 62,
    disk: 78,
    network: 125,
  });

  useEffect(() => {
    fetchSystems();
    
    // Simulate real-time metrics updates
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        cpu: Math.max(10, Math.min(90, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(20, Math.min(95, prev.memory + (Math.random() - 0.5) * 8)),
        disk: Math.max(30, Math.min(85, prev.disk + (Math.random() - 0.5) * 5)),
        network: Math.max(50, Math.min(200, prev.network + (Math.random() - 0.5) * 20)),
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchSystems]);

  const handleRefresh = async () => {
    await fetchSystems();
    console.log('System status refreshed');
  };

  const onlineSystems = systems.filter(s => s.status === 'online').length;
  const totalSystems = systems.length;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'offline':
        return <Error sx={{ color: 'error.main' }} />;
      case 'warning':
        return <Warning sx={{ color: 'warning.main' }} />;
      default:
        return <Warning sx={{ color: 'grey.500' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            🚀 NEXUS Command Center
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Research Workstation Interface - {onlineSystems}/{totalSystems} systems online
          </Typography>
        </Box>
        <IconButton onClick={handleRefresh} disabled={systemsLoading}>
          <Refresh />
        </IconButton>
      </Box>

      {/* System Metrics */}
      <Box sx={{ display: 'flex', gap: 3, mb: 4, flexWrap: 'wrap' }}>
        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Memory sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">CPU Usage</Typography>
            </Box>
            <Typography variant="h4" color="primary">
              {Math.round(systemMetrics.cpu)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={systemMetrics.cpu}
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>

        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Memory sx={{ mr: 1, color: 'secondary.main' }} />
              <Typography variant="h6">Memory</Typography>
            </Box>
            <Typography variant="h4" color="secondary">
              {Math.round(systemMetrics.memory)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={systemMetrics.memory}
              color="secondary"
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>

        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Memory sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6">Disk Usage</Typography>
            </Box>
            <Typography variant="h4" color="warning.main">
              {Math.round(systemMetrics.disk)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={systemMetrics.disk}
              color="warning"
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>

        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Speed sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6">Network</Typography>
            </Box>
            <Typography variant="h4" color="success.main">
              {Math.round(systemMetrics.network)} MB/s
            </Typography>
            <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
              +12% from last hour
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* System Status and Quick Actions */}
      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* System Status */}
        <Card sx={{ flex: 2, minWidth: 400 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            {systemsLoading ? (
              <LinearProgress sx={{ mb: 2 }} />
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {systems.map((system) => (
                  <Card 
                    key={system.id}
                    variant="outlined" 
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' }
                    }} 
                    onClick={() => {
                      const module = SYSTEM_MODULES.find(m => m.id === system.id);
                      if (module) navigate(module.path);
                    }}
                  >
                    <CardContent sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getStatusIcon(system.status)}
                          <Box sx={{ ml: 1 }}>
                            <Typography variant="subtitle2">{system.name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {system.description}
                            </Typography>
                          </Box>
                        </Box>
                        <Chip
                          label={system.status}
                          color={getStatusColor(system.status) as any}
                          size="small"
                        />
                      </Box>
                      {system.status === 'online' && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          Uptime: {system.uptime}%
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card sx={{ flex: 1, minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button
                variant="outlined"
                onClick={() => navigate('/rag')}
                fullWidth
              >
                Open RAG System
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/changlee')}
                fullWidth
              >
                Launch Changlee Assistant
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/genome')}
                fullWidth
              >
                Genome Analysis
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/molecular')}
                fullWidth
              >
                Molecular Simulation
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/settings')}
                fullWidth
              >
                System Settings
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default BasicDashboard;