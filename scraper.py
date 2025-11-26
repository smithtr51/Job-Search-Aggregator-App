"""
Web scraper for job postings from various career sites.
Handles different ATS systems (Workday, iCIMS, Greenhouse, etc.)
"""

import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlencode
from typing import Generator
import json

import requests
from bs4 import BeautifulSoup

from config import TARGET_SITES, REQUEST_DELAY, DEFAULT_SEARCH_TERMS
from storage import Job


class JobScraper:
    """Base scraper with common functionality."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.last_request_time = {}
    
    def _rate_limit(self, domain: str):
        """Enforce rate limiting per domain."""
        now = time.time()
        if domain in self.last_request_time:
            elapsed = now - self.last_request_time[domain]
            if elapsed < REQUEST_DELAY:
                time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time[domain] = time.time()
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page with rate limiting."""
        domain = self._get_domain(url)
        self._rate_limit(domain)
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def fetch_json(self, url: str, params: dict = None) -> dict:
        """Fetch JSON data from an API endpoint."""
        domain = self._get_domain(url)
        self._rate_limit(domain)
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None


class USAJobsScraper(JobScraper):
    """
    Scraper for USAJobs.gov - uses their public API.
    This is a great source for federal positions.
    Requires API key from https://developer.usajobs.gov/
    """
    
    BASE_URL = "https://data.usajobs.gov/api/search"
    
    def __init__(self, api_key: str = None, email: str = None):
        super().__init__()
        self.api_key = api_key
        if api_key and email:
            self.session.headers.update({
                'Authorization-Key': api_key,
                'User-Agent': email,
            })
    
    def search(self, keyword: str, location: str = None) -> Generator[Job, None, None]:
        """Search USAJobs for positions."""
        if not self.api_key:
            print("USAJobs requires an API key. Get one at https://developer.usajobs.gov/")
            return
        
        params = {
            'Keyword': keyword,
            'ResultsPerPage': 50,
        }
        if location:
            params['LocationName'] = location
        
        data = self.fetch_json(self.BASE_URL, params)
        if not data:
            return
        
        results = data.get('SearchResult', {}).get('SearchResultItems', [])
        
        for item in results:
            match = item.get('MatchedObjectDescriptor', {})
            yield Job(
                company="US Federal Government",
                title=match.get('PositionTitle', ''),
                location=match.get('PositionLocationDisplay', ''),
                description=match.get('UserArea', {}).get('Details', {}).get('JobSummary', ''),
                url=match.get('PositionURI', ''),
                posted_date=match.get('PublicationStartDate', ''),
                scraped_at=datetime.now().isoformat(),
            )


class GenericCareerPageScraper(JobScraper):
    """
    Generic scraper that attempts to find job listings on any career page.
    Uses heuristics to identify job posting patterns.
    """
    
    # Common patterns for job links
    JOB_LINK_PATTERNS = [
        r'/job[s]?/',
        r'/career[s]?/',
        r'/position[s]?/',
        r'/opening[s]?/',
        r'/requisition/',
        r'job[-_]?id=',
        r'req[-_]?id=',
    ]
    
    def scrape_site(self, site_config: dict, search_term: str = None) -> Generator[Job, None, None]:
        """
        Attempt to scrape jobs from a career page.
        This is a best-effort approach that works for many sites.
        """
        company = site_config['name']
        base_url = site_config['careers_url']
        
        print(f"Scraping {company}...")
        
        soup = self.fetch_page(base_url)
        if not soup:
            return
        
        # Find all links that look like job postings
        job_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            for pattern in self.JOB_LINK_PATTERNS:
                if re.search(pattern, href, re.IGNORECASE):
                    full_url = urljoin(base_url, href)
                    if full_url not in job_links:
                        job_links.append(full_url)
                    break
        
        print(f"Found {len(job_links)} potential job links")
        
        # Scrape each job page
        for url in job_links[:20]:  # Limit to first 20 to be polite
            job = self._scrape_job_page(url, company)
            if job:
                yield job
    
    def _scrape_job_page(self, url: str, company: str) -> Job:
        """Extract job details from a job posting page."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Try to extract title
        title = None
        for selector in ['h1', '.job-title', '.position-title', '[class*="title"]']:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                break
        
        # Try to extract description
        description = None
        for selector in ['.job-description', '.description', '[class*="description"]', 'article', 'main']:
            elem = soup.select_one(selector)
            if elem:
                description = elem.get_text(separator=' ', strip=True)[:5000]  # Limit length
                break
        
        # Try to extract location
        location = None
        for selector in ['.location', '[class*="location"]', '[class*="Location"]']:
            elem = soup.select_one(selector)
            if elem:
                location = elem.get_text(strip=True)
                break
        
        if title:
            return Job(
                company=company,
                title=title,
                location=location or "",
                description=description or "",
                url=url,
                scraped_at=datetime.now().isoformat(),
            )
        
        return None


class GoogleSearchScraper(JobScraper):
    """
    Uses Google Custom Search API to find job postings.
    More reliable than scraping individual sites.
    Requires Google Custom Search API key and Search Engine ID.
    """
    
    BASE_URL = "https://www.googleapis.com/customsearch/v1"
    
    def __init__(self, api_key: str = None, search_engine_id: str = None):
        super().__init__()
        self.api_key = api_key
        self.search_engine_id = search_engine_id
    
    def search(self, query: str, site: str = None) -> list[dict]:
        """
        Search for jobs using Google Custom Search.
        
        Args:
            query: Search terms (e.g., "enterprise architect federal")
            site: Optional site filter (e.g., "jobs.baesystems.com")
        """
        if not self.api_key or not self.search_engine_id:
            print("Google Custom Search requires API key and Search Engine ID")
            return []
        
        if site:
            query = f"site:{site} {query}"
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 10,
        }
        
        data = self.fetch_json(self.BASE_URL, params)
        return data.get('items', []) if data else []


def scrape_all_sites(sites: list[dict] = None) -> Generator[Job, None, None]:
    """
    Scrape all configured sites and yield jobs.
    """
    sites = sites or TARGET_SITES
    scraper = GenericCareerPageScraper()
    
    for site in sites:
        try:
            for job in scraper.scrape_site(site):
                yield job
        except Exception as e:
            print(f"Error scraping {site['name']}: {e}")
            continue


if __name__ == "__main__":
    # Test the scraper
    print("Testing generic scraper...")
    for job in scrape_all_sites(TARGET_SITES[:1]):
        print(f"Found: {job.title} at {job.company}")
        print(f"URL: {job.url}")
        print("---")
