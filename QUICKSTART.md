# LinkedIn-Style Job Search - Quick Start Guide

Complete guide to get your LinkedIn-style job search application up and running.

## Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys:
  - ScraperAPI key (for web scraping)
  - Anthropic API key (for AI job scoring)

## Step 1: Set Up API Keys

### Option A: Environment Variables (Recommended)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export SCRAPERAPI_KEY='your_scraperapi_key_here'
export ANTHROPIC_API_KEY='your_anthropic_key_here'
```

Then reload:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option B: .env File

Create a `.env` file in the project root:

```bash
SCRAPERAPI_KEY=your_scraperapi_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Step 2: Backend Setup

```bash
# Navigate to project directory
cd /path/to/Job-Search-Aggregator-App

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Initialize database
python -c "from storage import init_db; init_db()"

# Start FastAPI backend
cd api
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

## Step 3: Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd /path/to/Job-Search-Aggregator-App/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Step 4: Create Your Resume File

Create a `resume.txt` file in the project root with your resume content (plain text format works best).

## Step 5: Start Using the Application

1. **Open the application** at `http://localhost:5173`

2. **Go to Settings** page to:
   - View your search configuration
   - Start scraping jobs
   - Score jobs against your resume
   - Export jobs as CSV

3. **Go to Jobs** page to:
   - Browse all jobs with LinkedIn-style interface
   - Filter by company, status, and match score
   - View detailed job information
   - Update application status
   - Add personal notes

4. **Go to Dashboard** page to:
   - View statistics and charts
   - See your job search progress
   - Identify high-match opportunities

## Common Commands

### Backend

```bash
# Start backend
cd api && uvicorn main:app --reload

# Run scraper via CLI (alternative to UI)
python main.py scrape

# Score jobs via CLI
python main.py score

# View jobs in CLI
python main.py list --min-score 70
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## File Structure

```
Job-Search-Aggregator-App/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # Pydantic models
│   └── background.py      # Background tasks
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   ├── hooks/        # Custom hooks
│   │   └── types/        # TypeScript types
│   └── package.json
├── storage.py             # Database operations
├── scraper.py             # Web scraping logic
├── scorer.py              # AI job scoring
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
└── resume.txt             # Your resume (create this)
```

## Troubleshooting

### Backend won't start

- Make sure virtual environment is activated
- Check that port 8000 is not in use
- Verify API keys are set correctly

### Frontend won't connect to backend

- Ensure backend is running at `http://localhost:8000`
- Check browser console for errors
- Verify CORS settings in `api/main.py`

### Scraping fails

- Verify SCRAPERAPI_KEY is set correctly
- Check your ScraperAPI account has credits
- Review error messages in terminal

### Scoring fails

- Verify ANTHROPIC_API_KEY is set correctly
- Ensure `resume.txt` exists in project root
- Check Anthropic API account has credits

## Production Deployment

### Build Frontend

```bash
cd frontend
npm run build
```

### Serve with FastAPI

Update `api/main.py` to serve static files:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
```

Then run:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Next Steps

- Customize search keywords in `config.py`
- Add your target locations
- Set salary ranges
- Configure experience levels
- Start scraping and scoring!

## Support

For issues or questions:
- Check the API docs at `http://localhost:8000/docs`
- Review logs in the terminal
- Ensure all dependencies are installed

