import { useEffect, useState } from 'react';
import { Loader2, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { actionsApi } from '../services/api';

interface TaskProgress {
  task_id: string;
  task_type: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  total: number;
  current_item: string;
  message: string;
  started_at: string;
  completed_at?: string;
  error?: string;
}

interface ProgressTrackerProps {
  taskId: string | null;
  onComplete?: () => void;
}

export default function ProgressTracker({ taskId, onComplete }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (!taskId) return;

    const fetchProgress = async () => {
      try {
        const data = await actionsApi.getTaskStatus(taskId);
        setProgress(data);

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          if (onComplete) onComplete();
        }
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(fetchProgress, 2000);
    fetchProgress(); // Initial fetch

    return () => clearInterval(interval);
  }, [taskId, onComplete]);

  useEffect(() => {
    if (!progress || progress.status !== 'running') return;

    const timer = setInterval(() => {
      const start = new Date(progress.started_at).getTime();
      const now = new Date().getTime();
      setElapsedTime(Math.floor((now - start) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [progress]);

  if (!progress) return null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    if (progress.total === 0) return 0;
    return Math.round((progress.progress / progress.total) * 100);
  };

  return (
    <div className="mt-4 p-4 border border-linkedin-border rounded-lg bg-gray-50">
      {/* Status Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          {progress.status === 'running' && (
            <>
              <Loader2 className="w-5 h-5 text-linkedin-blue animate-spin mr-2" />
              <span className="font-semibold text-linkedin-blue">
                {progress.task_type === 'scrape' ? 'Scraping Jobs' : 'Scoring Jobs'}...
              </span>
            </>
          )}
          {progress.status === 'completed' && (
            <>
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              <span className="font-semibold text-green-600">Completed</span>
            </>
          )}
          {progress.status === 'failed' && (
            <>
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="font-semibold text-red-600">Failed</span>
            </>
          )}
        </div>
        <div className="flex items-center text-sm text-linkedin-text-secondary">
          <Clock className="w-4 h-4 mr-1" />
          {formatTime(elapsedTime)}
        </div>
      </div>

      {/* Progress Bar */}
      {progress.status === 'running' && (
        <div className="mb-3">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-linkedin-text-secondary">{progress.message}</span>
            <span className="font-medium text-linkedin-blue">
              {progress.progress} / {progress.total || '?'}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-linkedin-blue h-full transition-all duration-500 rounded-full"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
          {progress.total > 0 && (
            <div className="text-xs text-linkedin-text-secondary mt-1 text-right">
              {getProgressPercentage()}%
            </div>
          )}
        </div>
      )}

      {/* Current Item */}
      {progress.status === 'running' && progress.current_item && (
        <div className="text-sm">
          <span className="text-linkedin-text-secondary">Current: </span>
          <span className="text-linkedin-text truncate">{progress.current_item}</span>
        </div>
      )}

      {/* Completion Message */}
      {progress.status === 'completed' && (
        <div className="text-sm text-green-700 bg-green-50 p-2 rounded">
          {progress.message}
        </div>
      )}

      {/* Error Message */}
      {progress.status === 'failed' && progress.error && (
        <div className="text-sm text-red-700 bg-red-50 p-2 rounded">
          Error: {progress.error}
        </div>
      )}
    </div>
  );
}

