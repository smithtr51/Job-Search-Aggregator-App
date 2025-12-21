# Job Search Aggregator - LinkedIn-Style UI

A professional job search aggregator with a modern LinkedIn-style user interface, powered by React, FastAPI, and AI-driven job matching.

![LinkedIn-Style Interface](https://img.shields.io/badge/UI-LinkedIn_Style-0A66C2?style=for-the-badge&logo=linkedin)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?style=for-the-badge&logo=typescript)

## ✨ Features

### 🎨 LinkedIn-Style Interface
- **Three-column layout** - Professional job browsing experience
- **Advanced filtering** - Search by company, status, and match score
- **Job cards** - Clean design with company logos and match scores
- **Real-time updates** - Instant UI updates with React Query
- **Responsive design** - Works beautifully on all screen sizes

### 🤖 AI-Powered Matching
- **Claude AI scoring** - Intelligent job-resume matching
- **Match reasoning** - Understand why a job is a good fit
- **Resume gap analysis** - Identify missing qualifications
- **Cover letter points** - AI-generated talking points

### 🔍 Smart Job Discovery
- **Google Search scraping** - Find jobs across the entire internet
- **Multiple job boards** - LinkedIn, Indeed, Glassdoor, and more
- **Location filtering** - DC Metro Area and Remote opportunities
- **Experience level matching** - Senior, Director, Executive roles

### 📊 Analytics Dashboard
- **Visual statistics** - Charts showing job distribution
- **Progress tracking** - Monitor application status
- **Company insights** - See top hiring companies
- **Score distribution** - Understand your match quality

## 🚀 Quick Start

### Prerequisites

```bash
# Required
- Python 3.10+
- Node.js 18+
- ScraperAPI key (sign up at scraperapi.com)
- Anthropic API key (sign up at anthropic.com)
```

### 1. Set Up API Keys

```bash
# Add to ~/.zshrc or ~/.bashrc
export SCRAPERAPI_KEY='your_scraperapi_key_here'
export ANTHROPIC_API_KEY='your_anthropic_key_here'

# Reload shell
source ~/.zshrc
```

### 2. Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### 3. Initialize Database

```bash
python -c "from storage import init_db; init_db()"
```

### 4. Create Resume File

Create `resume.txt` in the project root with your resume content.

### 5. Start the Application

#### Option A: Use the Startup Script (Easiest)

```bash
./start.sh
```

#### Option B: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd api
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Open the Application

🌐 Frontend: http://localhost:5173
📡 Backend API: http://localhost:8000
📚 API Docs: http://localhost:8000/docs

## 📱 Using the Application

### Jobs Page (Main View)

The jobs page features LinkedIn's signature three-column layout:

**Left Column - Filters:**
- Search by company name
- Filter by application status
- Set minimum match score (slider)
- Clear all filters

**Middle Column - Job List:**
- Browse all jobs as cards
- See match scores and status badges
- Click to view details
- Star icon for high-match jobs (70+)

**Right Column - Job Details:**
- Full job description
- AI match reasoning
- Update application status
- Add personal notes
- Link to original posting

### Dashboard Page

Get a bird's-eye view of your job search:
- Total jobs tracked
- High-match opportunities (70+ score)
- Application progress (applied/interviewing)
- Unscored jobs count
- Company distribution chart
- Status breakdown pie chart
- Average match score

### Settings Page

Manage your job search operations:

**Actions:**
- **Scrape Jobs** - Search for new opportunities
- **Score Jobs** - Run AI matching on unscored jobs
- **Export CSV** - Download your job data

**Configuration:**
- View search keywords
- Check target locations
- See experience levels
- Review salary ranges
- Monitor API status

## 🎯 Workflow

1. **Scrape** → Find jobs matching your criteria
2. **Score** → AI analyzes fit with your resume
3. **Filter** → Focus on high-match opportunities (70+)
4. **Apply** → Track status as you progress
5. **Analyze** → Review statistics and insights

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   React Frontend (TypeScript + Vite)    │
│   • Three-column layout                 │
│   • React Query for data fetching       │
│   • Tailwind CSS for styling           │
│   • Recharts for visualizations         │
└──────────────┬──────────────────────────┘
               │ REST API
┌──────────────▼──────────────────────────┐
│        FastAPI Backend (Python)         │
│   • Pydantic models                     │
│   • Background tasks                    │
│   • CORS middleware                     │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────┐         ┌──────────┐
│ Storage │         │ Scraper  │
│ Scorer  │         │ Config   │
└────┬────┘         └──────────┘
     │
     ▼
┌──────────┐
│ SQLite   │
│ Database │
└──────────┘
```

## 📁 Project Structure

```
Job-Search-Aggregator-App/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # Pydantic models
│   └── background.py      # Background tasks
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   ├── hooks/        # React hooks
│   │   └── types/        # TypeScript types
│   └── package.json
├── storage.py             # Database operations
├── scraper.py             # Web scraping
├── scorer.py              # AI job scoring
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── resume.txt             # Your resume
├── QUICKSTART.md          # Detailed setup guide
└── start.sh               # Startup script
```

## 🎨 Design System

The UI implements LinkedIn's professional design language:

**Colors:**
- Primary: #0A66C2 (LinkedIn Blue)
- Background: #F3F2EF (Light Gray)
- Success: #057642 (Green)
- Warning: #F5C75D (Yellow)

**Components:**
- Job cards with hover effects
- Color-coded status badges
- Match score indicators
- Professional typography
- Smooth transitions

## 🔧 Configuration

Edit `config.py` to customize:

```python
GOOGLE_SEARCH_CONFIG = {
    "keywords": [
        "enterprise architect",
        "chief technology officer",
        "director technology",
        # Add your target roles
    ],
    "primary_location": "Washington DC",
    "date_range": "past_week",
    "min_salary": 150000,
    "experience_levels": ["senior", "director", "executive"],
}
```

## 📊 API Endpoints

- `GET /api/jobs` - List jobs with filters
- `GET /api/jobs/{id}` - Get job details
- `PUT /api/jobs/{id}/status` - Update job status
- `PUT /api/jobs/{id}/notes` - Update notes
- `GET /api/stats` - Dashboard statistics
- `POST /api/scrape` - Trigger job scraping
- `POST /api/score` - Trigger job scoring
- `GET /api/config` - Get configuration
- `GET /api/jobs/export/csv` - Export jobs

Full API documentation: http://localhost:8000/docs

## 🚢 Production Deployment

### Build Frontend

```bash
cd frontend
npm run build
```

### Deploy Options

**Option 1: Vercel (Frontend) + Railway (Backend)**
- Frontend: Deploy to Vercel
- Backend: Deploy to Railway with database

**Option 2: All-in-One with Docker**
```dockerfile
# Build both frontend and backend
# Serve frontend static files via FastAPI
```

**Option 3: Traditional Hosting**
- VPS (DigitalOcean, Linode, AWS EC2)
- Nginx reverse proxy
- PM2 or systemd for process management

## 🔍 Troubleshooting

**Backend won't start:**
- Verify API keys are set: `echo $SCRAPERAPI_KEY`
- Check port 8000 is available
- Activate virtual environment

**Frontend won't connect:**
- Ensure backend is running at localhost:8000
- Check browser console for CORS errors
- Verify network tab shows API calls

**Scraping fails:**
- Verify ScraperAPI key and credits
- Check rate limits
- Review error messages in terminal

**Scoring fails:**
- Verify Anthropic API key
- Ensure resume.txt exists
- Check Claude API credits

## 📝 Documentation

- **QUICKSTART.md** - Comprehensive setup guide
- **frontend/README.md** - Frontend documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **API Docs** - http://localhost:8000/docs

## 🎓 Tech Stack

**Frontend:**
- React 18 with TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Query (data fetching)
- React Router (navigation)
- Recharts (charts)
- Lucide React (icons)

**Backend:**
- FastAPI (API framework)
- Pydantic (data validation)
- SQLite (database)
- Anthropic Claude (AI)
- ScraperAPI (web scraping)

## 📈 Roadmap

- [ ] User authentication
- [ ] Email job alerts
- [ ] Browser extension
- [ ] Mobile app
- [ ] Resume builder
- [ ] Interview prep AI
- [ ] Salary insights
- [ ] Company research

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 💬 Support

- Create an issue for bugs
- Check documentation first
- Review API docs for backend questions

## ⭐ Acknowledgments

- Anthropic for Claude AI
- ScraperAPI for web scraping
- LinkedIn for design inspiration
- Open source community

---

**Built with ❤️ for job seekers everywhere**

Start your job search: `./start.sh`

