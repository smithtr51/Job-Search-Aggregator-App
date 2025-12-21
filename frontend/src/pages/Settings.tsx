import { useState } from 'react';
import { Download, Play, CheckCircle, AlertCircle } from 'lucide-react';
import { useConfig, useScrapeJobs, useScoreJobs } from '../hooks/useJobs';
import { jobsApi } from '../services/api';

export default function Settings() {
  const { data: config } = useConfig();
  const scrapeJobs = useScrapeJobs();
  const scoreJobs = useScoreJobs();
  const [exportStatus, setExportStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const handleScrape = () => {
    scrapeJobs.mutate();
  };

  const handleScore = () => {
    scoreJobs.mutate();
  };

  const handleExport = async () => {
    try {
      setExportStatus('loading');
      const blob = await jobsApi.exportCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `jobs-export-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setExportStatus('success');
      setTimeout(() => setExportStatus('idle'), 3000);
    } catch (error) {
      setExportStatus('error');
      setTimeout(() => setExportStatus('idle'), 3000);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-linkedin-text mb-2">Settings</h1>
        <p className="text-linkedin-text-secondary">Configure your job search and manage data</p>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-lg border border-linkedin-border p-6">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Scrape Jobs */}
          <div className="border border-linkedin-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Scrape Jobs</h3>
            <p className="text-sm text-linkedin-text-secondary mb-4">
              Search for new jobs using Google Search via ScraperAPI
            </p>
            <button
              onClick={handleScrape}
              disabled={scrapeJobs.isPending}
              className="w-full flex items-center justify-center px-4 py-2 bg-linkedin-blue text-white rounded-lg hover:bg-linkedin-dark-blue disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4 mr-2" />
              {scrapeJobs.isPending ? 'Scraping...' : 'Start Scraping'}
            </button>
            {scrapeJobs.isSuccess && (
              <div className="mt-2 flex items-center text-sm text-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                Scraping started
              </div>
            )}
            {scrapeJobs.isError && (
              <div className="mt-2 flex items-center text-sm text-red-600">
                <AlertCircle className="w-4 h-4 mr-1" />
                Failed to start scraping
              </div>
            )}
          </div>

          {/* Score Jobs */}
          <div className="border border-linkedin-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Score Jobs</h3>
            <p className="text-sm text-linkedin-text-secondary mb-4">
              Score all unscored jobs against your resume using AI
            </p>
            <button
              onClick={handleScore}
              disabled={scoreJobs.isPending}
              className="w-full flex items-center justify-center px-4 py-2 bg-linkedin-success text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4 mr-2" />
              {scoreJobs.isPending ? 'Scoring...' : 'Start Scoring'}
            </button>
            {scoreJobs.isSuccess && (
              <div className="mt-2 flex items-center text-sm text-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                Scoring started
              </div>
            )}
            {scoreJobs.isError && (
              <div className="mt-2 flex items-center text-sm text-red-600">
                <AlertCircle className="w-4 h-4 mr-1" />
                Failed to start scoring
              </div>
            )}
          </div>

          {/* Export Jobs */}
          <div className="border border-linkedin-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Export Jobs</h3>
            <p className="text-sm text-linkedin-text-secondary mb-4">
              Download all jobs as a CSV file for external analysis
            </p>
            <button
              onClick={handleExport}
              disabled={exportStatus === 'loading'}
              className="w-full flex items-center justify-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              {exportStatus === 'loading' ? 'Exporting...' : 'Export CSV'}
            </button>
            {exportStatus === 'success' && (
              <div className="mt-2 flex items-center text-sm text-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                Export successful
              </div>
            )}
            {exportStatus === 'error' && (
              <div className="mt-2 flex items-center text-sm text-red-600">
                <AlertCircle className="w-4 h-4 mr-1" />
                Export failed
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Search Configuration */}
      {config && (
        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <h2 className="text-xl font-semibold mb-4">Search Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-2">Keywords</h3>
              <div className="flex flex-wrap gap-2">
                {config.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Experience Levels</h3>
              <div className="flex flex-wrap gap-2">
                {config.experience_levels.map((level, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                  >
                    {level}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Primary Location</h3>
              <p className="text-linkedin-text-secondary">{config.primary_location}</p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Date Range</h3>
              <p className="text-linkedin-text-secondary capitalize">{config.date_range.replace('_', ' ')}</p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Salary Range</h3>
              <p className="text-linkedin-text-secondary">
                {config.min_salary ? `$${config.min_salary.toLocaleString()}` : 'No minimum'} -{' '}
                {config.max_salary ? `$${config.max_salary.toLocaleString()}` : 'No maximum'}
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Results Per Search</h3>
              <p className="text-linkedin-text-secondary">{config.results_per_search}</p>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="font-semibold mb-2">Included Job Boards</h3>
            <div className="flex flex-wrap gap-2">
              {config.included_sites.map((site, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {site}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              To modify these settings, edit the <code className="bg-blue-100 px-2 py-1 rounded">config.py</code> file
              and restart the backend server.
            </p>
          </div>
        </div>
      )}

      {/* API Status */}
      <div className="bg-white rounded-lg border border-linkedin-border p-6">
        <h2 className="text-xl font-semibold mb-4">API Status</h2>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
            <span className="font-medium">Backend API</span>
            <span className="flex items-center text-green-600">
              <CheckCircle className="w-4 h-4 mr-1" />
              Connected
            </span>
          </div>
          <p className="text-sm text-linkedin-text-secondary mt-2">
            Backend URL: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:8000</code>
          </p>
        </div>
      </div>
    </div>
  );
}

