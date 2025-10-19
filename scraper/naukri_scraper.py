from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import re
from datetime import datetime, timedelta
from utils.helpers import clean_text, contains_keywords

def parse_naukri_time(time_text):
    """Parse Naukri-specific time formats"""
    if not time_text:
        return None
    
    time_text = time_text.lower().strip()
    now = datetime.now()
    
    # Naukri time patterns
    patterns = {
        r'just now|just posted|today': now,
        r'(\d+)\s*days?\s*ago': lambda x: now - timedelta(days=int(x)),
        r'(\d+)\s*hours?\s*ago': lambda x: now - timedelta(hours=int(x)),
        r'(\d+)\s*weeks?\s*ago': lambda x: now - timedelta(weeks=int(x)),
        r'(\d+)\s*months?\s*ago': lambda x: now - timedelta(days=int(x)*30),
    }
    
    for pattern, time_func in patterns.items():
        match = re.search(pattern, time_text)
        if match:
            if callable(time_func):
                return time_func(match.group(1))
            else:
                return time_func
    
    return None

def format_naukri_posted_time(posted_date):
    """Format the posted time for Naukri"""
    if not posted_date:
        return "Recently"
    
    if isinstance(posted_date, str):
        return posted_date
    
    now = datetime.now()
    time_diff = now - posted_date
    
    if time_diff.days == 0:
        if time_diff.seconds < 60:  # Less than 1 minute
            return "Just now"
        elif time_diff.seconds < 3600:  # Less than 1 hour
            minutes = time_diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            hours = time_diff.seconds // 3600
            return f"{hours} hours ago"
    elif time_diff.days == 1:
        return "1 day ago"
    elif time_diff.days < 7:
        return f"{time_diff.days} days ago"
    elif time_diff.days < 30:
        weeks = time_diff.days // 7
        return f"{weeks} weeks ago"
    else:
        return posted_date.strftime("%b %d, %Y")

def scrape_naukri_jobs(keyword, location):
    """Scrape jobs from Naukri.com using Selenium with time parsing"""
    jobs = []
    
    try:
        print(f"🔍 Scraping Naukri for: {keyword} in {location}")
        
        # Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Headless mode
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = f"https://www.naukri.com/{keyword}-jobs-in-{location}?k={keyword}&l={location}"
        print(f"🌐 Opening URL: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Scroll to load more jobs
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Find job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, "article.jobTuple, div.srp-jobtuple-wrapper, div[class*='jobTuple']")
        
        if not job_cards:
            # Try alternative selectors
            job_cards = driver.find_elements(By.CSS_SELECTOR, "article, div[class*='job'], div[class*='tuple']")
        
        print(f"📊 Naukri found {len(job_cards)} job cards")
        
        for i, card in enumerate(job_cards[:20]):  # Increased limit to see more
            try:
                print(f"\n--- Processing job card {i+1} ---")
                
                # Extract title
                title_elem = None
                title_selectors = [
                    "a.title",
                    ".title a",
                    "a[class*='title']",
                    "h2",
                    "h3",
                    "a.jobTitle"
                ]
                
                for selector in title_selectors:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, selector)
                        if title_elem and title_elem.text.strip():
                            break
                    except:
                        continue
                
                if not title_elem:
                    print("❌ Could not extract title")
                    continue
                
                title = clean_text(title_elem.text.strip())
                print(f"✅ Title: {title}")
                
                # Extract company
                company_elem = None
                company_selectors = [
                    "a.comp-name",
                    ".comp-name",
                    "a[class*='comp']",
                    ".companyInfo",
                    "[class*='company']"
                ]
                
                for selector in company_selectors:
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, selector)
                        if company_elem and company_elem.text.strip():
                            break
                    except:
                        continue
                
                company = clean_text(company_elem.text.strip()) if company_elem else "Not specified"
                print(f"✅ Company: {company}")
                
                # Extract location
                location_elem = None
                location_selectors = [
                    ".loc",
                    ".location",
                    "li[class*='location']",
                    "[class*='loc']",
                    ".locWdth"
                ]
                
                for selector in location_selectors:
                    try:
                        location_elem = card.find_element(By.CSS_SELECTOR, selector)
                        if location_elem and location_elem.text.strip():
                            break
                    except:
                        continue
                
                location_text = clean_text(location_elem.text.strip()) if location_elem else location
                print(f"✅ Location: {location_text}")
                
                # Extract posted time - Naukri specific selectors
                posted_time_elem = None
                time_selectors = [
                    ".job-post-day",
                    ".fleft.postedDate",
                    "span[class*='date']",
                    "span[class*='time']",
                    ".postedDate",
                    ".type.br2.seeMore"
                ]
                
                posted_time_text = None
                posted_datetime = None
                for selector in time_selectors:
                    try:
                        posted_time_elem = card.find_element(By.CSS_SELECTOR, selector)
                        if posted_time_elem and posted_time_elem.text.strip():
                            posted_time_text = clean_text(posted_time_elem.text.strip())
                            # Parse Naukri time format
                            posted_datetime = parse_naukri_time(posted_time_text)
                            if posted_datetime:
                                formatted_time = format_naukri_posted_time(posted_datetime)
                                print(f"✅ Posted: {posted_time_text} → {formatted_time}")
                            else:
                                print(f"⏰ Posted: {posted_time_text} (could not parse)")
                            break
                    except:
                        continue
                
                if not posted_time_text:
                    print("⏰ No posting time found")
                
                # Get link
                link = ""
                link_selectors = [
                    "a.title",
                    "a[class*='title']",
                    "a.jobTitle",
                    "a[href*='naukri.com']"
                ]
                
                for selector in link_selectors:
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, selector)
                        if link_elem:
                            link = link_elem.get_attribute('href')
                            if link:
                                # Clean the link
                                if '? ' in link:
                                    link = link.split('? ')[0]
                                print(f"✅ Link: {link[:80]}...")
                                break
                    except:
                        continue
                
                # Create job object with posted_time
                job = {
                    'title': title,
                    'company': company,
                    'location': location_text,
                    'link': link,
                    'source': 'Naukri',
                    'posted_time': format_naukri_posted_time(posted_datetime) if posted_datetime else posted_time_text,
                    '_parsed_time': posted_datetime  # Internal use for filtering
                }
                
                # Filter by keywords
                if contains_keywords(job['title']):
                    jobs.append(job)
                    print(f"🎯 ADDED Naukri job: {title[:50]}...")
                else:
                    print(f"⏭️ Skipped - no keywords: {title[:50]}...")
                        
            except Exception as e:
                print(f"⚠️ Error parsing Naukri job card {i+1}: {e}")
                continue
        
        driver.quit()
        print(f"🎯 Total Naukri jobs added: {len(jobs)}")
                
    except Exception as e:
        print(f"❌ Error scraping Naukri: {e}")
        try:
            driver.quit()
        except:
            pass
    
    return jobs


def filter_naukri_recent_jobs(jobs, max_hours_old=24):
    """Filter Naukri jobs by recency - STRICT filtering"""
    if not jobs:
        return []
    
    recent_jobs = []
    now = datetime.now()
    
    for job in jobs:
        parsed_time = job.get('_parsed_time')
        
        if parsed_time:
            # Calculate hours difference
            time_diff = now - parsed_time
            hours_diff = time_diff.total_seconds() / 3600
            
            if hours_diff <= max_hours_old:
                recent_jobs.append(job)
                print(f"📅 INCLUDED recent job: {job['title'][:40]}... ({hours_diff:.1f} hours ago)")
            else:
                print(f"📅 EXCLUDED old job: {job['title'][:40]}... ({hours_diff:.1f} hours ago)")
        else:
            # If we can't parse time, exclude it to be safe
            print(f"📅 EXCLUDED job (no time): {job['title'][:40]}...")
    
    print(f"📅 STRICT FILTERING: {len(recent_jobs)} recent jobs out of {len(jobs)} total (within {max_hours_old} hours)")
    return recent_jobs


def scrape_naukri_recent_jobs(keyword, location, max_hours_old=24):
    """Scrape Naukri jobs and STRICTLY filter for recent postings only"""
    all_jobs = scrape_naukri_jobs(keyword, location)
    recent_jobs = filter_naukri_recent_jobs(all_jobs, max_hours_old)
    
    # Sort by most recent first
    recent_jobs.sort(key=lambda x: x.get('_parsed_time', datetime.min), reverse=True)
    
    # Remove internal field before returning
    for job in recent_jobs:
        job.pop('_parsed_time', None)
    
    return recent_jobs