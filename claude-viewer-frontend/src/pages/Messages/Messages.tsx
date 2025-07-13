import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  CircularProgress,
  Chip,
  IconButton,
  Breadcrumbs,
  Link,
  TextField,
  InputAdornment,
  Fade,
} from '@mui/material';
import {
  ArrowBack,
  Message as MessageIcon,
  Schedule,
  Search,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import MessageView from '../../components/MessageView/MessageView';
import { sessionApi, Session, Message } from '../../services/api';

const Messages: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [filteredMessages, setFilteredMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | 'user' | 'assistant'>('all');

  useEffect(() => {
    const fetchSessionAndMessages = async () => {
      try {
        const [sessionData, messagesData] = await Promise.all([
          sessionApi.getById(sessionId!),
          sessionApi.getMessages(sessionId!),
        ]);
        setSession(sessionData);
        
        // Filter out messages with empty content
        const nonEmptyMessages = messagesData.filter(msg => 
          msg.content && msg.content.trim() !== ''
        );
        
        setMessages(nonEmptyMessages);
        setFilteredMessages(nonEmptyMessages);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      fetchSessionAndMessages();
    }
  }, [sessionId]);

  useEffect(() => {
    let filtered = messages;

    if (searchTerm) {
      filtered = filtered.filter((msg) =>
        msg.content?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (roleFilter !== 'all') {
      filtered = filtered.filter((msg) => msg.role === roleFilter);
    }

    setFilteredMessages(filtered);
  }, [searchTerm, roleFilter, messages]);


  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const projectName = session?.project_path.split('/').pop() || '';

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Box sx={{ mb: 4 }}>
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link
              component="button"
              variant="body2"
              onClick={() => navigate('/')}
              sx={{
                color: 'text.secondary',
                textDecoration: 'none',
                '&:hover': { color: 'primary.main' },
              }}
            >
              Projects
            </Link>
            <Link
              component="button"
              variant="body2"
              onClick={() => navigate(`/project/${session?.project_id}`)}
              sx={{
                color: 'text.secondary',
                textDecoration: 'none',
                '&:hover': { color: 'primary.main' },
              }}
            >
              {projectName}
            </Link>
            <Typography variant="body2" color="text.primary">
              Session
            </Typography>
          </Breadcrumbs>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <IconButton
              onClick={() => navigate(`/project/${session?.project_id}`)}
              sx={{ color: 'primary.main' }}
            >
              <ArrowBack />
            </IconButton>
            <Typography variant="h2">Conversation</Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
            <Chip
              icon={<MessageIcon />}
              label={`${filteredMessages.length} Messages`}
              sx={{
                background: 'rgba(124, 58, 237, 0.1)',
                border: '1px solid rgba(124, 58, 237, 0.3)',
              }}
            />
            <Chip
              icon={<Schedule />}
              label={
                session?.message_timestamp
                  ? format(new Date(session.message_timestamp), 'MMM dd, yyyy HH:mm')
                  : 'No timestamp'
              }
              sx={{
                background: 'rgba(236, 72, 153, 0.1)',
                border: '1px solid rgba(236, 72, 153, 0.3)',
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', md: 'row' } }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search messages..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  background: 'rgba(26, 26, 46, 0.5)',
                  backdropFilter: 'blur(10px)',
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: 'text.secondary', fontSize: 20 }} />
                  </InputAdornment>
                ),
              }}
            />
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label="All"
                onClick={() => setRoleFilter('all')}
                sx={{
                  cursor: 'pointer',
                  bgcolor: roleFilter === 'all' ? 'primary.main' : 'transparent',
                  border: '1px solid',
                  borderColor: roleFilter === 'all' ? 'primary.main' : 'divider',
                }}
              />
              <Chip
                label="User"
                onClick={() => setRoleFilter('user')}
                sx={{
                  cursor: 'pointer',
                  bgcolor: roleFilter === 'user' ? 'primary.main' : 'transparent',
                  border: '1px solid',
                  borderColor: roleFilter === 'user' ? 'primary.main' : 'divider',
                }}
              />
              <Chip
                label="Assistant"
                onClick={() => setRoleFilter('assistant')}
                sx={{
                  cursor: 'pointer',
                  bgcolor: roleFilter === 'assistant' ? 'secondary.main' : 'transparent',
                  border: '1px solid',
                  borderColor: roleFilter === 'assistant' ? 'secondary.main' : 'divider',
                }}
              />
            </Box>
          </Box>
        </Box>
      </motion.div>

      <AnimatePresence mode="wait">
        <Box sx={{ pb: 4 }}>
          {filteredMessages.map((message, index) => (
            <MessageView key={message._id} message={message} index={index} />
          ))}
        </Box>
      </AnimatePresence>

      {filteredMessages.length === 0 && (
        <Fade in timeout={300}>
          <Box
            sx={{
              textAlign: 'center',
              py: 8,
              px: 4,
              borderRadius: 4,
              background: 'rgba(26, 26, 46, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
            }}
          >
            <MessageIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" color="text.secondary">
              No messages found
            </Typography>
            {searchTerm && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Try adjusting your search terms
              </Typography>
            )}
          </Box>
        </Fade>
      )}
    </Box>
  );
};

export default Messages;