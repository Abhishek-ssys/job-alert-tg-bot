#!/usr/bin/env python3
"""
Quick test for deployment - minimal tests
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Quick test for deployment verification"""
    print("🚀 Quick Deployment Test")
    print("=" * 40)
    
    tests = []
    
    # Test 1: Config
    try:
        from config import TOKEN, CHAT_ID
        tests.append(("Config", "✅"))
    except Exception as e:
        tests.append(("Config", f"❌ {e}"))
    
    # Test 2: Database
    try:
        from db.database import create_table
        create_table()
        tests.append(("Database", "✅"))
    except Exception as e:
        tests.append(("Database", f"❌ {e}"))
    
    # Test 3: Telegram (basic)
    try:
        from tg.bot import send_message
        tests.append(("Telegram Import", "✅"))
    except Exception as e:
        tests.append(("Telegram Import", f"❌ {e}"))
    
    # Test 4: Scrapers (import only)
    try:
        from scraper.naukri_scraper import scrape_naukri_jobs
        from scraper.linkedin_scraper import scrape_linkedin_jobs
        tests.append(("Scrapers Import", "✅"))
    except Exception as e:
        tests.append(("Scrapers Import", f"❌ {e}"))
    
    # Print results
    print("\n📊 Quick Test Results:")
    for test_name, result in tests:
        print(f"{test_name:<20} {result}")
    
    # Check if all passed
    all_passed = all("✅" in result for _, result in tests)
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 QUICK TEST PASSED - Ready for deployment!")
        return True
    else:
        print("❌ QUICK TEST FAILED - Check errors above")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)