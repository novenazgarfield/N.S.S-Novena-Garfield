import React from 'react';
import { Box, Typography, Card, CardContent, Alert } from '@mui/material';
import { Science } from '@mui/icons-material';

const MolecularSimulation: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🧪 Molecular Simulation
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Molecular Dynamics Simulation Toolkit
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Alert severity="info" icon={<Science />}>
            Molecular Simulation interface is under development. This will provide GROMACS-based molecular dynamics simulation capabilities.
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MolecularSimulation;