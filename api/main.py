"""
FastAPI backend for Job Search Aggregator.
Provides REST API for the React frontend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import sys
import os
from typing import Optional
import io
import csv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import (
    init_db, get_jobs, get_job_by_id, update_job_status as db_update_job_status,
    get_stats, get_unscored_jobs
)
from config import GOOGLE_SEARCH_CONFIG, MIN_MATCH_SCORE
from api.models import (
    JobResponse, JobStatusUpdate, JobNotesUpdate, JobFilters,
    StatsResponse, TaskResponse, ConfigResponse
)
from api.background import run_scraper_task, run_scorer_task

# Initialize FastAPI app
app = FastAPI(
    title="Job Search Aggregator API",
    description="Backend API for LinkedIn-style job search application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Job Search Aggregator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/jobs", response_model=list[JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    company: Optional[str] = None,
    limit: int = 100
):
    """
    Get list of jobs with optional filters.
    
    - **status**: Filter by application status (new, reviewed, applied, rejected, interviewing)
    - **min_score**: Minimum match score (0-100)
    - **company**: Filter by company name (partial match)
    - **limit**: Maximum number of results (default 100, max 500)
    """
    try:
        jobs = get_jobs(status=status, min_score=min_score, company=company, limit=min(limit, 500))
        return [JobResponse(**job.to_dict()) for job in jobs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    """
    Get details for a specific job by ID.
    """
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return JobResponse(**job.to_dict())


@app.put("/api/jobs/{job_id}/status")
async def update_status(job_id: int, update: JobStatusUpdate):
    """
    Update the status of a job.
    
    Valid statuses: new, reviewed, applied, rejected, interviewing
    """
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        db_update_job_status(job_id, update.status)
        return {"message": "Status updated successfully", "job_id": job_id, "status": update.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/jobs/{job_id}/notes")
async def update_notes(job_id: int, update: JobNotesUpdate):
    """
    Update the notes for a job.
    """
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        db_update_job_status(job_id, job.status, update.notes)
        return {"message": "Notes updated successfully", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def get_statistics():
    """
    Get summary statistics about jobs.
    
    Returns:
    - Total number of jobs
    - Breakdown by status
    - Average match score
    - Breakdown by company
    """
    try:
        stats = get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape", response_model=TaskResponse)
async def trigger_scrape(background_tasks: BackgroundTasks):
    """
    Trigger job scraping in the background.
    
    This will search for jobs using Google Search via ScraperAPI
    based on the configuration in config.py.
    """
    task_id = f"scrape_{os.urandom(8).hex()}"
    
    async def scrape_and_notify():
        result = await run_scraper_task()
        # In a production app, you'd store this result and provide a status endpoint
        print(f"Scraping task {task_id} completed: {result}")
    
    background_tasks.add_task(scrape_and_notify)
    
    return TaskResponse(
        task_id=task_id,
        status="started",
        message="Scraping job started in background"
    )


@app.post("/api/score", response_model=TaskResponse)
async def trigger_scoring(background_tasks: BackgroundTasks):
    """
    Trigger job scoring in the background.
    
    This will score all unscored jobs against your resume using Claude AI.
    """
    unscored = get_unscored_jobs()
    if not unscored:
        return TaskResponse(
            task_id="",
            status="completed",
            message="No unscored jobs to process"
        )
    
    task_id = f"score_{os.urandom(8).hex()}"
    
    async def score_and_notify():
        result = await run_scorer_task()
        print(f"Scoring task {task_id} completed: {result}")
    
    background_tasks.add_task(score_and_notify)
    
    return TaskResponse(
        task_id=task_id,
        status="started",
        message=f"Scoring started for {len(unscored)} jobs"
    )


@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """
    Get the current search configuration.
    """
    return ConfigResponse(
        keywords=GOOGLE_SEARCH_CONFIG.get('keywords', []),
        primary_location=GOOGLE_SEARCH_CONFIG.get('primary_location', ''),
        date_range=GOOGLE_SEARCH_CONFIG.get('date_range', 'past_week'),
        included_sites=GOOGLE_SEARCH_CONFIG.get('included_sites', []),
        experience_levels=GOOGLE_SEARCH_CONFIG.get('experience_levels', []),
        min_salary=GOOGLE_SEARCH_CONFIG.get('min_salary'),
        max_salary=GOOGLE_SEARCH_CONFIG.get('max_salary'),
        results_per_search=GOOGLE_SEARCH_CONFIG.get('results_per_search', 100)
    )


@app.get("/api/jobs/export/csv")
async def export_jobs_csv(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    company: Optional[str] = None
):
    """
    Export jobs to CSV file.
    """
    try:
        jobs = get_jobs(status=status, min_score=min_score, company=company, limit=10000)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'id', 'company', 'title', 'location', 'match_score', 'status',
            'url', 'scraped_at', 'notes'
        ])
        writer.writeheader()
        
        for job in jobs:
            writer.writerow({
                'id': job.id,
                'company': job.company,
                'title': job.title,
                'location': job.location or '',
                'match_score': job.match_score or '',
                'status': job.status,
                'url': job.url,
                'scraped_at': job.scraped_at,
                'notes': job.notes or ''
            })
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=jobs_export.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "job-search-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

