interface ScoreIndicatorProps {
  score?: number;
  size?: 'small' | 'medium' | 'large';
}

export default function ScoreIndicator({ score, size = 'medium' }: ScoreIndicatorProps) {
  if (score === undefined || score === null) {
    return (
      <div className={`text-gray-400 ${size === 'large' ? 'text-2xl' : 'text-sm'}`}>
        —
      </div>
    );
  }

  const getScoreClass = () => {
    if (score >= 70) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
  };

  const getSizeClass = () => {
    switch (size) {
      case 'small':
        return 'text-sm';
      case 'medium':
        return 'text-base';
      case 'large':
        return 'text-4xl';
    }
  };

  if (size === 'large') {
    return (
      <div className="flex flex-col items-center">
        <div className={`${getSizeClass()} ${getScoreClass()} font-bold`}>
          {Math.round(score)}
        </div>
        <div className="text-xs text-linkedin-text-secondary mt-1">Match Score</div>
      </div>
    );
  }

  return (
    <div className={`${getSizeClass()} ${getScoreClass()}`}>
      {Math.round(score)}
    </div>
  );
}

