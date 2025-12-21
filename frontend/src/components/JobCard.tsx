import { Briefcase, MapPin, Calendar, Star } from 'lucide-react';
import type { Job } from '../types';
import StatusBadge from './StatusBadge';
import ScoreIndicator from './ScoreIndicator';

interface JobCardProps {
  job: Job;
  isSelected: boolean;
  onClick: () => void;
}

export default function JobCard({ job, isSelected, onClick }: JobCardProps) {
  // Generate a color for the company logo based on company name
  const getCompanyColor = (name: string) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-red-500',
    ];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  const isHighMatch = job.match_score && job.match_score >= 70;

  return (
    <div
      onClick={onClick}
      className={`job-card ${isSelected ? 'selected' : ''} ${isHighMatch ? 'border-l-4 border-l-linkedin-success' : ''}`}
    >
      <div className="flex items-start space-x-3">
        {/* Company Logo */}
        <div className={`flex-shrink-0 w-12 h-12 ${getCompanyColor(job.company)} rounded flex items-center justify-center text-white font-bold text-lg`}>
          {job.company.charAt(0).toUpperCase()}
        </div>

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-1">
            <h3 className="font-semibold text-base text-linkedin-text line-clamp-2">
              {isHighMatch && <Star className="inline w-4 h-4 text-linkedin-success mr-1 fill-current" />}
              {job.title}
            </h3>
            <ScoreIndicator score={job.match_score} size="small" />
          </div>

          <p className="text-sm text-linkedin-text-secondary font-medium mb-1">
            {job.company}
          </p>

          {job.location && (
            <div className="flex items-center text-xs text-linkedin-text-secondary mb-2">
              <MapPin className="w-3 h-3 mr-1" />
              <span className="line-clamp-1">{job.location}</span>
            </div>
          )}

          <div className="flex items-center justify-between">
            <StatusBadge status={job.status} />
            <div className="flex items-center text-xs text-linkedin-text-secondary">
              <Calendar className="w-3 h-3 mr-1" />
              <span>{new Date(job.scraped_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

