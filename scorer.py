"""
Job matching and scoring using LLM.
Compares job descriptions against resume to generate match scores.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

from config import LLM_CONFIG, RESUME_PATH, MIN_MATCH_SCORE
from storage import Job, get_unscored_jobs, update_match_score


def load_resume(path: str = None) -> str:
    """Load resume from file."""
    path = path or RESUME_PATH
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Resume not found at {path}. "
            "Please create a resume.txt file with your resume content."
        )
    return Path(path).read_text()


def score_job(job: Job, resume: str, client: Anthropic = None) -> tuple[float, str]:
    """
    Score a job posting against a resume.
    
    Returns:
        tuple of (score 0-100, reasoning string)
    """
    client = client or Anthropic()
    
    prompt = f"""You are a job matching expert. Analyze how well this job posting matches the candidate's resume.

CANDIDATE RESUME:
{resume}

JOB POSTING:
Company: {job.company}
Title: {job.title}
Location: {job.location}

Description:
{job.description[:4000]}

Evaluate the match on these criteria:
1. Skills alignment (technical skills, tools, frameworks)
2. Experience level match (years of experience, seniority)
3. Industry/domain fit (federal, commercial, specific sectors)
4. Certifications/clearances match
5. Location compatibility

Provide your response in this exact format:
SCORE: [number 0-100]
REASONING: [2-3 sentences explaining the match, highlighting key alignments and gaps]
KEY_MATCHES: [comma-separated list of matching qualifications]
KEY_GAPS: [comma-separated list of missing requirements, or "None" if none]
"""

    response = client.messages.create(
        model=LLM_CONFIG["model"],
        max_tokens=LLM_CONFIG["max_tokens"],
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.content[0].text
    
    # Parse the response
    score = 0
    reasoning = content
    
    for line in content.split('\n'):
        if line.startswith('SCORE:'):
            try:
                score = float(line.replace('SCORE:', '').strip())
            except ValueError:
                score = 50  # Default if parsing fails
        elif line.startswith('REASONING:'):
            reasoning = line.replace('REASONING:', '').strip()
    
    # Append key matches/gaps to reasoning
    for line in content.split('\n'):
        if line.startswith('KEY_MATCHES:'):
            matches = line.replace('KEY_MATCHES:', '').strip()
            reasoning += f"\n\nKey matches: {matches}"
        elif line.startswith('KEY_GAPS:'):
            gaps = line.replace('KEY_GAPS:', '').strip()
            if gaps.lower() != "none":
                reasoning += f"\nGaps: {gaps}"
    
    return score, reasoning


def generate_cover_letter_points(job: Job, resume: str, client: Anthropic = None) -> str:
    """
    Generate key points to emphasize in a cover letter for this job.
    """
    client = client or Anthropic()
    
    prompt = f"""Based on this job posting and resume, identify the 3-5 most important points 
the candidate should emphasize in their cover letter.

RESUME:
{resume}

JOB POSTING:
Company: {job.company}
Title: {job.title}
Description:
{job.description[:3000]}

For each point:
1. Identify a specific requirement from the job
2. Connect it to a specific accomplishment from the resume
3. Suggest how to frame it

Format as bullet points.
"""

    response = client.messages.create(
        model=LLM_CONFIG["model"],
        max_tokens=LLM_CONFIG["max_tokens"],
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


def identify_resume_gaps(job: Job, resume: str, client: Anthropic = None) -> str:
    """
    Identify gaps in the resume relative to job requirements
    and suggest how to address them.
    """
    client = client or Anthropic()
    
    prompt = f"""Analyze this job posting against the candidate's resume.
Identify any gaps or weaknesses, and suggest how to address them.

RESUME:
{resume}

JOB POSTING:
Company: {job.company}
Title: {job.title}
Description:
{job.description[:3000]}

For each gap:
1. What requirement is not clearly met?
2. Does the candidate likely have relevant experience that isn't highlighted?
3. How could they reframe existing experience to address this?
4. Is this a dealbreaker or minor concern?

Be constructive and specific.
"""

    response = client.messages.create(
        model=LLM_CONFIG["model"],
        max_tokens=LLM_CONFIG["max_tokens"],
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


def score_all_unscored_jobs(resume_path: str = None):
    """Score all jobs in the database that don't have scores yet."""
    resume = load_resume(resume_path)
    client = Anthropic()
    
    jobs = get_unscored_jobs()
    print(f"Scoring {len(jobs)} unscored jobs...")
    
    for i, job in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] Scoring: {job.title} at {job.company}...")
        try:
            score, reasoning = score_job(job, resume, client)
            update_match_score(job.id, score, reasoning)
            
            if score >= MIN_MATCH_SCORE:
                print(f"  ★ HIGH MATCH: {score}/100")
            else:
                print(f"  Score: {score}/100")
        except Exception as e:
            print(f"  Error scoring job: {e}")
    
    print("Scoring complete!")


if __name__ == "__main__":
    # Test the scorer
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "score-all":
        score_all_unscored_jobs()
    else:
        print("Usage: python scorer.py score-all")
        print("Make sure you have:")
        print("1. Set ANTHROPIC_API_KEY environment variable")
        print("2. Created resume.txt with your resume")
