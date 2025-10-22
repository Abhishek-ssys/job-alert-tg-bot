import requests
from bs4 import BeautifulSoup
from config import get_random_headers, REQUEST_TIMEOUT
from utils.helpers import clean_text, contains_keywords
import time

def scrape_naukri_fallback(keyword, location):
    """Fallback Naukri scraper using requests only"""
    jobs = []
    
    try:
        print(f"🔍 Scraping Naukri (Fallback) for: {keyword} in {location}")
        
        url = f"https://www.naukri.com/{keyword}-jobs-in-{location}"
        
        headers = {
            **get_random_headers(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            print(f"❌ Naukri returned status: {response.status_code}")
            return jobs
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for Naukri job cards
        selectors = [
            'article.jobTuple',
            '.srp-jobtuple-wrapper',
            'div[class*="jobTuple"]',
            '.list',
            'div[data-job-id]'
        ]
        
        job_cards = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                job_cards = found
                break
        
        print(f"📊 Naukri fallback found {len(job_cards)} job cards")
        
        for card in job_cards[:10]:
            try:
                # Extract title
                title_elem = card.select_one('a.title, .title a, a[class*="title"]')
                if not title_elem or not title_elem.text.strip():
                    continue
                
                title = clean_text(title_elem.text.strip())
                
                # Extract company
                company_elem = card.select_one('a.comp-name, .comp-name, [class*="company"]')
                company = clean_text(company_elem.text.strip()) if company_elem else "Not specified"
                
                # Extract location
                location_elem = card.select_one('.loc, .location, [class*="loc"]')
                location_text = clean_text(location_elem.text.strip()) if location_elem else location
                
                # Get link
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = "https://www.naukri.com" + link
                
                job = {
                    'title': title,
                    'company': company,
                    'location': location_text,
                    'link': link,
                    'source': 'Naukri',
                    'posted_time': 'Recently'
                }
                
                if contains_keywords(job['title']):
                    jobs.append(job)
                    print(f"✅ Added Naukri job: {title[:40]}...")
                    
            except Exception as e:
                print(f"⚠️ Error parsing Naukri job: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error in Naukri fallback: {e}")
    
    return jobs