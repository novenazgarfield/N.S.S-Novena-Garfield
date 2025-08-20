import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Alert,
} from '@mui/material';
import { Settings as SettingsIcon, Palette, Notifications, Security } from '@mui/icons-material';
import { useAppStore } from '../../services/simpleStore';

const Settings: React.FC = () => {
  const { theme, setTheme } = useAppStore();

  const handleThemeChange = (field: string, value: any) => {
    setTheme({ [field]: value });
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          ⚙️ Settings
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Configure your NEXUS experience
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Appearance Settings */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Palette sx={{ mr: 2 }} />
              <Typography variant="h6">Appearance</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Theme Mode</InputLabel>
                <Select
                  value={theme.mode}
                  label="Theme Mode"
                  onChange={(e) => handleThemeChange('mode', e.target.value)}
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                </Select>
              </FormControl>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Primary Color
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {['#1976d2', '#2e7d32', '#ed6c02', '#d32f2f', '#7b1fa2'].map((color) => (
                    <Box
                      key={color}
                      sx={{
                        width: 40,
                        height: 40,
                        backgroundColor: color,
                        borderRadius: 1,
                        cursor: 'pointer',
                        border: theme.primary === color ? '3px solid white' : '1px solid #ccc',
                        boxShadow: theme.primary === color ? '0 0 0 2px ' + color : 'none',
                      }}
                      onClick={() => handleThemeChange('primary', color)}
                    />
                  ))}
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* System Settings */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <SettingsIcon sx={{ mr: 2 }} />
              <Typography variant="h6">System</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Auto-refresh system status"
              />
              
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Refresh Interval (seconds)
                </Typography>
                <Slider
                  defaultValue={30}
                  min={10}
                  max={300}
                  step={10}
                  marks={[
                    { value: 10, label: '10s' },
                    { value: 60, label: '1m' },
                    { value: 300, label: '5m' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>

              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable system notifications"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Notifications sx={{ mr: 2 }} />
              <Typography variant="h6">Notifications</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="System status alerts"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Task completion notifications"
              />
              <FormControlLabel
                control={<Switch />}
                label="Email notifications"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Browser notifications"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Security sx={{ mr: 2 }} />
              <Typography variant="h6">Security</Typography>
            </Box>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Security settings will be available in a future update.
            </Alert>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Button variant="outlined" disabled>
                Change Password
              </Button>
              <Button variant="outlined" disabled>
                Two-Factor Authentication
              </Button>
              <Button variant="outlined" disabled>
                API Key Management
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="contained" color="primary">
                Save Settings
              </Button>
              <Button variant="outlined">
                Reset to Defaults
              </Button>
              <Button variant="outlined" color="error">
                Clear All Data
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Settings;