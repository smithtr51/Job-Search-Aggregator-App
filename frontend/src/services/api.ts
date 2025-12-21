import axios from 'axios';
import type { Job, JobFilters, Stats, Config, TaskResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Job endpoints
export const jobsApi = {
  getAll: async (filters?: JobFilters): Promise<Job[]> => {
    const { data } = await api.get('/api/jobs', { params: filters });
    return data;
  },

  getById: async (id: number): Promise<Job> => {
    const { data } = await api.get(`/api/jobs/${id}`);
    return data;
  },

  updateStatus: async (id: number, status: Job['status']): Promise<void> => {
    await api.put(`/api/jobs/${id}/status`, { status });
  },

  updateNotes: async (id: number, notes: string): Promise<void> => {
    await api.put(`/api/jobs/${id}/notes`, { notes });
  },

  exportCsv: async (filters?: JobFilters): Promise<Blob> => {
    const { data } = await api.get('/api/jobs/export/csv', {
      params: filters,
      responseType: 'blob',
    });
    return data;
  },
};

// Stats endpoint
export const statsApi = {
  get: async (): Promise<Stats> => {
    const { data } = await api.get('/api/stats');
    return data;
  },
};

// Config endpoint
export const configApi = {
  get: async (): Promise<Config> => {
    const { data } = await api.get('/api/config');
    return data;
  },
};

// Action endpoints
export const actionsApi = {
  scrape: async (): Promise<TaskResponse> => {
    const { data } = await api.post('/api/scrape');
    return data;
  },

  score: async (): Promise<TaskResponse> => {
    const { data } = await api.post('/api/score');
    return data;
  },

  getTaskStatus: async (taskId: string): Promise<any> => {
    const { data } = await api.get(`/api/tasks/${taskId}`);
    return data;
  },
};

export default api;

