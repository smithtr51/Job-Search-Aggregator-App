import { Search, X } from 'lucide-react';
import { useState } from 'react';
import type { JobFilters } from '../../types';

interface SidebarProps {
  filters: JobFilters;
  onFiltersChange: (filters: JobFilters) => void;
  companies: string[];
}

export default function Sidebar({ filters, onFiltersChange, companies }: SidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const statuses: Array<{ value: string; label: string }> = [
    { value: 'new', label: 'New' },
    { value: 'reviewed', label: 'Reviewed' },
    { value: 'applied', label: 'Applied' },
    { value: 'interviewing', label: 'Interviewing' },
    { value: 'rejected', label: 'Rejected' },
  ];

  const handleStatusToggle = (status: string) => {
    onFiltersChange({
      ...filters,
      status: filters.status === status ? undefined : status,
    });
  };

  const handleClearFilters = () => {
    onFiltersChange({});
    setSearchTerm('');
  };

  return (
    <div className="w-64 bg-white rounded-lg border border-linkedin-border p-4 h-fit sticky top-24">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-lg">Filters</h2>
        <button
          onClick={handleClearFilters}
          className="text-sm text-linkedin-blue hover:text-linkedin-dark-blue"
        >
          Clear all
        </button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Search Company</label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              onFiltersChange({ ...filters, company: e.target.value || undefined });
            }}
            placeholder="Search..."
            className="w-full pl-10 pr-4 py-2 border border-linkedin-border rounded-lg focus:outline-none focus:ring-2 focus:ring-linkedin-blue"
          />
          {searchTerm && (
            <button
              onClick={() => {
                setSearchTerm('');
                onFiltersChange({ ...filters, company: undefined });
              }}
              className="absolute right-3 top-1/2 transform -translate-y-1/2"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>
      </div>

      {/* Status Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Status</label>
        <div className="space-y-2">
          {statuses.map((status) => (
            <label key={status.value} className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={filters.status === status.value}
                onChange={() => handleStatusToggle(status.value)}
                className="w-4 h-4 text-linkedin-blue border-gray-300 rounded focus:ring-linkedin-blue"
              />
              <span className="ml-2 text-sm">{status.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Match Score Slider */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          Minimum Match Score: {filters.min_score || 0}%
        </label>
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={filters.min_score || 0}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              min_score: parseInt(e.target.value) || undefined,
            })
          }
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0</span>
          <span>50</span>
          <span>100</span>
        </div>
      </div>
    </div>
  );
}

