import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  IconButton,
  CircularProgress,
  Divider,
  Paper,
} from '@mui/material';
import {
  Send,
  Psychology,
  Description,
  Refresh,
  Upload,
} from '@mui/icons-material';

const BasicRAGSystem: React.FC = () => {
  const [queries, setQueries] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);

  useEffect(() => {
    // Mock documents
    setDocuments([
      { id: '1', title: 'Research Paper 1', type: 'PDF', size: 1024, indexed: true },
      { id: '2', title: 'Lab Notes', type: 'TXT', size: 512, indexed: true },
      { id: '3', title: 'Experiment Results', type: 'CSV', size: 2048, indexed: true },
    ]);
  }, []);

  const handleSubmitQuery = async () => {
    if (currentQuery.trim()) {
      setIsLoading(true);
      // Mock query response
      const mockResponse = {
        id: Date.now().toString(),
        query: currentQuery,
        response: `This is a mock response to: "${currentQuery}". The RAG system would normally search through documents and provide relevant information based on the indexed content.`,
        timestamp: new Date(),
        sources: ['Research Paper 1', 'Lab Notes'],
        confidence: 0.85,
      };
      
      setTimeout(() => {
        setQueries(prev => [mockResponse, ...prev]);
        setCurrentQuery('');
        setIsLoading(false);
      }, 1000);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmitQuery();
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🧠 RAG System
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Retrieval-Augmented Generation AI
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Query Interface */}
        <Box sx={{ flex: 2, minWidth: 400 }}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ask a Question
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Enter your question here..."
                  value={currentQuery}
                  onChange={(e) => setCurrentQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                />
                <Button
                  variant="contained"
                  onClick={handleSubmitQuery}
                  disabled={isLoading || !currentQuery.trim()}
                  sx={{ minWidth: 100 }}
                >
                  {isLoading ? <CircularProgress size={24} /> : <Send />}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Query Results */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Query History
              </Typography>
              {queries.length === 0 ? (
                <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No queries yet. Ask your first question above!
                </Typography>
              ) : (
                <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
                  {queries.map((query) => (
                    <Paper key={query.id} sx={{ p: 2, mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Psychology sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="subtitle2" color="primary">
                          Query
                        </Typography>
                        <Chip
                          label={`${Math.round(query.confidence * 100)}% confidence`}
                          size="small"
                          color="success"
                          sx={{ ml: 'auto' }}
                        />
                      </Box>
                      <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                        {query.query}
                      </Typography>
                      
                      <Divider sx={{ my: 1 }} />
                      
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        {query.response}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Sources:
                        </Typography>
                        {query.sources.map((source: string, idx: number) => (
                          <Chip key={idx} label={source} size="small" variant="outlined" />
                        ))}
                      </Box>
                      
                      <Typography variant="caption" color="text.secondary">
                        {query.timestamp.toLocaleString()}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Document Library */}
        <Box sx={{ flex: 1, minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Document Library</Typography>
                <Box>
                  <IconButton onClick={() => console.log('Refresh documents')} disabled={isLoading}>
                    <Refresh />
                  </IconButton>
                  <IconButton>
                    <Upload />
                  </IconButton>
                </Box>
              </Box>
              
              <List>
                {documents.map((doc) => (
                  <ListItem
                    key={doc.id}
                    onClick={() => setSelectedDocument(doc)}
                    sx={{ 
                      cursor: 'pointer',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: selectedDocument?.id === doc.id ? 'action.selected' : 'transparent',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    <Description sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary={doc.title}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Chip label={doc.type} size="small" />
                          <Typography variant="caption">
                            {(doc.size / 1024).toFixed(1)} KB
                          </Typography>
                          {doc.indexed && (
                            <Chip label="Indexed" size="small" color="success" />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>

              {selectedDocument && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Selected Document
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedDocument.title}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    Type: {selectedDocument.type} | Size: {(selectedDocument.size / 1024).toFixed(1)} KB
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default BasicRAGSystem;