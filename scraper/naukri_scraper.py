import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from config import get_random_headers, REQUEST_TIMEOUT
from utils.helpers import clean_text, contains_keywords

def setup_driver():
    """Setup Chrome driver that works on Railway"""
    chrome_options = Options()
    
    # Essential options for Railway
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Use webdriver-manager to handle ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Stealth settings
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scrape_naukri_jobs(keyword, location):
    """Scrape jobs from Naukri.com - Railway optimized version"""
    jobs = []
    driver = None
    
    try:
        print(f"🔍 Scraping Naukri for: {keyword} in {location}")
        
        # Setup driver
        driver = setup_driver()
        
        # Build URL
        url = f"https://www.naukri.com/{keyword}-jobs-in-{location}?k={keyword}&l={location}"
        print(f"🌐 Opening: {url}")
        
        driver.get(url)
        time.sleep(5)  # Wait for page load
        
        # Find job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, "article.jobTuple, div[class*='jobTuple'], .srp-jobtuple-wrapper")
        
        if not job_cards:
            # Try alternative selectors
            job_cards = driver.find_elements(By.CSS_SELECTOR, "article, div[class*='job'], div[class*='tuple']")
        
        print(f"📊 Found {len(job_cards)} job cards")
        
        for i, card in enumerate(job_cards[:15]):
            try:
                # Extract job data
                title_elem = card.find_elements(By.CSS_SELECTOR, "a.title, .title a, h2, h3")
                company_elem = card.find_elements(By.CSS_SELECTOR, "a.comp-name, .comp-name, [class*='company']")
                location_elem = card.find_elements(By.CSS_SELECTOR, ".loc, .location, [class*='loc']")
                
                if title_elem and title_elem[0].text.strip():
                    title = clean_text(title_elem[0].text.strip())
                    company = clean_text(company_elem[0].text.strip()) if company_elem else "Not specified"
                    location_text = clean_text(location_elem[0].text.strip()) if location_elem else location
                    
                    # Get link
                    link = ""
                    if title_elem[0].get_attribute('href'):
                        link = title_elem[0].get_attribute('href')
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
                        print(f"✅ Added: {title[:40]}...")
                        
            except Exception as e:
                print(f"⚠️ Error parsing card {i+1}: {e}")
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