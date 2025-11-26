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

# Playwright is optional - only import if available
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from config import TARGET_SITES, REQUEST_DELAY, DEFAULT_SEARCH_TERMS, TARGET_LOCATIONS
from storage import Job


def is_location_match(job_location: str) -> bool:
    """Check if a job location matches our target DC Metro Area or Remote locations."""
    if not job_location:
        return True  # Include jobs without location info (will be filtered by scoring)
    
    location_lower = job_location.lower()
    
    # Check for remote keywords
    remote_keywords = ['remote', 'telework', 'work from home', 'wfh', 'anywhere']
    if any(keyword in location_lower for keyword in remote_keywords):
        return True
    
    # Check for DC Metro Area locations
    dc_metro_keywords = [
        # DC
        'washington', 'dc', 'd.c.',
        # Virginia
        'virginia', ' va', ',va', 'arlington', 'alexandria', 'fairfax',
        'reston', 'mclean', 'tysons', 'chantilly', 'herndon', 'vienna',
        'sterling', 'manassas', 'falls church',
        # Maryland
        'maryland', ' md', ',md', 'bethesda', 'rockville', 'silver spring',
        'gaithersburg', 'germantown', 'college park', 'bowie', 'greenbelt',
        'largo', 'fort washington', 'suitland', 'annapolis', 'fort meade',
        'glen burnie', 'severn', 'columbia', 'ellicott city', 'laurel',
    ]
    if any(keyword in location_lower for keyword in dc_metro_keywords):
        return True
    
    return False


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


class PlaywrightScraper:
    """
    Scraper using Playwright for JavaScript-heavy sites.
    Works with Workday, iCIMS, Greenhouse, and other modern ATS systems.
    """
    
    # Common selectors for different ATS systems
    ATS_SELECTORS = {
        'workday': {
            'job_list': '[data-automation-id="jobResults"] a, .css-19uc56f a, a[href*="/job/"]',
            'title': 'h1, h2, .job-title, [class*="title"]',
            'location': '[data-automation-id="locations"], .css-129m7dg, [class*="location"]',
            'description': '[data-automation-id="jobPostingDescription"], .css-psnqcr, [class*="description"], article, main',
        },
        'icims': {
            'job_list': '.iCIMS_JobsTable a, a[href*="jobs-"], .jobs-list a',
            'title': 'h1, h2, .iCIMS_Header h1, .job-title',
            'location': '.iCIMS_JobHeaderLocation, .job-location, [class*="location"]',
            'description': '.iCIMS_JobContent, .job-description, [class*="description"], article',
        },
        'avature': {
            'job_list': 'a[href*="FolderDetail"]',
            'title': 'h2, .title, h1',
            'location': '[class*="location"], [class*="Location"]',
            'description': '[class*="description"], .content, article, main',
        },
        'generic': {
            'job_list': 'a[href*="/job"], a[href*="/career"], a[href*="/position"], a[href*="requisition"]',
            'title': 'h1, h2, .job-title, [class*="title"]',
            'location': '[class*="location"], [class*="Location"]',
            'description': '[class*="description"], article, main',
        }
    }
    
    def __init__(self, headless: bool = True):
        self.headless = headless
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
    
    def scrape_site(self, site_config: dict) -> Generator[Job, None, None]:
        """
        Scrape a JavaScript-heavy career site using Playwright.
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright not installed. Run: pip install playwright && playwright install")
            return
        
        company = site_config['name']
        base_url = site_config['careers_url']
        site_type = site_config.get('type', 'generic')
        search_params = site_config.get('search_params', {})
        
        selectors = self.ATS_SELECTORS.get(site_type, self.ATS_SELECTORS['generic'])
        
        print(f"Scraping {company} with Playwright ({site_type})...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            try:
                # Navigate to the careers page
                self._rate_limit(self._get_domain(base_url))
                page.goto(base_url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for job listings to load
                page.wait_for_timeout(5000)  # Give JS time to render
                
                # Try to fill in keyword search if there's a search box
                if search_params.get('keywords'):
                    keyword_selectors = [
                        'input[type="search"]',
                        'input[placeholder*="search" i]',
                        'input[placeholder*="keyword" i]',
                        'input[name*="search" i]',
                        'input[name*="keyword" i]',
                        'input[id*="search" i]',
                        'input[id*="keyword" i]',
                        '#keywordInput',
                    ]
                    for selector in keyword_selectors:
                        try:
                            search_input = page.locator(selector).first
                            if search_input.is_visible(timeout=2000):
                                search_input.fill(search_params['keywords'])
                                break
                        except:
                            continue
                
                # Try to fill in location search
                if search_params.get('location'):
                    location_selectors = [
                        'input[placeholder*="location" i]',
                        'input[placeholder*="city" i]',
                        'input[placeholder*="where" i]',
                        'input[name*="location" i]',
                        'input[id*="location" i]',
                        'input[aria-label*="location" i]',
                        '#locationInput',
                    ]
                    for selector in location_selectors:
                        try:
                            location_input = page.locator(selector).first
                            if location_input.is_visible(timeout=2000):
                                location_input.fill(search_params['location'])
                                break
                        except:
                            continue
                
                # Submit search (press Enter or click search button)
                try:
                    search_button = page.locator('button[type="submit"], button:has-text("Search"), button[aria-label*="search" i]').first
                    if search_button.is_visible(timeout=1000):
                        search_button.click()
                    else:
                        page.keyboard.press('Enter')
                except:
                    page.keyboard.press('Enter')
                
                page.wait_for_timeout(3000)
                
                # Find job links
                job_links = []
                try:
                    # Get all links and filter for job-related ones
                    all_links = page.locator('a[href]').all()
                    for link in all_links:
                        try:
                            href = link.get_attribute('href')
                            if href:
                                full_url = urljoin(base_url, href)
                                
                                # Skip social media and external links
                                if any(ext in full_url.lower() for ext in [
                                    'facebook.com', 'twitter.com', 'linkedin.com', 
                                    'instagram.com', 'youtube.com'
                                ]):
                                    continue
                                
                                # Match various job URL patterns
                                is_job_link = any(pattern in full_url.lower() for pattern in [
                                    '/job/', '/jobs/', 'jobid=', 'jobdetail', 
                                    'requisition', '/position/', '/opening/',
                                    'folderdetail'  # Avature
                                ])
                                # Exclude search/list pages
                                is_list_page = any(pattern in full_url.lower() for pattern in [
                                    '/search', 'offset=', 'page=', 'results',
                                    'searchjobs', 'login', 'referral', 'applicationmethods'
                                ])
                                if is_job_link and not is_list_page and full_url not in job_links:
                                    job_links.append(full_url)
                                    if len(job_links) >= 30:
                                        break
                        except:
                            continue
                except Exception as e:
                    print(f"  Error finding job links: {e}")
                
                print(f"  Found {len(job_links)} job links")
                
                # Scrape each job page
                for url in job_links[:20]:  # Limit to 20 to be polite
                    job = self._scrape_job_page(page, url, company, selectors)
                    if job:
                        yield job
                        
            except Exception as e:
                print(f"  Error scraping {company}: {e}")
            finally:
                browser.close()
    
    def _scrape_job_page(self, page, url: str, company: str, selectors: dict) -> Job:
        """Extract job details from a job posting page using Playwright."""
        try:
            self._rate_limit(self._get_domain(url))
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(2000)
            
            # Extract title - try each selector individually
            title = None
            title_selectors = selectors['title'].split(', ')
            for sel in title_selectors:
                try:
                    elem = page.locator(sel).first
                    if elem.is_visible(timeout=1000):
                        text = elem.inner_text().strip()
                        if text and len(text) > 3:  # Skip empty or very short
                            title = text
                            break
                except:
                    continue
            
            if not title:
                return None
            
            # Extract location - try each selector individually
            location = ""
            location_selectors = selectors['location'].split(', ')
            for sel in location_selectors:
                try:
                    elem = page.locator(sel).first
                    if elem.is_visible(timeout=1000):
                        text = elem.inner_text().strip()
                        if text:
                            location = text
                            break
                except:
                    continue
            
            # Extract description - try each selector individually
            description = ""
            desc_selectors = selectors['description'].split(', ')
            for sel in desc_selectors:
                try:
                    elem = page.locator(sel).first
                    if elem.is_visible(timeout=1000):
                        text = elem.inner_text()
                        if text and len(text) > 50:  # Need substantial description
                            description = text[:5000]
                            break
                except:
                    continue
            
            print(f"  Scraped: {title[:50]}...")
            
            return Job(
                company=company,
                title=title,
                location=location,
                description=description,
                url=url,
                scraped_at=datetime.now().isoformat(),
            )
            
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            return None


def scrape_all_sites(sites: list[dict] = None, use_playwright: bool = True) -> Generator[Job, None, None]:
    """
    Scrape all configured sites and yield jobs.
    
    Args:
        sites: List of site configurations. Defaults to TARGET_SITES.
        use_playwright: Whether to use Playwright for JS-heavy sites. Defaults to True.
    """
    sites = sites or TARGET_SITES
    generic_scraper = GenericCareerPageScraper()
    playwright_scraper = PlaywrightScraper() if use_playwright and PLAYWRIGHT_AVAILABLE else None
    
    # Site types that need Playwright (JavaScript rendering)
    js_heavy_types = {'workday', 'icims', 'greenhouse', 'lever', 'avature'}
    
    for site in sites:
        site_type = site.get('type', 'custom')
        
        try:
            if site_type in js_heavy_types and playwright_scraper:
                for job in playwright_scraper.scrape_site(site):
                    # Filter by location (DC Metro Area or Remote)
                    if is_location_match(job.location):
                        yield job
                    else:
                        print(f"  Skipped (location): {job.title} - {job.location}")
            else:
                for job in generic_scraper.scrape_site(site):
                    # Filter by location (DC Metro Area or Remote)
                    if is_location_match(job.location):
                        yield job
                    else:
                        print(f"  Skipped (location): {job.title} - {job.location}")
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
