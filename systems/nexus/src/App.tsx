import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import { useAppStore } from './services/simpleStore';
import Layout from './components/Layout';
import Dashboard from './features/dashboard/BasicDashboard';
import RAGSystem from './features/rag/BasicRAGSystem';
import ChangleeAssistant from './features/changlee/BasicChangleeAssistant';
import Chronicle from './features/chronicle/Chronicle';
import GenomeJigsaw from './features/genome/GenomeJigsaw';
import MolecularSimulation from './features/molecular/MolecularSimulation';
import Settings from './features/settings/Settings';
import { RemoteCommandCenter } from './components/remote/RemoteCommandCenter';

function App() {
  const { theme, fetchSystems } = useAppStore();

  // Create MUI theme based on store theme
  const muiTheme = createTheme({
    palette: {
      mode: theme.mode,
      primary: {
        main: theme.primary,
      },
      secondary: {
        main: theme.secondary,
      },
      background: {
        default: theme.background,
        paper: theme.surface,
      },
      text: {
        primary: theme.text,
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 700,
      },
      h2: {
        fontWeight: 600,
      },
      h3: {
        fontWeight: 600,
      },
    },
  });

  // Initialize app
  useEffect(() => {
    // Fetch system statuses on app start
    fetchSystems();

    // Set up periodic system status updates
    const interval = setInterval(() => {
      fetchSystems();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [fetchSystems]);

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/rag" element={<RAGSystem />} />
              <Route path="/changlee" element={<ChangleeAssistant />} />
              <Route path="/chronicle" element={<Chronicle />} />
              <Route path="/genome" element={<GenomeJigsaw />} />
              <Route path="/molecular" element={<MolecularSimulation />} />
              <Route path="/remote" element={<RemoteCommandCenter />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
