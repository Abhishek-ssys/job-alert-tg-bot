#!/usr/bin/env python3
"""Test web scrapers"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_scrapers():
    """Test scraping functionality"""
    print("\n🌐 Testing Scrapers...")
    
    try:
        from scraper.naukri_scraper import scrape_naukri_jobs, scrape_naukri_recent_jobs
        from scraper.linkedin_scraper import scrape_linkedin_jobs, scrape_linkedin_recent_jobs
        from config import LOCATION
        
        test_keyword = "python"
        
        # Test 1: Basic Naukri scraping
        print("🔍 Testing Naukri scraper...")
        naukri_jobs = scrape_naukri_jobs(test_keyword, LOCATION)
        assert isinstance(naukri_jobs, list), "Naukri jobs should return a list"
        print(f"✅ Naukri found {len(naukri_jobs)} jobs")
        
        # Test 2: Naukri recent jobs
        naukri_recent = scrape_naukri_recent_jobs(test_keyword, LOCATION, max_hours_old=24)
        assert isinstance(naukri_recent, list), "Naukri recent jobs should return a list"
        print(f"✅ Naukri recent found {len(naukri_recent)} jobs")
        
        # Test 3: Basic LinkedIn scraping
        print("🔍 Testing LinkedIn scraper...")
        linkedin_jobs = scrape_linkedin_jobs(test_keyword, LOCATION)
        assert isinstance(linkedin_jobs, list), "LinkedIn jobs should return a list"
        print(f"✅ LinkedIn found {len(linkedin_jobs)} jobs")
        
        # Test 4: LinkedIn recent jobs
        linkedin_recent = scrape_linkedin_recent_jobs(test_keyword, LOCATION, max_hours_old=24)
        assert isinstance(linkedin_recent, list), "LinkedIn recent jobs should return a list"
        print(f"✅ LinkedIn recent found {len(linkedin_recent)} jobs")
        
        # Verify job structure for any found jobs
        all_jobs = naukri_jobs + linkedin_jobs
        if all_jobs:
            sample_job = all_jobs[0]
            required_fields = ['title', 'company', 'location', 'link', 'source']
            for field in required_fields:
                assert field in sample_job, f"Job missing required field: {field}"
            print("✅ Job structure validation passed")
        
        print("✅ Scrapers test passed")
        return "PASS"
        
    except Exception as e:
        print(f"❌ Scrapers test failed: {e}")
        return f"Scrapers error: {e}"