import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  IconButton,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  ArrowBack,
  Message,
  Schedule,
  ArrowForward,
  AutoAwesome,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { projectApi, Project, Session } from '../../services/api';

const Sessions: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProjectAndSessions = async () => {
      try {
        const [projectData, sessionsData] = await Promise.all([
          projectApi.getById(projectId!),
          projectApi.getSessions(projectId!),
        ]);
        setProject(projectData);
        setSessions(sessionsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProjectAndSessions();
    }
  }, [projectId]);


  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const projectName = project?.path.split('/').pop() || project?.path || '';

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
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
            <Typography variant="body2" color="text.primary">
              {projectName}
            </Typography>
          </Breadcrumbs>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <IconButton onClick={() => navigate('/')} sx={{ color: 'primary.main' }}>
              <ArrowBack />
            </IconButton>
            <Typography variant="h2">{projectName}</Typography>
          </Box>

          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {project?.path}
          </Typography>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              icon={<Message />}
              label={`${sessions.length} Sessions`}
              sx={{
                background: 'rgba(124, 58, 237, 0.1)',
                border: '1px solid rgba(124, 58, 237, 0.3)',
              }}
            />
            <Chip
              icon={<Schedule />}
              label={`Updated ${format(new Date(project?.updated_at || ''), 'MMM dd, yyyy')}`}
              sx={{
                background: 'rgba(236, 72, 153, 0.1)',
                border: '1px solid rgba(236, 72, 153, 0.3)',
              }}
            />
          </Box>
        </Box>
      </motion.div>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {sessions.map((session, index) => (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.01 }}
            >
              <Card
                sx={{
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                onClick={() => navigate(`/session/${session.id}`)}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'start',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <AutoAwesome sx={{ color: 'secondary.main', fontSize: 20 }} />
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          Session {index + 1}
                        </Typography>
                        <Chip
                          label={`${session.message_count} messages`}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Box>

                      {session.first_message && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            mb: 2,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            lineHeight: 1.6,
                          }}
                        >
                          {session.first_message}
                        </Typography>
                      )}

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {(() => {
                            try {
                              const date = new Date(session.message_timestamp || session.created_at);
                              return isNaN(date.getTime()) 
                                ? 'Date not available' 
                                : format(date, 'MMM dd, yyyy HH:mm');
                            } catch {
                              return 'Date not available';
                            }
                          })()}
                        </Typography>
                      </Box>
                    </Box>

                    <IconButton
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
                </CardContent>
              </Card>
            </motion.div>
        ))}
      </Box>

      {sessions.length === 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
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
            <Message sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" color="text.secondary">
              No sessions found
            </Typography>
          </Box>
        </motion.div>
      )}
    </Box>
  );
};

export default Sessions;