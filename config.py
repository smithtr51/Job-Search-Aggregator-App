"""
Configuration for job search aggregator.
Add/modify target career pages and search parameters here.
"""

# Target career pages - federal contractors and companies of interest
# Format: (company_name, careers_url, search_keywords)
TARGET_SITES = [
    {
        "name": "BAE Systems",
        "careers_url": "https://jobs.baesystems.com/global/en/search-results",
        "search_params": {"keywords": "enterprise architect", "location": "Washington DC"},
        "type": "workday"  # Helps select the right parser
    },
    {
        "name": "Maximus",
        "careers_url": "https://maximus.avature.net/careers/SearchJobs",
        "search_params": {"keywords": "technology"},
        "type": "avature"
    },
    {
        "name": "Leidos",
        "careers_url": "https://leidos.wd5.myworkdayjobs.com/External",
        "search_params": {"keywords": "chief architect"},
        "type": "workday"
    },
    # SAIC - Cloudflare protected, requires manual access
    # {
    #     "name": "SAIC",
    #     "careers_url": "https://jobs.saic.com/search-jobs",
    #     "search_params": {"keywords": "enterprise architect"},
    #     "type": "icims"
    # },
    {
        "name": "Booz Allen Hamilton",
        "careers_url": "https://careers.boozallen.com/jobs/search",
        "search_params": {"keywords": "chief technology officer"},
        "type": "workday"  # Uses Playwright for JS rendering
    },
    {
        "name": "General Dynamics IT",
        "careers_url": "https://gdit.wd5.myworkdayjobs.com/en-US/External_Career_Site",
        "search_params": {"keywords": "enterprise architect"},
        "type": "workday"
    },
]

# Keywords to search for across all sites
DEFAULT_SEARCH_TERMS = [
    "enterprise architect",
    "chief technology officer",
    "director technology",
    "cloud architect",
    "IT director federal",
]

# Minimum match score (0-100) to flag as high priority
MIN_MATCH_SCORE = 70

# Database path
DATABASE_PATH = "jobs.db"

# Your resume file path (used for matching)
RESUME_PATH = "resume.txt"

# Rate limiting - seconds between requests to same domain
REQUEST_DELAY = 2.0

# LLM configuration for job matching
LLM_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
}
