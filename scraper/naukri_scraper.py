from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_random_headers
from utils.helpers import clean_text, contains_keywords

def scrape_naukri_jobs(keyword, location):
    """Scrape Naukri using Selenium in headless mode"""
    jobs = []
    driver = None
    
    try:
        print(f"🔍 Scraping Naukri for: {keyword} in {location}")
        
        # Setup Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument(f"user-agent={get_random_headers()['User-Agent']}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # HEADLESS MODE - No browser window will open
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = f"https://www.naukri.com/{keyword}-jobs-in-{location}?k={keyword}&l={location}"
        print(f"🌐 Opening URL: {url}")
        
        driver.get(url)
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(8)
        
        # Check if we got redirected or blocked
        if "captcha" in driver.current_url or "blocked" in driver.page_source.lower():
            print("❌ Page blocked or CAPTCHA detected!")
            return jobs
        
        # Try multiple selectors for job cards
        selectors = [
            "article.jobTuple",
            ".srp-jobtuple-wrapper", 
            "div[class*='jobTuple']"
        ]
        
        job_cards = []
        for selector in selectors:
            try:
                found = driver.find_elements(By.CSS_SELECTOR, selector)
                if found:
                    job_cards = found
                    print(f"✅ Found {len(job_cards)} job cards")
                    break
            except:
                continue
        
        for i, card in enumerate(job_cards[:15]):
            try:
                # Extract job data
                title_elem = card.find_elements(By.CSS_SELECTOR, "a.title, .title a")
                company_elem = card.find_elements(By.CSS_SELECTOR, "a.comp-name, .comp-name")
                location_elem = card.find_elements(By.CSS_SELECTOR, "li.location, .loc")
                
                if title_elem and title_elem[0].text.strip():
                    title = clean_text(title_elem[0].text.strip())
                    company = clean_text(company_elem[0].text.strip()) if company_elem else "Not specified"
                    location_text = clean_text(location_elem[0].text.strip()) if location_elem else location
                    
                    # Get link
                    link = title_elem[0].get_attribute('href')
                    
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
                print(f"⚠️ Error parsing job card {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error scraping Naukri: {e}")
        
    finally:
        if driver:
            driver.quit()
    
    return jobs

def scrape_naukri_recent_jobs(keyword, location, max_hours_old=24):
    """Wrapper for recent jobs filtering"""
    return scrape_naukri_jobs(keyword, location)