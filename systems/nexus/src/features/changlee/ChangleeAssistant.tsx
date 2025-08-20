import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  Paper,
  Avatar,
  Chip,
  IconButton,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Mic,
  Stop,
  VolumeUp,
  Settings,
} from '@mui/icons-material';
// import { useChangleeStore } from '../../services/store';

const ChangleeAssistant: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSession, setCurrentSession] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Mock sessions
    setSessions([
      { id: '1', title: 'General Chat', messages: [] },
      { id: '2', title: 'Research Help', messages: [] },
    ]);
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

  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      if (isListening) {
        recognition.stop();
      } else {
        recognition.start();
      }
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🤖 Changlee Assistant
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Your AI Desktop Assistant
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 3, height: 'calc(100vh - 200px)' }}>
        {/* Chat Sessions */}
        <Box sx={{ width: 280 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Chat Sessions</Typography>
                <Button size="small" variant="outlined">
                  New Chat
                </Button>
              </Box>
              <List>
                {sessions.map((session) => (
                  <ListItem
                    key={session.id}
                    component="div"
                    onClick={() => setCurrentSession(session)}
                    sx={{ 
                      borderRadius: 1, 
                      mb: 1, 
                      cursor: 'pointer',
                      backgroundColor: currentSession?.id === session.id ? 'action.selected' : 'transparent',
                      '&:hover': { backgroundColor: 'action.hover' }
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle2">
                        {session.title || 'New Conversation'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {session.messages?.length || 0} messages
                      </Typography>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* Chat Interface */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Chat Header */}
            <CardContent sx={{ borderBottom: 1, borderColor: 'divider', py: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <SmartToy />
                  </Avatar>
                  <Box>
                    <Typography variant="h6">Changlee</Typography>
                    <Chip 
                      label="Online" 
                      color="success" 
                      size="small" 
                      variant="outlined"
                    />
                  </Box>
                </Box>
                <IconButton>
                  <Settings />
                </IconButton>
              </Box>
            </CardContent>

            {/* Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              {messages.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    Start a conversation with Changlee
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Ask questions, get help, or just chat!
                  </Typography>
                </Box>
              ) : (
                <List>
                  {messages.map((message, index) => (
                    <ListItem key={message.id || index} sx={{ px: 0, py: 1 }}>
                      <Box sx={{ 
                        display: 'flex', 
                        width: '100%',
                        justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
                      }}>
                        <Box sx={{ 
                          display: 'flex', 
                          alignItems: 'flex-start', 
                          gap: 1,
                          maxWidth: '70%',
                          flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
                        }}>
                          <Avatar sx={{ 
                            bgcolor: message.type === 'user' ? 'secondary.main' : 'primary.main',
                            width: 32, 
                            height: 32 
                          }}>
                            {message.type === 'user' ? <Person /> : <SmartToy />}
                          </Avatar>
                          <Paper sx={{ 
                            p: 2, 
                            bgcolor: message.type === 'user' ? 'primary.main' : 'background.paper',
                            color: message.type === 'user' ? 'primary.contrastText' : 'text.primary'
                          }}>
                            <Typography variant="body2">
                              {message.content}
                            </Typography>
                            <Typography variant="caption" sx={{ 
                              opacity: 0.7,
                              display: 'block',
                              mt: 1
                            }}>
                              {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'Now'}
                            </Typography>
                          </Paper>
                        </Box>
                      </Box>
                    </ListItem>
                  ))}
                  {isTyping && (
                    <ListItem sx={{ px: 0, py: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                          <SmartToy />
                        </Avatar>
                        <Paper sx={{ p: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CircularProgress size={16} />
                            <Typography variant="body2" color="text.secondary">
                              Changlee is typing...
                            </Typography>
                          </Box>
                        </Paper>
                      </Box>
                    </ListItem>
                  )}
                </List>
              )}
              <div ref={messagesEndRef} />
            </Box>

            {/* Input Area */}
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
                  color={isListening ? 'secondary' : 'default'}
                  onClick={handleVoiceInput}
                  disabled={isTyping}
                >
                  {isListening ? <Stop /> : <Mic />}
                </IconButton>
                <Button
                  variant="contained"
                  endIcon={isTyping ? <CircularProgress size={20} /> : <Send />}
                  onClick={handleSendMessage}
                  disabled={isTyping || !inputMessage.trim()}
                >
                  Send
                </Button>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Press Enter to send, Shift+Enter for new line
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default ChangleeAssistant;