"""
Background task handlers for long-running operations.
"""

import asyncio
from typing import Callable
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import save_job
from scraper import GoogleJobScraper
from scorer import score_all_unscored_jobs
from config import GOOGLE_SEARCH_CONFIG
from api.progress import create_task, update_task, complete_task, fail_task


async def run_scraper_task(task_id: str) -> dict:
    """Run the job scraper in the background with progress tracking."""
    try:
        # Calculate estimated total searches
        num_keywords = len(GOOGLE_SEARCH_CONFIG.get('keywords', []))
        num_exp_levels = len(GOOGLE_SEARCH_CONFIG.get('experience_levels', []))
        total_searches = num_keywords * max(num_exp_levels, 1)
        
        create_task(task_id, "scrape", total_items=total_searches)
        
        scraper = GoogleJobScraper()
        count = 0
        search_count = 0
        start_time = datetime.now()
        
        # Run scraper in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def scrape_jobs():
            nonlocal count, search_count
            
            # Monkey patch to track progress
            original_search_all = scraper.search_all
            
            for job in scraper.search_all():
                save_job(job)
                count += 1
                
                # Update progress every 5 jobs
                if count % 5 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    jobs_per_sec = count / elapsed if elapsed > 0 else 0
                    remaining = max(50 - count, 0)  # Estimate 50 jobs target
                    est_time_remaining = remaining / jobs_per_sec if jobs_per_sec > 0 else 0
                    
                    update_task(
                        task_id,
                        progress=count,
                        total=total_searches,
                        current_item=job.title,
                        message=f"Found {count} jobs. Est. {int(est_time_remaining / 60)} min remaining..."
                    )
            
            return count
        
        count = await loop.run_in_executor(None, scrape_jobs)
        
        complete_task(task_id, f"Successfully scraped {count} jobs")
        
        return {
            "status": "completed",
            "message": f"Successfully scraped {count} jobs",
            "jobs_found": count
        }
    except Exception as e:
        fail_task(task_id, str(e))
        return {
            "status": "failed",
            "message": f"Scraping failed: {str(e)}",
            "jobs_found": 0
        }


async def run_scorer_task(task_id: str, resume_path: str = None) -> dict:
    """Run the job scorer in the background with progress tracking."""
    try:
        from storage import get_unscored_jobs
        
        unscored = get_unscored_jobs()
        total_jobs = len(unscored)
        
        create_task(task_id, "score", total_items=total_jobs)
        
        loop = asyncio.get_event_loop()
        start_time = datetime.now()
        
        def score_jobs():
            # This will be updated if we modify scorer.py to report progress
            update_task(task_id, message=f"Scoring {total_jobs} jobs...")
            return score_all_unscored_jobs(resume_path)
        
        await loop.run_in_executor(None, score_jobs)
        
        complete_task(task_id, f"Successfully scored {total_jobs} jobs")
        
        return {
            "status": "completed",
            "message": f"Successfully scored {total_jobs} jobs"
        }
    except Exception as e:
        fail_task(task_id, str(e))
        return {
            "status": "failed",
            "message": f"Scoring failed: {str(e)}"
        }

