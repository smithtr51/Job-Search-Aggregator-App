# Job Search Frontend

LinkedIn-style React frontend for the Job Search Aggregator application.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Query** for data fetching and state management
- **React Router** for navigation
- **Recharts** for data visualization
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
```

### Development

```bash
# Start the development server
npm run dev
```

The application will be available at `http://localhost:5173`

**Note:** Make sure the FastAPI backend is running at `http://localhost:8000`

### Build for Production

```bash
# Build the application
npm run build

# Preview the production build
npm run preview
```

## Features

- **Three-column LinkedIn-style layout** - Filters, job list, and job details
- **Advanced filtering** - Search by company, status, and match score
- **Real-time updates** - Optimistic UI updates with React Query
- **Job management** - Update status, add notes, and track applications
- **Dashboard** - Visualize your job search progress with charts
- **Export functionality** - Download jobs as CSV
- **Scraping and scoring** - Trigger background tasks from the UI

## Project Structure

```
src/
├── components/        # Reusable components
│   ├── layout/       # Layout components (Sidebar, JobList, JobDetails)
│   ├── JobCard.tsx   # Job card component
│   ├── StatusBadge.tsx
│   └── ScoreIndicator.tsx
├── pages/            # Page components
│   ├── Dashboard.tsx
│   ├── Jobs.tsx
│   └── Settings.tsx
├── services/         # API client
│   └── api.ts
├── hooks/            # Custom React hooks
│   └── useJobs.ts
├── types/            # TypeScript types
│   └── index.ts
├── App.tsx           # Main app component
├── main.tsx          # Entry point
└── index.css         # Global styles
```

## LinkedIn-Style Design

The UI follows LinkedIn's design language with:

- **LinkedIn Blue** (#0A66C2) as primary color
- **Light gray background** (#F3F2EF)
- **White cards** with subtle borders and shadows
- **Professional typography** with system fonts
- **Smooth transitions** and hover effects
- **Color-coded status badges** for visual clarity
- **Match score indicators** with green/yellow/gray colors

## API Integration

The frontend communicates with the FastAPI backend through:

- `/api/jobs` - Get and filter jobs
- `/api/jobs/{id}` - Get job details
- `/api/jobs/{id}/status` - Update job status
- `/api/jobs/{id}/notes` - Update job notes
- `/api/stats` - Get dashboard statistics
- `/api/scrape` - Trigger job scraping
- `/api/score` - Trigger job scoring
- `/api/config` - Get search configuration
- `/api/jobs/export/csv` - Export jobs as CSV

All API calls use React Query for caching, automatic refetching, and optimistic updates.

