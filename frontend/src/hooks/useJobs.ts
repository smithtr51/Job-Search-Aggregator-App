import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi, statsApi, configApi, actionsApi } from '../services/api';
import type { JobFilters, Job } from '../types';

export const useJobs = (filters?: JobFilters) => {
  return useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => jobsApi.getAll(filters),
  });
};

export const useJob = (id: number | null) => {
  return useQuery({
    queryKey: ['job', id],
    queryFn: () => id ? jobsApi.getById(id) : null,
    enabled: !!id,
  });
};

export const useStats = () => {
  return useQuery({
    queryKey: ['stats'],
    queryFn: () => statsApi.get(),
  });
};

export const useConfig = () => {
  return useQuery({
    queryKey: ['config'],
    queryFn: () => configApi.get(),
  });
};

export const useUpdateJobStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: Job['status'] }) =>
      jobsApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['job'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
};

export const useUpdateJobNotes = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, notes }: { id: number; notes: string }) =>
      jobsApi.updateNotes(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['job'] });
    },
  });
};

export const useScrapeJobs = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => actionsApi.scrape(),
    onSuccess: () => {
      // Refetch jobs after scraping
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['jobs'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
      }, 3000);
    },
  });
};

export const useScoreJobs = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => actionsApi.score(),
    onSuccess: () => {
      // Refetch jobs after scoring
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['jobs'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
      }, 3000);
    },
  });
};

