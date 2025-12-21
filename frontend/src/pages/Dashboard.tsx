import { TrendingUp, Briefcase, CheckCircle, Clock } from 'lucide-react';
import { useStats, useJobs } from '../hooks/useJobs';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const { data: stats } = useStats();
  const { data: highMatchJobs = [] } = useJobs({ min_score: 70 });
  const { data: unscoredJobs = [] } = useJobs();

  const totalJobs = stats?.total_jobs || 0;
  const avgScore = stats?.average_match_score || 0;
  const appliedCount = (stats?.by_status.applied || 0) + (stats?.by_status.interviewing || 0);
  const unscored = unscoredJobs.filter(j => !j.match_score).length;

  // Prepare data for charts
  const statusData = stats?.by_status
    ? Object.entries(stats.by_status).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
      }))
    : [];

  const companyData = stats?.by_company
    ? Object.entries(stats.by_company)
        .slice(0, 10)
        .map(([name, value]) => ({ name, jobs: value }))
    : [];

  const statusColors: Record<string, string> = {
    New: '#3498db',
    Reviewed: '#9b59b6',
    Applied: '#2ecc71',
    Interviewing: '#f39c12',
    Rejected: '#e74c3c',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-linkedin-text mb-2">Dashboard</h1>
        <p className="text-linkedin-text-secondary">Overview of your job search progress</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-linkedin-text-secondary mb-1">Total Jobs</p>
              <p className="text-3xl font-bold text-linkedin-text">{totalJobs}</p>
            </div>
            <Briefcase className="w-12 h-12 text-linkedin-blue opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-linkedin-text-secondary mb-1">High Match (70+)</p>
              <p className="text-3xl font-bold text-linkedin-success">{highMatchJobs.length}</p>
            </div>
            <TrendingUp className="w-12 h-12 text-linkedin-success opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-linkedin-text-secondary mb-1">Applied/Interviewing</p>
              <p className="text-3xl font-bold text-linkedin-blue">{appliedCount}</p>
            </div>
            <CheckCircle className="w-12 h-12 text-linkedin-blue opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-linkedin-text-secondary mb-1">Unscored</p>
              <p className="text-3xl font-bold text-linkedin-warning">{unscored}</p>
            </div>
            <Clock className="w-12 h-12 text-linkedin-warning opacity-20" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Company Distribution */}
        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <h2 className="text-xl font-semibold mb-4">Top Companies</h2>
          {companyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={companyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="jobs" fill="#0A66C2" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-linkedin-text-secondary">
              No data available
            </div>
          )}
        </div>

        {/* Status Distribution */}
        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <h2 className="text-xl font-semibold mb-4">Jobs by Status</h2>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={statusColors[entry.name] || '#999'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-linkedin-text-secondary">
              No data available
            </div>
          )}
        </div>
      </div>

      {/* Average Match Score */}
      {avgScore > 0 && (
        <div className="bg-white rounded-lg border border-linkedin-border p-6">
          <h2 className="text-xl font-semibold mb-4">Average Match Score</h2>
          <div className="flex items-center">
            <div className="flex-1">
              <div className="h-8 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-linkedin-blue transition-all duration-500"
                  style={{ width: `${avgScore}%` }}
                />
              </div>
            </div>
            <div className="ml-4 text-3xl font-bold text-linkedin-blue">
              {Math.round(avgScore)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

