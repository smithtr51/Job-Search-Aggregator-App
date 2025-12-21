"""
Background task handlers for long-running operations.
"""

import asyncio
from typing import Callable
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import save_job
from scraper import GoogleJobScraper
from scorer import score_all_unscored_jobs


async def run_scraper_task() -> dict:
    """Run the job scraper in the background."""
    try:
        scraper = GoogleJobScraper()
        count = 0
        
        # Run scraper in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def scrape_jobs():
            nonlocal count
            for job in scraper.search_all():
                save_job(job)
                count += 1
            return count
        
        count = await loop.run_in_executor(None, scrape_jobs)
        
        return {
            "status": "completed",
            "message": f"Successfully scraped {count} jobs",
            "jobs_found": count
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Scraping failed: {str(e)}",
            "jobs_found": 0
        }


async def run_scorer_task(resume_path: str = None) -> dict:
    """Run the job scorer in the background."""
    try:
        loop = asyncio.get_event_loop()
        
        def score_jobs():
            return score_all_unscored_jobs(resume_path)
        
        await loop.run_in_executor(None, score_jobs)
        
        return {
            "status": "completed",
            "message": "Successfully scored all unscored jobs"
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Scoring failed: {str(e)}"
        }

