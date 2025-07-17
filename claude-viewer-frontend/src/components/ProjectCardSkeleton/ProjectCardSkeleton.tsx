import React from 'react';
import { Box, Card, CardContent, Skeleton } from '@mui/material';

const ProjectCardSkeleton: React.FC = () => {
  return (
    <Card
      sx={{
        borderRadius: 3,
        background: 'rgba(26, 26, 46, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Skeleton variant="rectangular" width="60%" height={24} sx={{ borderRadius: 1 }} />
          <Skeleton variant="circular" width={24} height={24} />
        </Box>
        
        {/* Path */}
        <Skeleton variant="text" width="80%" height={16} sx={{ mb: 1 }} />
        
        {/* Chips */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Skeleton variant="rounded" width={80} height={24} />
          <Skeleton variant="rounded" width={60} height={24} />
        </Box>
        
        {/* Stats */}
        <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Skeleton variant="circular" width={16} height={16} />
            <Skeleton variant="text" width={30} height={14} />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Skeleton variant="circular" width={16} height={16} />
            <Skeleton variant="text" width={40} height={14} />
          </Box>
        </Box>
        
        {/* Last updated */}
        <Skeleton variant="text" width="50%" height={12} />
      </CardContent>
    </Card>
  );
};

export default ProjectCardSkeleton;