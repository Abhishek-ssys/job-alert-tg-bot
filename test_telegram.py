#!/usr/bin/env python3
"""Test Telegram bot functionality"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_telegram():
    """Test Telegram bot"""
    print("\n🤖 Testing Telegram Bot...")
    
    try:
        from tg.bot import send_message, send_job_alert
        
        # Test 1: Send simple message
        print("📤 Testing simple message...")
        test_msg = "🧪 Test Message from Job Bot\nTime: " + str(__import__('datetime').datetime.now())
        success1 = send_message(test_msg)
        
        if success1:
            print("✅ Simple message sent successfully")
        else:
            print("⚠️ Simple message failed (might be network/token issue)")
        
        # Test 2: Send job alert
        print("📤 Testing job alert...")
        test_job = {
            'title': 'TEST: Senior Python Developer',
            'company': 'TestTech Solutions',
            'location': 'Remote',
            'link': 'https://example.com/jobs/123',
            'source': 'Test Suite',
            'posted_time': 'Just now'
        }
        
        success2 = send_job_alert(test_job)
        
        if success2:
            print("✅ Job alert sent successfully")
        else:
            print("⚠️ Job alert failed (might be network/token issue)")
        
        # If both failed, it's likely a configuration issue
        if not success1 and not success2:
            return "Telegram messages failed - check TOKEN and CHAT_ID"
        
        print("✅ Telegram test completed")
        return "PASS"
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return f"Telegram error: {e}"