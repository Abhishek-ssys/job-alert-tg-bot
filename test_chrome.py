#!/usr/bin/env python3
"""Test Chrome and ChromeDriver setup"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_chrome():
    print("🧪 Testing Chrome setup...")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        print(f"✅ Chrome test passed! Title: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Chrome test failed: {e}")
        return False

if __name__ == "__main__":
    test_chrome()