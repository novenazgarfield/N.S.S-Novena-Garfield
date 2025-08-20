import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  Paper,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Send,
  Psychology,
  Description,
  Search,
  ExpandMore,
  Refresh,
  Upload,
} from '@mui/icons-material';
// import { useRAGStore } from '../../services/store';

const RAGSystem: React.FC = () => {
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
    ]);
  }, []);

  const handleSubmitQuery = async () => {
    if (currentQuery.trim()) {
      setIsLoading(true);
      // Mock query response
      const mockResponse = {
        id: Date.now().toString(),
        query: currentQuery,
        response: `This is a mock response to: "${currentQuery}". The RAG system would normally search through documents and provide relevant information.`,
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
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🧠 RAG System
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Retrieval-Augmented Generation AI System
        </Typography>
      </Box>

      {/* Query Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Ask a Question
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
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
              startIcon={isLoading ? <CircularProgress size={20} /> : <Send />}
              onClick={handleSubmitQuery}
              disabled={isLoading || !currentQuery.trim()}
              sx={{ minWidth: 120 }}
            >
              {isLoading ? 'Processing...' : 'Ask'}
            </Button>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Press Enter to submit, Shift+Enter for new line
          </Typography>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* Query Results */}
        <Box sx={{ flex: 2 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Query Results</Typography>
                <Chip label={`${queries.length} queries`} variant="outlined" />
              </Box>

              {queries.length === 0 ? (
                <Alert severity="info" icon={<Psychology />}>
                  No queries yet. Ask your first question above!
                </Alert>
              ) : (
                <List>
                  {queries.map((query, index) => (
                    <React.Fragment key={query.id || index}>
                      <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                        <ListItemText
                          primary={
                            <Box sx={{ mb: 1 }}>
                              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                Q: {query.query}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Paper sx={{ p: 2, bgcolor: 'action.hover', mb: 1 }}>
                                <Typography variant="body2">
                                  A: {query.response}
                                </Typography>
                              </Paper>
                              {query.sources && query.sources.length > 0 && (
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                  <Typography variant="caption" color="text.secondary">
                                    Sources:
                                  </Typography>
                                  {query.sources.map((source: string, idx: number) => (
                                    <Chip
                                      key={idx}
                                      label={source}
                                      size="small"
                                      variant="outlined"
                                      color="primary"
                                    />
                                  ))}
                                </Box>
                              )}
                              <Typography variant="caption" color="text.secondary">
                                {query.timestamp ? new Date(query.timestamp).toLocaleString() : 'Just now'}
                                {query.confidence && ` • Confidence: ${(query.confidence * 100).toFixed(1)}%`}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < queries.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Document Library */}
        <Box sx={{ flex: 1 }}>
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

              {documents.length === 0 ? (
                <Alert severity="info" icon={<Description />}>
                  No documents found. Upload documents to enable RAG functionality.
                </Alert>
              ) : (
                <List>
                  {documents.map((doc, index) => (
                    <ListItem
                      key={doc.id || index}
                      button
                      onClick={() => setSelectedDocument(doc)}
                      selected={selectedDocument?.id === doc.id}
                    >
                      <ListItemText
                        primary={doc.title || `Document ${index + 1}`}
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              {doc.type || 'Unknown type'}
                              {doc.size && ` • ${(doc.size / 1024).toFixed(1)} KB`}
                            </Typography>
                            {doc.indexed !== undefined && (
                              <Chip
                                label={doc.indexed ? 'Indexed' : 'Pending'}
                                size="small"
                                color={doc.indexed ? 'success' : 'warning'}
                                variant="outlined"
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>

          {/* Document Details */}
          {selectedDocument && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Document Details
                </Typography>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="subtitle2">
                      {selectedDocument.title || 'Untitled Document'}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary">
                      {selectedDocument.content || 'No content preview available'}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Type: {selectedDocument.type || 'Unknown'}
                      </Typography>
                      <br />
                      <Typography variant="caption" color="text.secondary">
                        Size: {selectedDocument.size ? `${(selectedDocument.size / 1024).toFixed(1)} KB` : 'Unknown'}
                      </Typography>
                      <br />
                      <Typography variant="caption" color="text.secondary">
                        Uploaded: {selectedDocument.uploadDate ? new Date(selectedDocument.uploadDate).toLocaleString() : 'Unknown'}
                      </Typography>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default RAGSystem;