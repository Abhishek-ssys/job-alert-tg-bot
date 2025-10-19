#!/usr/bin/env python3
"""
Comprehensive test suite for Job Alert Bot
Run this before deploying to Railway
"""
import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Job Bot Tests...")
    print("=" * 60)
    
    test_results = {}
    
    # Import and run individual tests
    try:
        from test_config import test_config
        test_results['config'] = test_config()
    except Exception as e:
        test_results['config'] = f"FAILED: {e}"
    
    try:
        from test_database import test_database
        test_results['database'] = test_database()
    except Exception as e:
        test_results['database'] = f"FAILED: {e}"
    
    try:
        from test_telegram import test_telegram
        test_results['telegram'] = test_telegram()
    except Exception as e:
        test_results['telegram'] = f"FAILED: {e}"
    
    try:
        from test_scraper import test_scrapers
        test_results['scrapers'] = test_scrapers()
    except Exception as e:
        test_results['scrapers'] = f"FAILED: {e}"
    
    try:
        from test_helpers import test_helpers
        test_results['helpers'] = test_helpers()
    except Exception as e:
        test_results['helpers'] = f"FAILED: {e}"
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASS" if result == "PASS" else "❌ FAIL"
        print(f"{test_name.upper():<15} {status}")
        if result != "PASS":
            all_passed = False
            print(f"   Error: {result}")
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Ready for deployment!")
        return True
    else:
        print("❌ SOME TESTS FAILED! Please fix before deployment.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)