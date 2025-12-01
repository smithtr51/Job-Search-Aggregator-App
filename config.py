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

# Location search string for job sites (condensed for search queries)
LOCATION_SEARCH = "Washington DC"

# Target career pages - federal contractors and companies of interest
# Format: (company_name, careers_url, search_keywords)
TARGET_SITES = [
    # ============ EXISTING FEDERAL CONTRACTORS ============
    {
        "name": "BAE Systems",
        "careers_url": "https://jobs.baesystems.com/global/en/search-results",
        "search_params": {"keywords": "enterprise architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Maximus",
        "careers_url": "https://maximus.avature.net/careers/SearchJobs",
        "search_params": {"keywords": "technology", "location": "Washington DC"},
        "type": "avature"
    },
    {
        "name": "Leidos",
        "careers_url": "https://leidos.wd5.myworkdayjobs.com/External",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Booz Allen Hamilton",
        "careers_url": "https://careers.boozallen.com/jobs/search",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "General Dynamics IT",
        "careers_url": "https://gdit.wd5.myworkdayjobs.com/en-US/External_Career_Site",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    
    # ============ NEW FEDERAL CONTRACTORS ============
    {
        "name": "Northrop Grumman",
        "careers_url": "https://www.northropgrumman.com/jobs",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Raytheon Technologies",
        "careers_url": "https://careers.rtx.com/global/en/search-results",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Lockheed Martin",
        "careers_url": "https://www.lockheedmartinjobs.com/search-jobs",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Accenture Federal Services",
        "careers_url": "https://accenture.wd3.myworkdayjobs.com/AccentureFederalServicesCareers",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Deloitte",
        "careers_url": "https://apply.deloitte.com/careers/SearchJobs",
        "search_params": {"keywords": "architect federal", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "ManTech",
        "careers_url": "https://mantech.wd1.myworkdayjobs.com/External",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "CACI International",
        "careers_url": "https://caci.wd1.myworkdayjobs.com/External",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Peraton",
        "careers_url": "https://careers.peraton.com/",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "CGI Federal",
        "careers_url": "https://cgi.njoyn.com/corp/xweb/xweb.asp?page=joblisting",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "custom"
    },
    {
        "name": "ICF International",
        "careers_url": "https://icf.wd5.myworkdayjobs.com/ICFExternal",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    
    # ============ INDUSTRY / COMMERCIAL EMPLOYERS ============
    {
        "name": "Amazon Web Services",
        "careers_url": "https://www.amazon.jobs/en/search",
        "search_params": {"keywords": "solutions architect", "location": "Washington DC"},
        "type": "custom"
    },
    {
        "name": "Microsoft",
        "careers_url": "https://careers.microsoft.com/us/en/search-results",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Google",
        "careers_url": "https://www.google.com/about/careers/applications/jobs/results",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "custom"
    },
    {
        "name": "Oracle",
        "careers_url": "https://www.oracle.com/careers/",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Salesforce",
        "careers_url": "https://careers.salesforce.com/en/jobs/",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "IBM",
        "careers_url": "https://www.ibm.com/careers/",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Cisco",
        "careers_url": "https://jobs.cisco.com/jobs/SearchJobs",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Dell Technologies",
        "careers_url": "https://dell.wd1.myworkdayjobs.com/en-US/External",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "VMware (Broadcom)",
        "careers_url": "https://broadcom.wd1.myworkdayjobs.com/en-US/External",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
        "type": "workday"
    },
    {
        "name": "Palo Alto Networks",
        "careers_url": "https://paloaltonetworks.wd1.myworkdayjobs.com/en-US/External",
        "search_params": {"keywords": "architect", "location": "Washington DC"},
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
    "remote",
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
