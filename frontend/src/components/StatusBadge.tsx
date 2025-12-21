import type { Job } from '../types';

interface StatusBadgeProps {
  status: Job['status'];
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    new: { label: 'New', className: 'status-new' },
    reviewed: { label: 'Reviewed', className: 'status-reviewed' },
    applied: { label: 'Applied', className: 'status-applied' },
    interviewing: { label: 'Interviewing', className: 'status-interviewing' },
    rejected: { label: 'Rejected', className: 'status-rejected' },
  };

  const config = statusConfig[status] || statusConfig.new;

  return (
    <span className={`status-badge ${config.className}`}>
      {config.label}
    </span>
  );
}

