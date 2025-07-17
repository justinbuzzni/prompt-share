import React from 'react';
import { Box, Container, IconButton, Typography, useTheme, Button } from '@mui/material';
import { motion } from 'framer-motion';
import { AutoAwesome, GitHub, Search, Home } from '@mui/icons-material';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';

const Layout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, #1A1A2E 100%)`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated background elements */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: 'hidden',
          zIndex: 0,
        }}
      >
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          style={{
            position: 'absolute',
            top: '10%',
            left: '10%',
            width: '300px',
            height: '300px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(124, 58, 237, 0.3) 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'linear',
          }}
          style={{
            position: 'absolute',
            bottom: '20%',
            right: '20%',
            width: '400px',
            height: '400px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(236, 72, 153, 0.3) 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
        />
      </Box>

      {/* Header */}
      <Box
        component={motion.header}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 100 }}
        sx={{
          position: 'relative',
          zIndex: 10,
          py: 3,
          px: 4,
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          background: 'rgba(15, 15, 35, 0.8)',
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              >
                <AutoAwesome sx={{ fontSize: 40, color: theme.palette.primary.main }} />
              </motion.div>
              <Typography variant="h4" sx={{ fontWeight: 800, color: theme.palette.text.primary }}>
                Claude Viewer
              </Typography>
            </Box>
            
            {/* Navigation */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                startIcon={<Home />}
                onClick={() => navigate('/')}
                sx={{
                  color: location.pathname === '/' ? theme.palette.primary.main : theme.palette.text.secondary,
                  '&:hover': {
                    color: theme.palette.primary.main,
                  },
                }}
              >
                Projects
              </Button>
              <Button
                startIcon={<Search />}
                onClick={() => navigate('/search')}
                sx={{
                  color: location.pathname === '/search' ? theme.palette.primary.main : theme.palette.text.secondary,
                  '&:hover': {
                    color: theme.palette.primary.main,
                  },
                }}
              >
                Search
              </Button>
              <IconButton
                href="https://github.com/justinbuzzni/prompt-share"
                target="_blank"
                sx={{
                  color: theme.palette.text.secondary,
                  '&:hover': {
                    color: theme.palette.primary.main,
                  },
                }}
              >
                <GitHub />
              </IconButton>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Main content */}
      <Container maxWidth="xl" sx={{ position: 'relative', zIndex: 1, py: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
};

export default Layout;