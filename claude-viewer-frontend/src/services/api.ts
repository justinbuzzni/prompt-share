import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Project {
  id: string;
  path: string;
  sessions: string[];
  created_at: string;
  updated_at: string;
  last_synced: string;
  last_conversation_date?: string;
  sessionCount?: number;
  messageCount?: number;
  workspace_type?: string;
  branch_info?: string;
}

export interface ProjectGroup {
  project_name: string;
  workspaces: Project[];
  total_sessions: number;
  total_messages: number;
  last_updated: string;
}

export interface Session {
  id: string;
  project_id: string;
  project_path: string;
  first_message?: string;
  message_timestamp?: string;
  message_count: number;
  todo_data?: any;
  created_at: string;
  updated_at: string;
  last_synced: string;
}

export interface Message {
  _id: string;
  session_id: string;
  project_id: string;
  message_index: number;
  type?: string;
  role?: string;
  content?: string;
  timestamp?: string;
  raw_data: any;
  last_synced: string;
}

export const projectApi = {
  getAll: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data;
  },

  getGrouped: async (): Promise<ProjectGroup[]> => {
    const response = await api.get('/projects/grouped');
    return response.data;
  },

  getById: async (id: string): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  getSessions: async (projectId: string): Promise<Session[]> => {
    const response = await api.get(`/projects/${projectId}/sessions`);
    return response.data;
  },
};

export const sessionApi = {
  getById: async (id: string): Promise<Session> => {
    const response = await api.get(`/sessions/${id}`);
    return response.data;
  },

  getMessages: async (sessionId: string): Promise<Message[]> => {
    const response = await api.get(`/sessions/${sessionId}/messages`);
    return response.data;
  },
};

export interface SearchFilters {
  project_id?: string;
  session_id?: string;
  role?: string;
  project_name?: string;
  date_from?: string;
  date_to?: string;
  size?: number;
  from?: number;
}

export interface SearchHit {
  id: string;
  score: number;
  source: {
    id: string;
    session_id: string;
    project_id: string;
    project_name: string;
    project_path: string;
    workspace_type: string;
    branch_info: string;
    message_index: number;
    type?: string;
    role?: string;
    content?: string;
    timestamp?: string;
    created_at: string;
    last_synced: string;
    tags?: string[];
    language?: string;
    code_blocks?: Array<{
      language: string;
      code: string;
    }>;
  };
  highlight: {
    content?: string[];
  };
}

export interface SearchResult {
  id: string;
  score: number;
  source: SearchHit['source'];
  highlight: SearchHit['highlight'];
}

export interface SearchResponse {
  total: number;
  max_score: number;
  hits: SearchResult[];
  took: number;
}

export const searchApi = {
  search: async (query: string, filters: SearchFilters = {}): Promise<SearchResponse> => {
    const params = {
      q: query,
      ...filters,
    };
    
    const response = await api.get('/search', { params });
    return response.data;
  },

  searchMessages: async (query: string): Promise<Message[]> => {
    const response = await api.get('/search/messages', { params: { q: query } });
    return response.data;
  },

  searchProjects: async (query: string): Promise<Project[]> => {
    const response = await api.get('/search/projects', { params: { q: query } });
    return response.data;
  },
};

export default api;