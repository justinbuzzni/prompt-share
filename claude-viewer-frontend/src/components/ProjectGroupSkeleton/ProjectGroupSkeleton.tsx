import React from 'react';
import { Box, Paper, Skeleton } from '@mui/material';
import ProjectCardSkeleton from '../ProjectCardSkeleton/ProjectCardSkeleton';

const ProjectGroupSkeleton: React.FC = () => {
  return (
    <Paper
      sx={{
        p: 3,
        borderRadius: 3,
        background: 'rgba(26, 26, 46, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Box sx={{ mb: 2 }}>
        {/* Group title */}
        <Skeleton variant="text" width="40%" height={32} sx={{ mb: 1 }} />
        
        {/* Chips */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Skeleton variant="rounded" width={120} height={24} />
          <Skeleton variant="rounded" width={100} height={24} />
        </Box>
      </Box>
      
      {/* Project cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 2 }}>
        {Array.from({ length: 3 }).map((_, index) => (
          <ProjectCardSkeleton key={index} />
        ))}
      </Box>
    </Paper>
  );
};

export default ProjectGroupSkeleton;