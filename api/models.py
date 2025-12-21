"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobBase(BaseModel):
    """Base job model."""
    company: str
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: str
    posted_date: Optional[str] = None
    scraped_at: str


class JobResponse(JobBase):
    """Job response model with all fields."""
    id: int
    match_score: Optional[float] = None
    match_reasoning: Optional[str] = None
    status: str = "new"
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class JobStatusUpdate(BaseModel):
    """Model for updating job status."""
    status: str = Field(..., pattern="^(new|reviewed|applied|rejected|interviewing)$")


class JobNotesUpdate(BaseModel):
    """Model for updating job notes."""
    notes: str


class JobFilters(BaseModel):
    """Model for job filtering."""
    status: Optional[str] = None
    min_score: Optional[float] = None
    company: Optional[str] = None
    limit: int = Field(default=100, le=500)


class StatsResponse(BaseModel):
    """Statistics response model."""
    total_jobs: int
    by_status: dict[str, int]
    average_match_score: Optional[float] = None
    by_company: dict[str, int]


class TaskResponse(BaseModel):
    """Response for background task operations."""
    task_id: str
    status: str
    message: str


class ConfigResponse(BaseModel):
    """Search configuration response."""
    keywords: list[str]
    primary_location: str
    date_range: str
    included_sites: list[str]
    experience_levels: list[str]
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    results_per_search: int

