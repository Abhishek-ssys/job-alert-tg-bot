#!/usr/bin/env python3
"""Test configuration settings"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test config module"""
    print("\n🔧 Testing Configuration...")
    
    try:
        from config import (
            TOKEN, CHAT_ID, KEYWORDS, LOCATION, 
            get_random_headers, REQUEST_TIMEOUT, 
            SCRAPING_INTERVAL, DB_PATH
        )
        
        # Test required variables exist
        assert TOKEN, "TELEGRAM_TOKEN is missing"
        assert CHAT_ID, "TELEGRAM_CHAT_ID is missing"
        assert KEYWORDS, "KEYWORDS is missing"
        assert LOCATION, "LOCATION is missing"
        
        # Test types
        assert isinstance(KEYWORDS, list), "KEYWORDS should be a list"
        assert isinstance(LOCATION, str), "LOCATION should be a string"
        assert isinstance(REQUEST_TIMEOUT, int), "REQUEST_TIMEOUT should be integer"
        assert isinstance(SCRAPING_INTERVAL, int), "SCRAPING_INTERVAL should be integer"
        
        # Test function calls
        headers = get_random_headers()
        assert 'User-Agent' in headers, "Headers should contain User-Agent"
        assert 'Accept' in headers, "Headers should contain Accept"
        
        print("✅ Config test passed")
        return "PASS"
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return f"Config error: {e}"