import { Link, useLocation } from 'react-router-dom';
import { Briefcase, LayoutDashboard, Settings } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/jobs', icon: Briefcase, label: 'Jobs' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="min-h-screen bg-linkedin-background">
      {/* Header */}
      <header className="bg-white border-b border-linkedin-border sticky top-0 z-50">
        <div className="max-w-[1440px] mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-8 h-8 text-linkedin-blue" />
              <h1 className="text-2xl font-bold text-linkedin-blue">Job Search</h1>
            </div>
            <nav className="flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex flex-col items-center px-4 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-linkedin-blue bg-opacity-10 text-linkedin-blue'
                        : 'text-linkedin-text-secondary hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-xs mt-1">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1440px] mx-auto px-6 py-6">
        {children}
      </main>
    </div>
  );
}

