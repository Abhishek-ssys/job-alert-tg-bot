import os
import random

# Telegram Configuration - Use environment variables for security
TOKEN = os.getenv("TELEGRAM_TOKEN", "8244499994:AAGRaqveIT7cbRda-6Dw_oL0JCnr0VYgz5Q")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "689236330")

# Job Search Configuration - Optimized for Abhishek Sorgile's Resume
KEYWORDS = [
    "java developer", "backend developer", "software engineer", 
    "java spring boot", "spring boot developer", "microservices developer",
    "apigee developer", "api developer", "api gateway", "api management",
    "apigee api", "api proxy", "oauth2", "jwt", "api security",
    "fullstack developer", "rest api", "java microservices", 
    "api integration", "backend engineer",
    "api security", "encryption", "security developer", "oauth developer",
    "junior java", "fresher", "entry level", "trainee", "intern",
    "associate developer", "graduate engineer"
]

LOCATION = "remote"

# Enhanced Headers for scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
]

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

# Scraping Configuration
REQUEST_TIMEOUT = 30  # Increased for Railway
DELAY_BETWEEN_REQUESTS = 3

# Database Configuration
DB_PATH = "jobs.db"

# Scheduling Configuration (in minutes)
SCRAPING_INTERVAL = int(os.getenv("SCRAPING_INTERVAL", "30"))