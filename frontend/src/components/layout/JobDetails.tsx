import { ExternalLink, Briefcase, MapPin, Calendar } from 'lucide-react';
import { useState } from 'react';
import type { Job } from '../../types';
import StatusBadge from '../StatusBadge';
import ScoreIndicator from '../ScoreIndicator';
import { useUpdateJobStatus, useUpdateJobNotes } from '../../hooks/useJobs';

interface JobDetailsProps {
  job: Job | null;
}

export default function JobDetails({ job }: JobDetailsProps) {
  const [localNotes, setLocalNotes] = useState(job?.notes || '');
  const [selectedStatus, setSelectedStatus] = useState<Job['status']>(job?.status || 'new');
  const updateStatus = useUpdateJobStatus();
  const updateNotes = useUpdateJobNotes();

  if (!job) {
    return (
      <div className="flex-1 bg-white rounded-lg border border-linkedin-border p-8">
        <div className="flex flex-col items-center justify-center h-full text-center">
          <Briefcase className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-linkedin-text-secondary text-lg">Select a job to view details</p>
        </div>
      </div>
    );
  }

  const handleStatusChange = (newStatus: Job['status']) => {
    setSelectedStatus(newStatus);
    updateStatus.mutate({ id: job.id, status: newStatus });
  };

  const handleSaveNotes = () => {
    if (localNotes !== job.notes) {
      updateNotes.mutate({ id: job.id, notes: localNotes });
    }
  };

  return (
    <div className="flex-1 bg-white rounded-lg border border-linkedin-border custom-scrollbar overflow-y-auto" style={{ maxHeight: 'calc(100vh - 160px)' }}>
      {/* Header */}
      <div className="p-6 border-b border-linkedin-border">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-linkedin-text mb-2">{job.title}</h1>
            <div className="flex items-center space-x-4 text-linkedin-text-secondary">
              <div className="flex items-center">
                <Briefcase className="w-4 h-4 mr-1" />
                <span className="font-medium">{job.company}</span>
              </div>
              {job.location && (
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  <span>{job.location}</span>
                </div>
              )}
            </div>
          </div>
          <ScoreIndicator score={job.match_score} size="large" />
        </div>

        <div className="flex items-center space-x-3">
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-linkedin-blue text-white rounded-lg hover:bg-linkedin-dark-blue transition-colors"
          >
            View Original
            <ExternalLink className="w-4 h-4 ml-2" />
          </a>
          <StatusBadge status={job.status} />
        </div>
      </div>

      {/* Status Update */}
      <div className="p-6 border-b border-linkedin-border bg-gray-50">
        <label className="block text-sm font-medium mb-2">Update Status</label>
        <div className="flex space-x-2">
          {(['new', 'reviewed', 'applied', 'interviewing', 'rejected'] as const).map((status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedStatus === status
                  ? 'bg-linkedin-blue text-white'
                  : 'bg-white border border-linkedin-border text-linkedin-text hover:bg-gray-50'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Match Reasoning */}
      {job.match_reasoning && (
        <div className="p-6 border-b border-linkedin-border">
          <h3 className="font-semibold text-lg mb-3">Match Analysis</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-linkedin-text whitespace-pre-wrap">{job.match_reasoning}</p>
          </div>
        </div>
      )}

      {/* Job Description */}
      <div className="p-6 border-b border-linkedin-border">
        <h3 className="font-semibold text-lg mb-3">Job Description</h3>
        <div className="prose prose-sm max-w-none">
          <p className="text-sm text-linkedin-text whitespace-pre-wrap">{job.description || 'No description available.'}</p>
        </div>
      </div>

      {/* Notes */}
      <div className="p-6">
        <h3 className="font-semibold text-lg mb-3">Notes</h3>
        <textarea
          value={localNotes}
          onChange={(e) => setLocalNotes(e.target.value)}
          onBlur={handleSaveNotes}
          placeholder="Add your notes about this job..."
          className="w-full h-32 px-4 py-2 border border-linkedin-border rounded-lg focus:outline-none focus:ring-2 focus:ring-linkedin-blue resize-none"
        />
      </div>

      {/* Metadata */}
      <div className="px-6 pb-6 text-xs text-linkedin-text-secondary">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <Calendar className="w-3 h-3 mr-1" />
            <span>Scraped: {new Date(job.scraped_at).toLocaleDateString()}</span>
          </div>
          {job.posted_date && (
            <div className="flex items-center">
              <Calendar className="w-3 h-3 mr-1" />
              <span>Posted: {new Date(job.posted_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

