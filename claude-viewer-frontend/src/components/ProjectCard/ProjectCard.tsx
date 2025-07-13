import React from 'react';
import { Card, CardContent, Typography, Box, Chip, IconButton } from '@mui/material';
import { Folder, Message, Schedule, ArrowForward } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';

interface ProjectCardProps {
  project: {
    id: string;
    path: string;
    sessions: string[];
    updated_at: string;
    last_conversation_date?: string;
    sessionCount?: number;
    messageCount?: number;
  };
  index: number;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, index }) => {
  const navigate = useNavigate();

  const projectName = project.path.split('/').pop() || project.path;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card
        sx={{
          cursor: 'pointer',
          height: '100%',
          position: 'relative',
          overflow: 'hidden',
        }}
        onClick={() => navigate(`/project/${project.id}`)}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: '100px',
            height: '100px',
            background: 'radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, transparent 70%)',
            filter: 'blur(40px)',
          }}
        />
        <CardContent sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Folder sx={{ color: 'primary.main', fontSize: 28 }} />
              <Typography 
                variant="h6" 
                sx={{ 
                  fontWeight: 600,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  maxWidth: '200px',
                }}
              >
                {projectName}
              </Typography>
            </Box>
            <IconButton
              size="small"
              sx={{
                color: 'primary.main',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateX(4px)',
                },
              }}
            >
              <ArrowForward />
            </IconButton>
          </Box>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 3, fontSize: '0.8rem' }}
          >
            {project.path}
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Chip
              icon={<Message sx={{ fontSize: 16 }} />}
              label={`${project.sessions.length} sessions`}
              size="small"
              sx={{ fontSize: '0.75rem' }}
            />
            {project.messageCount && (
              <Chip
                label={`${project.messageCount} messages`}
                size="small"
                sx={{ fontSize: '0.75rem' }}
              />
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              {(() => {
                try {
                  // Use last_conversation_date if available, otherwise fall back to updated_at
                  const dateString = project.last_conversation_date || project.updated_at;
                  const date = new Date(dateString);
                  return isNaN(date.getTime()) 
                    ? 'No conversations yet' 
                    : `Last conversation: ${format(date, 'MMM dd, yyyy HH:mm')}`;
                } catch {
                  return 'No conversations yet';
                }
              })()}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ProjectCard;