import requests
from bs4 import BeautifulSoup
from config import get_random_headers, REQUEST_TIMEOUT
from utils.helpers import clean_text, contains_keywords, parse_relative_time, format_posted_time
import time

def scrape_linkedin_jobs(keyword, location):
    """Scrape jobs from LinkedIn with time parsing for recent jobs"""
    jobs = []
    
    try:
        # Proper URL encoding
        keyword_encoded = requests.utils.quote(keyword)
        location_encoded = requests.utils.quote(location)
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={keyword_encoded}&location={location_encoded}"
        
        print(f"🔍 Scraping LinkedIn for: {keyword} in {location}")
        
        # Enhanced headers to avoid blocking
        headers = {
            **get_random_headers(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add delay to avoid rate limiting
        time.sleep(2)
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        print(f"📊 LinkedIn status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ LinkedIn returned status: {response.status_code}")
            return jobs
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple selector strategies for LinkedIn's changing structure
        job_cards = soup.find_all('div', class_='base-search-card__info')
        
        if not job_cards:
            job_cards = soup.find_all('li', class_=lambda x: x and 'jobs-search-results__list-item' in str(x))
            
        if not job_cards:
            job_cards = soup.find_all('div', class_='job-search-card')
            
        print(f"📊 LinkedIn found {len(job_cards)} job cards")
        
        for i, card in enumerate(job_cards[:15]):  # Increased limit
            try:
                # Extract title with multiple selectors
                title_elem = (card.find('h3', class_='base-search-card__title') or 
                             card.find('h3', class_='job-card-list__title') or
                             card.find('a', class_='job-card-list__title'))
                
                # Extract company with multiple selectors
                company_elem = (card.find('a', class_='hidden-nested-link') or
                               card.find('h4', class_='base-search-card__subtitle') or
                               card.find('a', class_='job-card-container__link'))
                
                # Extract location with multiple selectors
                location_elem = (card.find('span', class_='job-search-card__location') or
                                card.find('span', class_='job-card-container__metadata-item'))
                
                # Extract posted time - LinkedIn time elements
                time_elem = (card.find('time') or
                            card.find('span', class_='job-search-card__listdate') or
                            card.find('span', class_='job-search-card__listdate--new'))
                
                if title_elem and title_elem.text.strip():
                    title = clean_text(title_elem.text.strip())
                    company = clean_text(company_elem.text.strip()) if company_elem and company_elem.text.strip() else "Not specified"
                    location_text = clean_text(location_elem.text.strip()) if location_elem and location_elem.text.strip() else location
                    
                    # Parse posted time
                    posted_time = None
                    if time_elem and time_elem.text.strip():
                        time_text = clean_text(time_elem.text.strip())
                        # Parse relative time using your helper function
                        parsed_time = parse_relative_time(time_text)
                        if parsed_time:
                            posted_time = format_posted_time(parsed_time)
                        else:
                            posted_time = time_text
                        print(f"⏰ Posted: {posted_time}")
                    
                    # Get link - find in parent elements
                    link = ""
                    link_elem = card.find_previous('a', class_='base-card__full-link')
                    if not link_elem:
                        # Try finding link in parent card
                        parent_card = card.find_parent('div', class_='base-card')
                        if parent_card:
                            link_elem = parent_card.find('a', class_='base-card__full-link')
                    
                    if link_elem:
                        link = link_elem.get('href', '')
                        # Clean LinkedIn tracking parameters
                        if '?' in link:
                            link = link.split('?')[0]
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'link': link,
                        'source': 'LinkedIn',
                        'posted_time': posted_time  # Added time field
                    }
                    
                    # Filter by keywords
                    if contains_keywords(job['title']):
                        jobs.append(job)
                        print(f"✅ Added LinkedIn job {i+1}: {title[:40]}... | Time: {posted_time or 'N/A'}")
                    else:
                        print(f"⏭️ Skipped - no keywords: {title[:40]}...")
                        
            except Exception as e:
                print(f"⚠️ Error parsing LinkedIn job card {i+1}: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error scraping LinkedIn: {e}")
    except Exception as e:
        print(f"❌ Error scraping LinkedIn: {e}")
    
    return jobs


def filter_recent_jobs(jobs, hours=24):
    """Filter jobs posted within the last specified hours"""
    if not jobs:
        return []
    
    recent_jobs = []
    now = time.time()
    
    for job in jobs:
        # If job has posted_time, try to filter by recency
        if job.get('posted_time'):
            # Simple filtering based on time text
            time_text = job['posted_time'].lower()
            
            # Consider jobs as recent if they contain time indicators
            is_recent = any(indicator in time_text for indicator in 
                           ['minute', 'hour', 'today', 'just now', 'now', 'recent'])
            
            # For hours-based filtering
            if 'hour' in time_text:
                try:
                    # Extract hours number from text like "2 hours ago"
                    import re
                    hours_match = re.search(r'(\d+)\s*hour', time_text)
                    if hours_match:
                        job_hours = int(hours_match.group(1))
                        if job_hours <= hours:
                            recent_jobs.append(job)
                            continue
                except:
                    pass
            
            # If we can't parse exact hours but it seems recent, include it
            if is_recent:
                recent_jobs.append(job)
        else:
            # If no time info, include the job (be conservative)
            recent_jobs.append(job)
    
    print(f"📅 Filtered {len(recent_jobs)} recent jobs out of {len(jobs)} total")
    return recent_jobs


# Optional: Enhanced version with recency filtering
def scrape_linkedin_recent_jobs(keyword, location, max_hours_old=24):
    """Scrape LinkedIn jobs and filter for recent postings only"""
    all_jobs = scrape_linkedin_jobs(keyword, location)
    recent_jobs = filter_recent_jobs(all_jobs, max_hours_old)
    
    # Sort by recency (jobs with time info first, then others)
    recent_jobs.sort(key=lambda x: (
        0 if x.get('posted_time') and any(word in x['posted_time'].lower() 
        for word in ['minute', 'hour', 'today']) else 1,
        x.get('posted_time', '')
    ))
    
    return recent_jobs