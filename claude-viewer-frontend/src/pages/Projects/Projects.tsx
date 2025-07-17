import React, { useEffect, useState } from 'react';
import {
  Typography,
  TextField,
  InputAdornment,
  Box,
  CircularProgress,
  Fade,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
} from '@mui/material';
import { Search, FolderOpen, Message, ViewList, ViewModule } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import ProjectCard from '../../components/ProjectCard/ProjectCard';
import ProjectCardSkeleton from '../../components/ProjectCardSkeleton/ProjectCardSkeleton';
import ProjectGroupSkeleton from '../../components/ProjectGroupSkeleton/ProjectGroupSkeleton';
import { projectApi, Project, ProjectGroup } from '../../services/api';

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectGroups, setProjectGroups] = useState<ProjectGroup[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [filteredGroups, setFilteredGroups] = useState<ProjectGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'flat' | 'grouped'>('grouped');

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (viewMode === 'flat') {
      const filtered = projects.filter(
        (project) =>
          project.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
          project.id.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredProjects(filtered);
    } else {
      const filtered = projectGroups.filter((group) =>
        group.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        group.workspaces.some(w => w.path.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredGroups(filtered);
    }
  }, [searchTerm, projects, projectGroups, viewMode]);

  const fetchProjects = async () => {
    try {
      const [flatData, groupedData] = await Promise.all([
        projectApi.getAll(),
        projectApi.getGrouped()
      ]);
      setProjects(flatData);
      setProjectGroups(groupedData);
      setFilteredProjects(flatData);
      setFilteredGroups(groupedData);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalSessions = projects.reduce((acc, project) => acc + project.sessions.length, 0);

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h1" sx={{ mb: 2, fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
          Your Claude Projects
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600 }}>
          Explore your conversations, insights, and creative collaborations with Claude
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
          <Chip
            icon={<FolderOpen />}
            label={`${projects.length} Projects`}
            sx={{
              background: 'rgba(124, 58, 237, 0.1)',
              border: '1px solid rgba(124, 58, 237, 0.3)',
              fontWeight: 600,
            }}
          />
          <Chip
            icon={<Message />}
            label={`${totalSessions} Total Sessions`}
            sx={{
              background: 'rgba(236, 72, 153, 0.1)',
              border: '1px solid rgba(236, 72, 153, 0.3)',
              fontWeight: 600,
            }}
          />
        </Box>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField
            variant="outlined"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{
              flex: 1,
              minWidth: 300,
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                background: 'rgba(26, 26, 46, 0.5)',
                backdropFilter: 'blur(10px)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                },
                '&:hover fieldset': {
                  borderColor: 'primary.main',
                },
              },
            }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          />
          <Paper elevation={0} sx={{ p: 0.5, bgcolor: 'background.paper', borderRadius: 2 }}>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(_, newMode) => newMode && setViewMode(newMode)}
              aria-label="view mode"
              size="small"
            >
              <ToggleButton value="grouped" aria-label="grouped view">
                <ViewModule sx={{ mr: 1 }} />
                Grouped
              </ToggleButton>
              <ToggleButton value="flat" aria-label="flat view">
                <ViewList sx={{ mr: 1 }} />
                All Projects
              </ToggleButton>
            </ToggleButtonGroup>
          </Paper>
        </Box>
      </motion.div>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {viewMode === 'flat' ? (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
              {Array.from({ length: 6 }).map((_, index) => (
                <ProjectCardSkeleton key={index} />
              ))}
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {Array.from({ length: 3 }).map((_, index) => (
                <ProjectGroupSkeleton key={index} />
              ))}
            </Box>
          )}
        </Box>
      ) : viewMode === 'flat' ? (
        <AnimatePresence mode="wait">
          <Fade in={!loading} timeout={500}>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
              {filteredProjects.map((project, index) => (
                <ProjectCard key={project.id} project={project} index={index} />
              ))}
            </Box>
          </Fade>
        </AnimatePresence>
      ) : (
        <AnimatePresence mode="wait">
          <Fade in={!loading} timeout={500}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {filteredGroups.map((group, index) => (
                <motion.div
                  key={group.project_name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Paper
                    sx={{
                      p: 3,
                      borderRadius: 3,
                      background: 'rgba(26, 26, 46, 0.6)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        border: '1px solid rgba(124, 58, 237, 0.3)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                        {group.project_name}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Chip
                          size="small"
                          icon={<FolderOpen />}
                          label={`${group.workspaces.length} Workspaces`}
                          sx={{ bgcolor: 'rgba(124, 58, 237, 0.1)' }}
                        />
                        <Chip
                          size="small"
                          icon={<Message />}
                          label={`${group.total_sessions} Sessions`}
                          sx={{ bgcolor: 'rgba(236, 72, 153, 0.1)' }}
                        />
                      </Box>
                    </Box>
                    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 2 }}>
                      {group.workspaces.map((workspace, idx) => (
                        <ProjectCard key={workspace.id} project={workspace} index={idx} />
                      ))}
                    </Box>
                  </Paper>
                </motion.div>
              ))}
            </Box>
          </Fade>
        </AnimatePresence>
      )}

      {!loading && ((viewMode === 'flat' && filteredProjects.length === 0) || (viewMode === 'grouped' && filteredGroups.length === 0)) && (
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
            <FolderOpen sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" color="text.secondary">
              No projects found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {searchTerm ? 'Try adjusting your search terms' : 'Start a conversation with Claude to create your first project'}
            </Typography>
          </Box>
        </motion.div>
      )}
    </Box>
  );
};

export default Projects;