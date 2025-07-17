import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme/theme';
import Layout from './components/Layout/Layout';
import Projects from './pages/Projects/Projects';
import Sessions from './pages/Sessions/Sessions';
import Messages from './pages/Messages/Messages';
import Search from './pages/Search/Search';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Projects />} />
            <Route path="search" element={<Search />} />
            <Route path="project/:projectId" element={<Sessions />} />
            <Route path="session/:sessionId" element={<Messages />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
