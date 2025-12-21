#!/usr/bin/env python3
"""
Test script for Google job search via ScraperAPI.
This validates the GoogleJobScraper implementation.
"""

import os
import sys

# Test imports
print("Testing imports...")
try:
    from config import GOOGLE_SEARCH_CONFIG
    print("✓ Config imported successfully")
    print(f"  - Keywords: {len(GOOGLE_SEARCH_CONFIG['keywords'])}")
    print(f"  - Target locations: {len(GOOGLE_SEARCH_CONFIG.get('locations', []))}")
    print(f"  - Date range: {GOOGLE_SEARCH_CONFIG.get('date_range')}")
except ImportError as e:
    print(f"✗ Failed to import config: {e}")
    sys.exit(1)

try:
    from scraper import GoogleJobScraper, is_location_match
    print("✓ Scraper imported successfully")
except ImportError as e:
    print(f"✗ Failed to import scraper: {e}")
    sys.exit(1)

try:
    from storage import Job
    print("✓ Storage imported successfully")
except ImportError as e:
    print(f"✗ Failed to import storage: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Configuration Validation")
print("=" * 60)

# Validate configuration
required_keys = ['keywords', 'locations', 'primary_location', 'date_range', 
                 'included_sites', 'experience_levels', 'results_per_search']

for key in required_keys:
    if key in GOOGLE_SEARCH_CONFIG:
        value = GOOGLE_SEARCH_CONFIG[key]
        if isinstance(value, list):
            print(f"✓ {key}: {len(value)} items")
        else:
            print(f"✓ {key}: {value}")
    else:
        print(f"✗ {key}: MISSING")

print("\n" + "=" * 60)
print("API Key Check")
print("=" * 60)

# Check for API key
api_key = os.environ.get('SCRAPERAPI_KEY')
if api_key and api_key != 'your_key_here':
    print(f"✓ SCRAPERAPI_KEY is set (starts with: {api_key[:10]}...)")
    
    print("\n" + "=" * 60)
    print("Testing GoogleJobScraper Initialization")
    print("=" * 60)
    
    try:
        scraper = GoogleJobScraper()
        print("✓ GoogleJobScraper initialized successfully")
        print(f"  - Client type: {type(scraper.client)}")
        print(f"  - Seen URLs tracker: {type(scraper.seen_urls)}")
    except Exception as e:
        print(f"✗ Failed to initialize scraper: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Test Complete - Ready for Live Search")
    print("=" * 60)
    print("\nTo run a live search:")
    print("  python main.py scrape")
    
else:
    print("✗ SCRAPERAPI_KEY not set or is placeholder")
    print("\n" + "=" * 60)
    print("Setup Instructions")
    print("=" * 60)
    print("\n1. Sign up at: https://www.scraperapi.com/")
    print("2. Get your API key from the dashboard")
    print("3. Add to your shell profile (~/.zshrc or ~/.bash_profile):")
    print("   export SCRAPERAPI_KEY='your_actual_key_here'")
    print("4. Restart your terminal")
    print("5. Run this test again")
    print("\n" + "=" * 60)
    print("Skipping live API tests")
    print("=" * 60)

print("\n" + "=" * 60)
print("Testing Location Filter")
print("=" * 60)

# Test location matching
test_locations = [
    ("Washington, DC", True),
    ("Remote", True),
    ("Arlington, VA", True),
    ("Bethesda, MD", True),
    ("San Francisco, CA", False),
    ("New York, NY", False),
    ("Work from home", True),
    ("Columbia, MD", True),
]

for location, expected in test_locations:
    result = is_location_match(location)
    status = "✓" if result == expected else "✗"
    print(f"{status} {location}: {result} (expected {expected})")

print("\n" + "=" * 60)
print("All Tests Complete!")
print("=" * 60)

