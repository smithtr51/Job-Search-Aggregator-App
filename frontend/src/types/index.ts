export interface Job {
  id: number;
  company: string;
  title: string;
  location?: string;
  description?: string;
  url: string;
  posted_date?: string;
  scraped_at: string;
  match_score?: number;
  match_reasoning?: string;
  status: 'new' | 'reviewed' | 'applied' | 'rejected' | 'interviewing';
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface JobFilters {
  status?: string;
  min_score?: number;
  company?: string;
  limit?: number;
}

export interface Stats {
  total_jobs: number;
  by_status: Record<string, number>;
  average_match_score?: number;
  by_company: Record<string, number>;
}

export interface Config {
  keywords: string[];
  primary_location: string;
  date_range: string;
  included_sites: string[];
  experience_levels: string[];
  min_salary?: number;
  max_salary?: number;
  results_per_search: number;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
}

