import { useState } from 'react';
import Sidebar from '../components/layout/Sidebar';
import JobList from '../components/layout/JobList';
import JobDetails from '../components/layout/JobDetails';
import { useJobs } from '../hooks/useJobs';
import type { JobFilters, Job } from '../types';

export default function Jobs() {
  const [filters, setFilters] = useState<JobFilters>({});
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  
  const { data: jobs = [], isLoading } = useJobs(filters);

  // Extract unique companies for filter
  const companies = Array.from(new Set(jobs.map(job => job.company))).sort();

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  return (
    <div className="flex space-x-4">
      {/* Left Sidebar - Filters */}
      <Sidebar
        filters={filters}
        onFiltersChange={setFilters}
        companies={companies}
      />

      {/* Middle Column - Job List */}
      <JobList
        jobs={jobs}
        selectedJobId={selectedJob?.id || null}
        onSelectJob={handleSelectJob}
        isLoading={isLoading}
      />

      {/* Right Column - Job Details */}
      <JobDetails job={selectedJob} />
    </div>
  );
}

