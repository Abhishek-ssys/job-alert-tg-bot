#!/usr/bin/env python3
"""Test helper functions"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_helpers():
    """Test utility helper functions"""
    print("\n🛠️ Testing Helper Functions...")
    
    try:
        from utils.helpers import (
            contains_keywords, clean_text, format_job_text,
            parse_relative_time, format_posted_time, log_message
        )
        from config import KEYWORDS
        
        # Test 1: contains_keywords
        test_cases = [
            ("Python Developer needed", True),
            ("Java Backend Engineer", True),
            ("Marketing Manager", False),
            ("Senior Software Engineer Python", True)
        ]
        
        for text, expected in test_cases:
            result = contains_keywords(text)
            assert result == expected, f"Keyword check failed for: {text}"
        print("✅ Keyword matching working")
        
        # Test 2: clean_text
        dirty_text = "  Hello   World  \n\n  "
        cleaned = clean_text(dirty_text)
        assert cleaned == "Hello World", f"Clean text failed: '{cleaned}'"
        print("✅ Text cleaning working")
        
        # Test 3: format_job_text
        test_job = {
            'title': 'Python Dev',
            'company': 'Tech Co',
            'location': 'Remote',
            'link': 'https://example.com',
            'source': 'Test',
            'posted_time': '1 hour ago'
        }
        formatted = format_job_text(test_job)
        assert 'Python Dev' in formatted
        assert 'Tech Co' in formatted
        assert 'Remote' in formatted
        print("✅ Job formatting working")
        
        # Test 4: time parsing
        time_cases = [
            ("2 hours ago", "hours"),
            ("1 day ago", "days"),
            ("3 weeks ago", "weeks")
        ]
        
        for time_text, expected in time_cases:
            parsed = parse_relative_time(time_text)
            assert parsed is not None, f"Time parsing failed for: {time_text}"
            formatted_time = format_posted_time(parsed)
            assert formatted_time, f"Time formatting failed for: {time_text}"
        print("✅ Time parsing working")
        
        # Test 5: logging
        log_message("Test log message")
        print("✅ Logging working")
        
        print("✅ Helpers test passed")
        return "PASS"
        
    except Exception as e:
        print(f"❌ Helpers test failed: {e}")
        return f"Helpers error: {e}"