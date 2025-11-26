"""
Database models and storage operations for job postings.
Uses SQLite for simplicity - easily swappable for PostgreSQL if needed.
"""

import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from config import DATABASE_PATH


@dataclass
class Job:
    """Represents a job posting."""
    id: Optional[int] = None
    company: str = ""
    title: str = ""
    location: str = ""
    description: str = ""
    url: str = ""
    posted_date: Optional[str] = None
    scraped_at: str = ""
    match_score: Optional[float] = None
    match_reasoning: Optional[str] = None
    status: str = "new"  # new, reviewed, applied, rejected, interviewing
    notes: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database schema."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                location TEXT,
                description TEXT,
                url TEXT UNIQUE,
                posted_date TEXT,
                scraped_at TEXT NOT NULL,
                match_score REAL,
                match_reasoning TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(match_score DESC)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)
        """)
        
        conn.commit()
        print("Database initialized.")


def save_job(job: Job) -> int:
    """
    Save a job posting. Updates if URL already exists, inserts if new.
    Returns the job ID.
    """
    with get_db() as conn:
        # Check if job already exists by URL
        existing = conn.execute(
            "SELECT id FROM jobs WHERE url = ?", (job.url,)
        ).fetchone()
        
        if existing:
            # Update existing job
            conn.execute("""
                UPDATE jobs SET
                    company = ?,
                    title = ?,
                    location = ?,
                    description = ?,
                    posted_date = ?,
                    scraped_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE url = ?
            """, (
                job.company, job.title, job.location, job.description,
                job.posted_date, job.scraped_at, job.url
            ))
            conn.commit()
            return existing['id']
        else:
            # Insert new job
            cursor = conn.execute("""
                INSERT INTO jobs (
                    company, title, location, description, url,
                    posted_date, scraped_at, match_score, match_reasoning, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.company, job.title, job.location, job.description, job.url,
                job.posted_date, job.scraped_at, job.match_score, 
                job.match_reasoning, job.status, job.notes
            ))
            conn.commit()
            return cursor.lastrowid


def update_match_score(job_id: int, score: float, reasoning: str):
    """Update the match score for a job."""
    with get_db() as conn:
        conn.execute("""
            UPDATE jobs SET
                match_score = ?,
                match_reasoning = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (score, reasoning, job_id))
        conn.commit()


def update_job_status(job_id: int, status: str, notes: str = None):
    """Update the status of a job application."""
    with get_db() as conn:
        if notes:
            conn.execute("""
                UPDATE jobs SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, notes, job_id))
        else:
            conn.execute("""
                UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, job_id))
        conn.commit()


def get_jobs(
    status: str = None,
    min_score: float = None,
    company: str = None,
    limit: int = 100
) -> list[Job]:
    """Retrieve jobs with optional filters."""
    with get_db() as conn:
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if min_score is not None:
            query += " AND match_score >= ?"
            params.append(min_score)
        
        if company:
            query += " AND company LIKE ?"
            params.append(f"%{company}%")
        
        query += " ORDER BY match_score DESC NULLS LAST LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        return [Job(**dict(row)) for row in rows]


def get_job_by_id(job_id: int) -> Optional[Job]:
    """Get a single job by ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return Job(**dict(row)) if row else None


def get_unscored_jobs() -> list[Job]:
    """Get jobs that haven't been scored yet."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE match_score IS NULL"
        ).fetchall()
        return [Job(**dict(row)) for row in rows]


def get_stats() -> dict:
    """Get summary statistics."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        by_status = dict(conn.execute("""
            SELECT status, COUNT(*) FROM jobs GROUP BY status
        """).fetchall())
        avg_score = conn.execute(
            "SELECT AVG(match_score) FROM jobs WHERE match_score IS NOT NULL"
        ).fetchone()[0]
        by_company = dict(conn.execute("""
            SELECT company, COUNT(*) FROM jobs GROUP BY company ORDER BY COUNT(*) DESC
        """).fetchall())
        
        return {
            "total_jobs": total,
            "by_status": by_status,
            "average_match_score": round(avg_score, 1) if avg_score else None,
            "by_company": by_company,
        }


if __name__ == "__main__":
    init_db()
