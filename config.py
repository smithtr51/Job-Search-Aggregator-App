"""
Configuration for job search aggregator.
Add/modify target career pages and search parameters here.
"""

# Target locations - DC Metro Area and Remote
TARGET_LOCATIONS = [
    "Washington, DC",
    "Remote",
    # Northern Virginia
    "Arlington, VA", "Alexandria, VA", "Fairfax, VA", "Falls Church, VA",
    "Reston, VA", "McLean, VA", "Tysons, VA", "Chantilly, VA",
    "Herndon, VA", "Vienna, VA", "Sterling, VA", "Manassas, VA",
    # Montgomery County, MD
    "Bethesda, MD", "Rockville, MD", "Silver Spring, MD", 
    "Gaithersburg, MD", "Germantown, MD",
    # Prince George's County, MD
    "College Park, MD", "Bowie, MD", "Greenbelt, MD", 
    "Largo, MD", "Fort Washington, MD", "Suitland, MD",
    # Anne Arundel County, MD
    "Annapolis, MD", "Fort Meade, MD", "Glen Burnie, MD", "Severn, MD",
    # Howard County, MD
    "Columbia, MD", "Ellicott City, MD", "Laurel, MD",
]

# Google Search Configuration
GOOGLE_SEARCH_CONFIG = {
    # Keywords - will be combined with location
    "keywords": [
        "enterprise architect",
        "chief technology officer",
        "director technology",
        "cloud architect",
        "IT director federal",
        "solutions architect",
        "technical director",
    ],
    
    # Location filters (keep existing TARGET_LOCATIONS)
    "locations": TARGET_LOCATIONS,
    "primary_location": "Washington DC",
    
    # Date range filter
    "date_range": "past_week",  # Options: past_24h, past_week, past_month, any_time
    
    # Site filters
    "included_sites": [
        "linkedin.com/jobs",
        "indeed.com",
        "glassdoor.com",
        "monster.com",
        "clearancejobs.com",
        "usajobs.gov",
        "dice.com",
        # Company career pages will be found automatically
    ],
    "excluded_sites": [],  # Sites to exclude
    
    # Salary range (optional)
    "min_salary": 150000,
    "max_salary": None,
    
    # Experience level
    "experience_levels": ["senior", "director", "executive"],
    
    # Results per search
    "results_per_search": 100,
    
    # Search query template
    "query_template": "{keyword} {location} {experience_level}",
}

# Minimum match score (0-100) to flag as high priority
MIN_MATCH_SCORE = 70

# Database path
DATABASE_PATH = "jobs.db"

# Your resume file path (used for matching)
RESUME_PATH = "resume.txt"

# LLM configuration for job matching
LLM_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
}
