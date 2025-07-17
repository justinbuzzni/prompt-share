import React, { useState, useEffect } from 'react';
import {
  Typography,
  TextField,
  InputAdornment,
  Box,
  Card,
  CardContent,
  Chip,
  Pagination,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Collapse,
  IconButton,
  Paper,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList,
  Clear,
  AccessTime,
  Person,
  Code,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { searchApi, SearchResult, SearchFilters } from '../../services/api';

interface SearchState {
  query: string;
  filters: SearchFilters;
  results: SearchResult[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  took: number;
}

const Search: React.FC = () => {
  const [searchState, setSearchState] = useState<SearchState>({
    query: '',
    filters: {},
    results: [],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    error: null,
    took: 0,
  });

  const [showFilters, setShowFilters] = useState(false);
  const [tempFilters, setTempFilters] = useState<SearchFilters>({});

  const handleSearch = async (newQuery?: string, newPage?: number, newFilters?: SearchFilters) => {
    const query = newQuery !== undefined ? newQuery : searchState.query;
    const page = newPage !== undefined ? newPage : searchState.page;
    const filters = newFilters !== undefined ? newFilters : searchState.filters;

    if (!query.trim()) {
      setSearchState(prev => ({ ...prev, results: [], total: 0, error: null }));
      return;
    }

    setSearchState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await searchApi.search(query, {
        ...filters,
        size: searchState.pageSize,
        from: (page - 1) * searchState.pageSize,
      });

      setSearchState(prev => ({
        ...prev,
        query,
        results: response.hits,
        total: response.total,
        page,
        filters,
        loading: false,
        took: response.took,
      }));
    } catch (error) {
      console.error('Search error:', error);
      setSearchState(prev => ({
        ...prev,
        loading: false,
        error: 'Search failed. Please try again.',
      }));
    }
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    handleSearch(undefined, value);
  };

  const handleApplyFilters = () => {
    setSearchState(prev => ({ ...prev, page: 1 }));
    handleSearch(undefined, 1, tempFilters);
    setShowFilters(false);
  };

  const handleClearFilters = () => {
    setTempFilters({});
    setSearchState(prev => ({ ...prev, filters: {}, page: 1 }));
    handleSearch(undefined, 1, {});
    setShowFilters(false);
  };

  const formatHighlight = (text: string) => {
    return text.replace(/<em>/g, '<mark>').replace(/<\/em>/g, '</mark>');
  };

  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'primary';
      case 'assistant':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h1" sx={{ mb: 2, fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
          Search Messages
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600 }}>
          Search through your Claude conversations using advanced text search and filters
        </Typography>
      </motion.div>

      {/* Search Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search messages..."
            value={searchState.query}
            onChange={(e) => setSearchState(prev => ({ ...prev, query: e.target.value }))}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
              endAdornment: searchState.loading && (
                <InputAdornment position="end">
                  <CircularProgress size={20} />
                </InputAdornment>
              ),
            }}
            sx={{
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
          />
          <Button
            variant="contained"
            onClick={() => handleSearch()}
            disabled={searchState.loading || !searchState.query.trim()}
            sx={{ minWidth: 100, borderRadius: 3 }}
          >
            Search
          </Button>
          <IconButton
            onClick={() => setShowFilters(!showFilters)}
            color={showFilters ? 'primary' : 'default'}
            sx={{ borderRadius: 2 }}
          >
            <FilterList />
          </IconButton>
        </Box>
      </motion.div>

      {/* Filters Panel */}
      <Collapse in={showFilters}>
        <Paper
          sx={{
            p: 3,
            mb: 3,
            borderRadius: 3,
            background: 'rgba(26, 26, 46, 0.6)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <FilterList sx={{ mr: 1 }} />
            Search Filters
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 2, mb: 2 }}>
            <FormControl>
              <InputLabel>Role</InputLabel>
              <Select
                value={tempFilters.role || ''}
                onChange={(e) => setTempFilters(prev => ({ ...prev, role: e.target.value || undefined }))}
                label="Role"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="assistant">Assistant</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Project Name"
              value={tempFilters.project_name || ''}
              onChange={(e) => setTempFilters(prev => ({ ...prev, project_name: e.target.value || undefined }))}
            />

            <TextField
              label="Date From"
              type="date"
              value={tempFilters.date_from || ''}
              onChange={(e) => setTempFilters(prev => ({ ...prev, date_from: e.target.value || undefined }))}
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              label="Date To"
              type="date"
              value={tempFilters.date_to || ''}
              onChange={(e) => setTempFilters(prev => ({ ...prev, date_to: e.target.value || undefined }))}
              InputLabelProps={{ shrink: true }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button onClick={handleClearFilters} startIcon={<Clear />}>
              Clear Filters
            </Button>
            <Button
              variant="contained"
              onClick={handleApplyFilters}
              startIcon={<FilterList />}
            >
              Apply Filters
            </Button>
          </Box>
        </Paper>
      </Collapse>

      {/* Search Results */}
      {searchState.error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {searchState.error}
        </Alert>
      )}

      {/* Results Info */}
      {searchState.results.length > 0 && (
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Found {searchState.total} results in {searchState.took}ms
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Page {searchState.page} of {Math.ceil(searchState.total / searchState.pageSize)}
          </Typography>
        </Box>
      )}

      {/* Results List */}
      <AnimatePresence mode="wait">
        {searchState.results.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {searchState.results.map((result, index) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card
                    sx={{
                      borderRadius: 3,
                      background: 'rgba(26, 26, 46, 0.6)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        border: '1px solid rgba(124, 58, 237, 0.3)',
                        transform: 'translateY(-1px)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      {/* Header */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          <Chip
                            icon={<Person />}
                            label={result.source.role || 'Unknown'}
                            color={getMessageTypeColor(result.source.role)}
                            size="small"
                          />
                          <Typography variant="body2" color="text.secondary">
                            Score: {result.score.toFixed(2)}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <AccessTime sx={{ fontSize: 16, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {formatDate(result.source.timestamp)}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Project Info */}
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Project: {result.source.project_name || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Path: {result.source.project_path || 'Unknown'}
                        </Typography>
                      </Box>

                      {/* Content */}
                      <Box sx={{ mb: 2 }}>
                        {result.highlight.content ? (
                          <Box>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              Matching content:
                            </Typography>
                            {result.highlight.content.map((highlight, idx) => (
                              <Typography
                                key={idx}
                                variant="body2"
                                sx={{
                                  mb: 1,
                                  p: 1,
                                  bgcolor: 'rgba(255, 255, 255, 0.02)',
                                  borderRadius: 1,
                                  '& mark': {
                                    backgroundColor: 'rgba(124, 58, 237, 0.3)',
                                    color: 'inherit',
                                  },
                                }}
                                dangerouslySetInnerHTML={{
                                  __html: formatHighlight(highlight),
                                }}
                              />
                            ))}
                          </Box>
                        ) : (
                          <Typography
                            variant="body2"
                            sx={{
                              maxHeight: 200,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {result.source.content || 'No content available'}
                          </Typography>
                        )}
                      </Box>

                      {/* Tags */}
                      {result.source.tags && result.source.tags.length > 0 && (
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {result.source.tags.map((tag: string, idx: number) => (
                            <Chip
                              key={idx}
                              label={tag}
                              size="small"
                              variant="outlined"
                              sx={{ bgcolor: 'rgba(124, 58, 237, 0.1)' }}
                            />
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </Box>

            {/* Pagination */}
            {searchState.total > searchState.pageSize && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <Pagination
                  count={Math.ceil(searchState.total / searchState.pageSize)}
                  page={searchState.page}
                  onChange={handlePageChange}
                  color="primary"
                  size="large"
                />
              </Box>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!searchState.loading && searchState.query && searchState.results.length === 0 && (
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
            <SearchIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" color="text.secondary">
              No results found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Try adjusting your search terms or filters
            </Typography>
          </Box>
        </motion.div>
      )}
    </Box>
  );
};

export default Search;