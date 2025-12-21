#!/usr/bin/env python3
"""
Job Hunter CLI - Main entry point for the job search aggregator.

Usage:
    python main.py init          Initialize the database
    python main.py scrape        Scrape all configured sites
    python main.py score         Score all unscored jobs
    python main.py list          List jobs (optionally filtered)
    python main.py show <id>     Show details for a specific job
    python main.py stats         Show summary statistics
    python main.py analyze <id>  Deep analysis of a job posting
"""

import argparse
import sys

from storage import (
    init_db, save_job, get_jobs, get_job_by_id, 
    get_stats, update_job_status, update_match_score
)
from scraper import GoogleJobScraper
from scorer import (
    score_all_unscored_jobs, load_resume, score_job,
    generate_cover_letter_points, identify_resume_gaps
)
from config import MIN_MATCH_SCORE


def cmd_init(args):
    """Initialize the database."""
    init_db()
    print("Database initialized successfully.")
    print(f"\nNext steps:")
    print("1. Create resume.txt with your resume content")
    print("2. Run 'python main.py scrape' to fetch jobs")
    print("3. Run 'python main.py score' to score them")


def cmd_scrape(args):
    """Scrape jobs using Google search via ScraperAPI."""
    try:
        scraper = GoogleJobScraper()
    except (ValueError, ImportError) as e:
        print(f"Error: {e}")
        print("\nTo use Google search scraping:")
        print("1. Install scraperapi-sdk: pip install scraperapi-sdk")
        print("2. Set SCRAPERAPI_KEY environment variable")
        print("   Add to ~/.zshrc: export SCRAPERAPI_KEY='your_key_here'")
        sys.exit(1)
    
    print("Searching for jobs via Google...")
    
    count = 0
    for job in scraper.search_all():
        job_id = save_job(job)
        count += 1
    
    print("=" * 60)
    print(f"Scraped {count} jobs total.")
    print("\nRun 'python main.py score' to score these jobs against your resume.")


def cmd_score(args):
    """Score all unscored jobs."""
    try:
        score_all_unscored_jobs(args.resume)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_list(args):
    """List jobs with optional filters."""
    jobs = get_jobs(
        status=args.status,
        min_score=args.min_score,
        company=args.company,
        limit=args.limit
    )
    
    if not jobs:
        print("No jobs found matching criteria.")
        return
    
    print(f"\n{'ID':<5} {'Score':<7} {'Status':<12} {'Company':<20} {'Title':<40}")
    print("-" * 90)
    
    for job in jobs:
        score_str = f"{job.match_score:.0f}" if job.match_score else "—"
        title = job.title[:38] + ".." if len(job.title) > 40 else job.title
        company = job.company[:18] + ".." if len(job.company) > 20 else job.company
        
        # Highlight high-match jobs
        if job.match_score and job.match_score >= MIN_MATCH_SCORE:
            print(f"{job.id:<5} {score_str:<7} {job.status:<12} {company:<20} ★ {title}")
        else:
            print(f"{job.id:<5} {score_str:<7} {job.status:<12} {company:<20} {title}")
    
    print(f"\nShowing {len(jobs)} jobs. Use --min-score, --status, --company to filter.")


def cmd_show(args):
    """Show details for a specific job."""
    job = get_job_by_id(args.job_id)
    
    if not job:
        print(f"Job {args.job_id} not found.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(f"Job #{job.id}: {job.title}")
    print("=" * 60)
    print(f"Company:  {job.company}")
    print(f"Location: {job.location}")
    print(f"Status:   {job.status}")
    print(f"URL:      {job.url}")
    print(f"Scraped:  {job.scraped_at}")
    
    if job.match_score:
        print(f"\nMatch Score: {job.match_score:.0f}/100")
        print(f"Reasoning:\n{job.match_reasoning}")
    
    if job.notes:
        print(f"\nNotes: {job.notes}")
    
    print("\n--- Description ---")
    print(job.description[:2000])
    if len(job.description) > 2000:
        print("\n[Truncated - full description available in database]")


def cmd_stats(args):
    """Show summary statistics."""
    stats = get_stats()
    
    print("\n=== Job Hunt Statistics ===\n")
    print(f"Total jobs tracked: {stats['total_jobs']}")
    
    if stats['average_match_score']:
        print(f"Average match score: {stats['average_match_score']}/100")
    
    print("\nBy Status:")
    for status, count in stats['by_status'].items():
        print(f"  {status}: {count}")
    
    print("\nBy Company:")
    for company, count in list(stats['by_company'].items())[:10]:
        print(f"  {company}: {count}")


def cmd_analyze(args):
    """Deep analysis of a specific job posting."""
    from anthropic import Anthropic
    
    job = get_job_by_id(args.job_id)
    if not job:
        print(f"Job {args.job_id} not found.")
        sys.exit(1)
    
    try:
        resume = load_resume()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    client = Anthropic()
    
    print(f"\nAnalyzing: {job.title} at {job.company}")
    print("=" * 60)
    
    # Score if not already scored
    if not job.match_score:
        print("\nScoring job...")
        score, reasoning = score_job(job, resume, client)
        update_match_score(job.id, score, reasoning)
        print(f"Score: {score}/100")
        print(f"Reasoning: {reasoning}")
    else:
        print(f"\nExisting Score: {job.match_score}/100")
        print(f"Reasoning: {job.match_reasoning}")
    
    print("\n" + "-" * 40)
    print("Cover Letter Key Points:")
    print("-" * 40)
    points = generate_cover_letter_points(job, resume, client)
    print(points)
    
    print("\n" + "-" * 40)
    print("Resume Gap Analysis:")
    print("-" * 40)
    gaps = identify_resume_gaps(job, resume, client)
    print(gaps)


def cmd_status(args):
    """Update job status."""
    job = get_job_by_id(args.job_id)
    if not job:
        print(f"Job {args.job_id} not found.")
        sys.exit(1)
    
    update_job_status(args.job_id, args.new_status, args.notes)
    print(f"Updated job #{args.job_id} status to '{args.new_status}'")


def main():
    parser = argparse.ArgumentParser(
        description="Job Hunter - Automated job search and matching"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # init
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.set_defaults(func=cmd_init)
    
    # scrape
    scrape_parser = subparsers.add_parser('scrape', help='Scrape job sites')
    scrape_parser.set_defaults(func=cmd_scrape)
    
    # score
    score_parser = subparsers.add_parser('score', help='Score unscored jobs')
    score_parser.add_argument('--resume', '-r', help='Path to resume file')
    score_parser.set_defaults(func=cmd_score)
    
    # list
    list_parser = subparsers.add_parser('list', help='List jobs')
    list_parser.add_argument('--status', '-s', help='Filter by status')
    list_parser.add_argument('--min-score', '-m', type=float, help='Minimum match score')
    list_parser.add_argument('--company', '-c', help='Filter by company')
    list_parser.add_argument('--limit', '-l', type=int, default=50, help='Max results')
    list_parser.set_defaults(func=cmd_list)
    
    # show
    show_parser = subparsers.add_parser('show', help='Show job details')
    show_parser.add_argument('job_id', type=int, help='Job ID')
    show_parser.set_defaults(func=cmd_show)
    
    # stats
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)
    
    # analyze
    analyze_parser = subparsers.add_parser('analyze', help='Deep analyze a job')
    analyze_parser.add_argument('job_id', type=int, help='Job ID')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # status
    status_parser = subparsers.add_parser('status', help='Update job status')
    status_parser.add_argument('job_id', type=int, help='Job ID')
    status_parser.add_argument('new_status', 
        choices=['new', 'reviewed', 'applied', 'rejected', 'interviewing'],
        help='New status')
    status_parser.add_argument('--notes', '-n', help='Add notes')
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
