"""
Web scraper for job postings using Google Search via ScraperAPI.
Finds jobs across the entire internet with configurable search parameters.
"""

import time
import os
from datetime import datetime
from urllib.parse import urlencode, urlparse
from typing import Generator

from bs4 import BeautifulSoup

try:
    from scraperapi_sdk import ScraperAPIClient
    SCRAPERAPI_AVAILABLE = True
except ImportError:
    SCRAPERAPI_AVAILABLE = False

from config import GOOGLE_SEARCH_CONFIG
from storage import Job


def is_location_match(job_location: str) -> bool:
    """Check if a job location matches our target DC Metro Area or Remote locations."""
    if not job_location:
        return True
    
    location_lower = job_location.lower()
    
    remote_keywords = ['remote', 'telework', 'work from home', 'wfh', 'anywhere']
    if any(keyword in location_lower for keyword in remote_keywords):
        return True
    
    dc_metro_keywords = [
        'washington', 'dc', 'd.c.', 'virginia', ' va', ',va', 'arlington', 'alexandria', 
        'fairfax', 'reston', 'mclean', 'tysons', 'chantilly', 'herndon', 'vienna',
        'sterling', 'manassas', 'falls church', 'maryland', ' md', ',md', 'bethesda', 
        'rockville', 'silver spring', 'gaithersburg', 'germantown', 'college park', 
        'bowie', 'greenbelt', 'largo', 'fort washington', 'suitland', 'annapolis', 
        'fort meade', 'glen burnie', 'severn', 'columbia', 'ellicott city', 'laurel',
    ]
    if any(keyword in location_lower for keyword in dc_metro_keywords):
        return True
    
    return False


class GoogleJobScraper:
    """Scraper that uses Google Search via ScraperAPI to find jobs across the internet."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('SCRAPERAPI_KEY')
        
        if not self.api_key:
            raise ValueError("SCRAPERAPI_KEY not found in environment variables")
        
        if not SCRAPERAPI_AVAILABLE:
            raise ImportError("scraperapi-sdk not installed. Run: pip install scraperapi-sdk")
        
        self.client = ScraperAPIClient(self.api_key)
        self.seen_urls = set()
    
    def _build_google_search_url(self, query: str, date_range: str = None, num_results: int = 100) -> str:
        """Build a Google search URL with parameters."""
        params = {
            'q': query,
            'num': min(num_results, 100),
        }
        
        if date_range:
            date_filters = {'past_24h': 'qdr:d', 'past_week': 'qdr:w', 'past_month': 'qdr:m', 'any_time': ''}
            if date_range in date_filters and date_filters[date_range]:
                params['tbs'] = date_filters[date_range]
        
        return f"https://www.google.com/search?{urlencode(params)}"
    
    def _parse_google_results(self, html: str) -> list:
        """Parse Google search results HTML to extract job links."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for div in soup.find_all('div', class_='g'):
            try:
                link_elem = div.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue
                
                url = link_elem['href']
                if 'google.com' in url or url.startswith('/search'):
                    continue
                
                title_elem = div.find('h3')
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                if url and title:
                    results.append({'url': url, 'title': title})
            except:
                continue
        
        return results
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from job URL."""
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '').replace('jobs.', '').replace('careers.', '')
        parts = domain.split('.')
        return parts[0].title() if len(parts) >= 2 else domain
    
    def _scrape_job_details(self, url: str) -> dict:
        """Scrape full job details from a job posting URL."""
        try:
            html = self.client.get(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            title = None
            for sel in ['h1', 'h2', '.job-title', '.jobtitle']:
                elem = soup.select_one(sel)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and 3 < len(text) < 200:
                        title = text
                        break
            
            location = ""
            for sel in ['.location', '.job-location']:
                elem = soup.select_one(sel)
                if elem:
                    location = elem.get_text(strip=True)
                    break
            
            description = ""
            for sel in ['.job-description', '.description', 'article', 'main']:
                elem = soup.select_one(sel)
                if elem:
                    text = elem.get_text(separator=' ', strip=True)
                    if text and len(text) > 100:
                        description = text[:5000]
                        break
            
            return {'title': title, 'location': location, 'description': description}
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            return None
    
    def _build_search_query(self, keyword: str, location: str = None, exp_level: str = None, sites: list = None) -> str:
        """Build a Google search query string."""
        parts = [keyword]
        if location:
            parts.append(location)
        if exp_level:
            parts.append(exp_level)
        if sites:
            site_query = " OR ".join([f"site:{site}" for site in sites[:3]])
            parts.append(f"({site_query})")
        return " ".join(parts)
    
    def search_all(self) -> Generator[Job, None, None]:
        """Execute Google searches based on GOOGLE_SEARCH_CONFIG and yield jobs."""
        config = GOOGLE_SEARCH_CONFIG
        
        print(f"Starting Google job search via ScraperAPI...")
        print(f"Keywords: {len(config['keywords'])}")
        print("=" * 60)
        
        total_found = 0
        
        for keyword in config['keywords']:
            for exp_level in config.get('experience_levels', ['']):
                query = self._build_search_query(
                    keyword=keyword,
                    location=config.get('primary_location', ''),
                    exp_level=exp_level,
                    sites=config.get('included_sites', [])
                )
                
                print(f"\nSearching: {query}")
                
                try:
                    search_url = self._build_google_search_url(
                        query=query,
                        date_range=config.get('date_range', 'past_week'),
                        num_results=config.get('results_per_search', 100)
                    )
                    
                    html = self.client.get(search_url)
                    results = self._parse_google_results(html)
                    
                    print(f"  Found {len(results)} search results")
                    
                    for result in results:
                        url = result['url']
                        
                        if url in self.seen_urls:
                            continue
                        
                        self.seen_urls.add(url)
                        
                        job_details = self._scrape_job_details(url)
                        
                        if not job_details or not job_details.get('title'):
                            continue
                        
                        company = self._extract_company_from_url(url)
                        
                        job = Job(
                            company=company,
                            title=job_details['title'],
                            location=job_details.get('location', ''),
                            description=job_details.get('description', ''),
                            url=url,
                            scraped_at=datetime.now().isoformat(),
                        )
                        
                        if is_location_match(job.location):
                            total_found += 1
                            print(f"  ✓ {job.title} @ {company}")
                            yield job
                        else:
                            print(f"  ✗ Skipped (location): {job.title} - {job.location}")
                        
                        time.sleep(1)
                        
                        if total_found >= 500:
                            print(f"\n✓ Reached maximum of 500 jobs")
                            return
                
                except Exception as e:
                    print(f"  Error searching '{query}': {e}")
                    continue
                
                time.sleep(2)
        
        print(f"\n{'=' * 60}")
        print(f"Total jobs found: {total_found}")
