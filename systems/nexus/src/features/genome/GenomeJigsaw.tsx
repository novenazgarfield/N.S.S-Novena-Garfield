import React from 'react';
import { Box, Typography, Card, CardContent, Alert } from '@mui/material';
import { Biotech } from '@mui/icons-material';

const GenomeJigsaw: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🧬 Genome Jigsaw
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Bacterial Genome Analysis Pipeline
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Alert severity="info" icon={<Biotech />}>
            Genome Jigsaw interface is under development. This will provide automated bacterial genome sequencing analysis capabilities.
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};

export default GenomeJigsaw;