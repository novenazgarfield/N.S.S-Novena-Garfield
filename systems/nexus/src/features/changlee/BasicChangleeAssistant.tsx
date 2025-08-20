import React, { useState, useEffect, useRef } from 'react';
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
  IconButton,
  Paper,
  Avatar,
  Chip,
} from '@mui/material';
import {
  Send,
  Mic,
  MicOff,
  SmartToy,
  Person,
  Add,
  Settings,
} from '@mui/icons-material';

const BasicChangleeAssistant: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSession, setCurrentSession] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Mock sessions
    const mockSessions = [
      { id: '1', title: 'General Chat', messages: [], createdAt: new Date() },
      { id: '2', title: 'Research Help', messages: [], createdAt: new Date() },
    ];
    setSessions(mockSessions);
    setCurrentSession(mockSessions[0]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      const userMessage = {
        id: Date.now().toString(),
        type: 'user',
        content: inputMessage,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      setIsTyping(true);

      // Mock AI response
      setTimeout(() => {
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `Hello! I'm Changlee, your AI assistant. You said: "${inputMessage}". How can I help you with your research today?`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);
      }, 1500);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewSession = () => {
    const newSession = {
      id: Date.now().toString(),
      title: `Chat ${sessions.length + 1}`,
      messages: [],
      createdAt: new Date(),
    };
    setSessions(prev => [...prev, newSession]);
    setCurrentSession(newSession);
    setMessages([]);
  };

  const toggleListening = () => {
    setIsListening(!isListening);
    // Mock voice recognition
    if (!isListening) {
      setTimeout(() => {
        setInputMessage('This is a mock voice input');
        setIsListening(false);
      }, 2000);
    }
  };

  return (
    <Box sx={{ p: 3, height: 'calc(100vh - 100px)' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🤖 Changlee Assistant
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI Desktop Assistant
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 3, height: '100%' }}>
        {/* Session List */}
        <Box sx={{ width: 300 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Sessions</Typography>
                <IconButton onClick={handleNewSession} size="small">
                  <Add />
                </IconButton>
              </Box>
              
              <List>
                {sessions.map((session) => (
                  <ListItem
                    key={session.id}
                    onClick={() => {
                      setCurrentSession(session);
                      setMessages(session.messages || []);
                    }}
                    sx={{
                      cursor: 'pointer',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: currentSession?.id === session.id ? 'action.selected' : 'transparent',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    <ListItemText
                      primary={session.title}
                      secondary={session.createdAt.toLocaleDateString()}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* Chat Interface */}
        <Box sx={{ flex: 1 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Chat Header */}
            <CardContent sx={{ borderBottom: 1, borderColor: 'divider', py: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">
                  {currentSession?.title || 'Select a session'}
                </Typography>
                <Box>
                  <Chip
                    icon={<SmartToy />}
                    label="Changlee Online"
                    color="success"
                    size="small"
                  />
                  <IconButton sx={{ ml: 1 }}>
                    <Settings />
                  </IconButton>
                </Box>
              </Box>
            </CardContent>

            {/* Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              {messages.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    Start a conversation with Changlee
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Ask questions, get help with research, or just chat!
                  </Typography>
                </Box>
              ) : (
                <>
                  {messages.map((message) => (
                    <Box
                      key={message.id}
                      sx={{
                        display: 'flex',
                        mb: 2,
                        justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                      }}
                    >
                      <Box sx={{ display: 'flex', maxWidth: '70%', alignItems: 'flex-start' }}>
                        {message.type === 'assistant' && (
                          <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                            <SmartToy />
                          </Avatar>
                        )}
                        <Paper
                          sx={{
                            p: 2,
                            bgcolor: message.type === 'user' ? 'primary.main' : 'background.paper',
                            color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                          }}
                        >
                          <Typography variant="body1">{message.content}</Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              display: 'block',
                              mt: 1,
                              opacity: 0.7,
                            }}
                          >
                            {message.timestamp.toLocaleTimeString()}
                          </Typography>
                        </Paper>
                        {message.type === 'user' && (
                          <Avatar sx={{ ml: 1, bgcolor: 'secondary.main' }}>
                            <Person />
                          </Avatar>
                        )}
                      </Box>
                    </Box>
                  ))}
                  
                  {isTyping && (
                    <Box sx={{ display: 'flex', mb: 2 }}>
                      <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                        <SmartToy />
                      </Avatar>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Changlee is typing...
                        </Typography>
                      </Paper>
                    </Box>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </Box>

            {/* Input */}
            <CardContent sx={{ borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  placeholder="Type your message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isTyping}
                />
                <IconButton
                  onClick={toggleListening}
                  color={isListening ? 'secondary' : 'default'}
                  disabled={isTyping}
                >
                  {isListening ? <MicOff /> : <Mic />}
                </IconButton>
                <Button
                  variant="contained"
                  onClick={handleSendMessage}
                  disabled={isTyping || !inputMessage.trim()}
                  sx={{ minWidth: 100 }}
                >
                  <Send />
                </Button>
              </Box>
              {isListening && (
                <Typography variant="caption" color="secondary" sx={{ mt: 1, display: 'block' }}>
                  Listening... Speak now
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default BasicChangleeAssistant;