import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Psychology,
  SmartToy,
  MenuBook,
  Biotech,
  Science,
  Settings,
  Notifications,
  AccountCircle,
  Brightness4,
  Brightness7,
  ChevronLeft,
  Rocket,
  Computer,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppStore, SYSTEM_MODULES } from '../services/simpleStore';

const DRAWER_WIDTH = 280;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  
  const {
    sidebarOpen,
    setSidebarOpen,
    theme: appTheme,
    setTheme,
    systems,
  } = useAppStore();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null);

  const handleDrawerToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleThemeToggle = () => {
    setTheme({ mode: appTheme.mode === 'dark' ? 'light' : 'dark' });
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  const getSystemStatus = (systemId: string) => {
    const system = systems.find(s => s.id === systemId);
    return system?.status || 'offline';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'success';
      case 'offline': return 'error';
      case 'maintenance': return 'warning';
      default: return 'default';
    }
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Dashboard, path: '/' },
    { id: 'rag', label: 'RAG System', icon: Psychology, path: '/rag' },
    { id: 'changlee', label: 'Changlee Assistant', icon: SmartToy, path: '/changlee' },
    { id: 'chronicle', label: 'Chronicle', icon: MenuBook, path: '/chronicle' },
    { id: 'genome', label: 'Genome Jigsaw', icon: Biotech, path: '/genome' },
    { id: 'molecular', label: 'Molecular Simulation', icon: Science, path: '/molecular' },
    { id: 'remote', label: '远程指挥中心', icon: Computer, path: '/remote', highlight: true },
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo and Title */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Rocket sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h6" component="div" sx={{ fontWeight: 700 }}>
            NEXUS
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Command Center
          </Typography>
        </Box>
      </Box>

      <Divider />

      {/* Navigation */}
      <List sx={{ flex: 1, pt: 1 }}>
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path;
          const status = getSystemStatus(item.id);
          const IconComponent = item.icon;

          return (
            <ListItem key={item.id} disablePadding sx={{ px: 1, mb: 0.5 }}>
              <ListItemButton
                selected={isActive}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  ...(item.highlight && {
                    background: 'linear-gradient(45deg, #FF6B6B 30%, #4ECDC4 90%)',
                    color: 'white',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #FF5252 30%, #26C6DA 90%)',
                    },
                  }),
                  '&.Mui-selected': {
                    backgroundColor: item.highlight ? 'transparent' : 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: item.highlight ? 'transparent' : 'primary.dark',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ color: (isActive || item.highlight) ? 'inherit' : 'text.secondary' }}>
                  <IconComponent />
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: isActive ? 600 : 400,
                    color: item.highlight ? 'inherit' : undefined,
                  }}
                />
                {item.id === 'remote' ? (
                  <Chip
                    size="small"
                    label="NEW"
                    color="warning"
                    sx={{ 
                      fontSize: '0.6rem', 
                      height: 18,
                      backgroundColor: '#FFD700',
                      color: '#000',
                      fontWeight: 'bold',
                      '& .MuiChip-label': { px: 0.5 }
                    }}
                  />
                ) : (
                  <Chip
                    size="small"
                    label={status}
                    color={getStatusColor(status) as any}
                    variant="outlined"
                    sx={{ 
                      fontSize: '0.7rem', 
                      height: 20,
                      '& .MuiChip-label': { px: 1 }
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      {/* Settings */}
      <List>
        <ListItem disablePadding sx={{ px: 1 }}>
          <ListItemButton
            onClick={() => navigate('/settings')}
            sx={{ borderRadius: 2 }}
          >
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: sidebarOpen ? `calc(100% - ${DRAWER_WIDTH}px)` : '100%' },
          ml: { md: sidebarOpen ? `${DRAWER_WIDTH}px` : 0 },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            {sidebarOpen ? <ChevronLeft /> : <MenuIcon />}
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Research Workstation
          </Typography>

          {/* Theme Toggle */}
          <IconButton color="inherit" onClick={handleThemeToggle}>
            {appTheme.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>

          {/* Notifications */}
          <IconButton color="inherit" onClick={handleNotificationMenuOpen}>
            <Badge badgeContent={0} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          {/* Profile */}
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="primary-search-account-menu"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: sidebarOpen ? DRAWER_WIDTH : 0 }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          open={sidebarOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: sidebarOpen ? `calc(100% - ${DRAWER_WIDTH}px)` : '100%' },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        {children}
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        onClick={handleProfileMenuClose}
      >
        <MenuItem onClick={() => navigate('/settings')}>
          <Settings sx={{ mr: 2 }} />
          Settings
        </MenuItem>
        <MenuItem>
          <AccountCircle sx={{ mr: 2 }} />
          Profile
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleNotificationMenuClose}
        PaperProps={{
          sx: { width: 320, maxHeight: 400 }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6">Notifications</Typography>
        </Box>
        <Divider />
        <MenuItem>
          <Typography color="text.secondary">No notifications</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout;