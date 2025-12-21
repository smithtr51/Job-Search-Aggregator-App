import { ChevronDown } from 'lucide-react';
import type { Job } from '../../types';
import JobCard from '../JobCard';

interface JobListProps {
  jobs: Job[];
  selectedJobId: number | null;
  onSelectJob: (job: Job) => void;
  isLoading?: boolean;
}

export default function JobList({ jobs, selectedJobId, onSelectJob, isLoading }: JobListProps) {
  if (isLoading) {
    return (
      <div className="w-[420px] bg-white rounded-lg border border-linkedin-border p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-linkedin-blue"></div>
        </div>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="w-[420px] bg-white rounded-lg border border-linkedin-border p-6">
        <div className="text-center py-12">
          <p className="text-linkedin-text-secondary">No jobs found matching your criteria.</p>
          <p className="text-sm text-linkedin-text-secondary mt-2">
            Try adjusting your filters or run a new scrape.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-[420px]">
      <div className="bg-white rounded-lg border border-linkedin-border mb-4 p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-lg">{jobs.length} jobs</h2>
          <button className="flex items-center text-sm text-linkedin-text-secondary hover:text-linkedin-blue">
            Sort by
            <ChevronDown className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>

      <div className="space-y-2 custom-scrollbar overflow-y-auto" style={{ maxHeight: 'calc(100vh - 240px)' }}>
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            isSelected={job.id === selectedJobId}
            onClick={() => onSelectJob(job)}
          />
        ))}
      </div>
    </div>
  );
}

