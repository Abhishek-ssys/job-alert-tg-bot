#!/usr/bin/env python3
"""
Railway setup file - runs before main.py to ensure Selenium works
"""
import os
import sys

def check_selenium_setup():
    """Check if Selenium dependencies are available"""
    print("🔧 Checking Selenium setup on Railway...")
    
    # Check if Chrome/Chromium is available
    try:
        import subprocess
        result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Chromium found:", result.stdout.strip())
        else:
            print("❌ Chromium not found in PATH")
            
        # Check chromedriver
        result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ChromeDriver found:", result.stdout.strip())
        else:
            print("❌ ChromeDriver not found in PATH")
            
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
    
    # Test Selenium import
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium imports working")
        
        # Test basic driver setup
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ Selenium Chrome driver working")
        
    except Exception as e:
        print(f"❌ Selenium setup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_selenium_setup()
    if success:
        print("🚀 Selenium setup successful! Starting main application...")
        # Import and run main
        from main import main
        main()
    else:
        print("❌ Selenium setup failed!")
        sys.exit(1)