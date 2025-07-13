import React from 'react';
import { Box, Typography, Avatar, Paper, Chip } from '@mui/material';
import { Person, SmartToy, ContentCopy, Check } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MessageViewProps {
  message: {
    role?: string;
    content?: string;
    timestamp?: string;
    type?: string;
  };
  index: number;
}

const MessageView: React.FC<MessageViewProps> = ({ message, index }) => {
  const [copied, setCopied] = React.useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderContent = (content: string) => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index),
        });
      }
      parts.push({
        type: 'code',
        language: match[1] || 'text',
        content: match[2].trim(),
      });
      lastIndex = match.index + match[0].length;
    }

    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex),
      });
    }

    return parts.map((part, idx) => {
      if (part.type === 'code') {
        return (
          <Box key={idx} sx={{ my: 2, position: 'relative' }}>
            <SyntaxHighlighter
              language={part.language}
              style={vscDarkPlus}
              customStyle={{
                borderRadius: 12,
                padding: 16,
                fontSize: '0.875rem',
                background: 'rgba(0, 0, 0, 0.4)',
              }}
            >
              {part.content}
            </SyntaxHighlighter>
          </Box>
        );
      }
      return (
        <Typography
          key={idx}
          variant="body1"
          sx={{
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            lineHeight: 1.8,
          }}
        >
          {part.content}
        </Typography>
      );
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          mb: 4,
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}
      >
        <Avatar
          sx={{
            bgcolor: isUser ? 'primary.main' : 'secondary.main',
            width: 40,
            height: 40,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          }}
        >
          {isUser ? <Person /> : <SmartToy />}
        </Avatar>

        <Paper
          sx={{
            flex: 1,
            maxWidth: '80%',
            p: 3,
            borderRadius: 3,
            background: isUser
              ? 'linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%)'
              : 'rgba(26, 26, 46, 0.6)',
            border: '1px solid',
            borderColor: isUser ? 'rgba(124, 58, 237, 0.2)' : 'rgba(255, 255, 255, 0.05)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 2,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={isUser ? 'User' : 'Assistant'}
                size="small"
                sx={{
                  bgcolor: isUser ? 'primary.main' : 'secondary.main',
                  color: 'white',
                  fontWeight: 600,
                }}
              />
              {message.timestamp && (
                <Typography variant="caption" color="text.secondary">
                  {(() => {
                    try {
                      const date = new Date(message.timestamp);
                      return isNaN(date.getTime()) 
                        ? 'Time not available' 
                        : format(date, 'HH:mm:ss');
                    } catch {
                      return 'Time not available';
                    }
                  })()}
                </Typography>
              )}
            </Box>
            <Box
              component={motion.button}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleCopy}
              sx={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: copied ? 'success.main' : 'text.secondary',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                transition: 'color 0.3s ease',
              }}
            >
              {copied ? <Check fontSize="small" /> : <ContentCopy fontSize="small" />}
              <Typography variant="caption">{copied ? 'Copied!' : 'Copy'}</Typography>
            </Box>
          </Box>

          {renderContent(message.content || '')}
        </Paper>
      </Box>
    </motion.div>
  );
};

export default MessageView;