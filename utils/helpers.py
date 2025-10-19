import re
from datetime import datetime, timedelta
from config import KEYWORDS

def contains_keywords(text, keywords=None):
    """Check if text contains any of the keywords"""
    if keywords is None:
        keywords = KEYWORDS
    
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def format_job_text(job):
    """Format job information for Telegram message with posting time"""
    message = f"🏢 **{job['title']}**\n"
    message += f"🏭 **Company:** {job['company']}\n"
    message += f"📍 **Location:** {job['location']}\n"
    
    if job.get('posted_time'):
        message += f"⏰ **Posted:** {job['posted_time']}\n"
    
    message += f"🔗 **Apply:** [Link]({job['link']})\n"
    message += f"📱 **Source:** {job['source']}"
    
    return message

def clean_text(text):
    """Clean and normalize text"""
    if text:
        return re.sub(r'\s+', ' ', text.strip())
    return "Not specified"

def parse_relative_time(time_text):
    """Parse relative time strings like '2 hours ago', '1 day ago', etc."""
    if not time_text:
        return None
    
    time_text = time_text.lower().strip()
    
    # Patterns for relative time
    patterns = {
        r'(\d+)\s*seconds? ago': 'seconds',
        r'(\d+)\s*minutes? ago': 'minutes',
        r'(\d+)\s*hours? ago': 'hours',
        r'(\d+)\s*days? ago': 'days',
        r'(\d+)\s*weeks? ago': 'weeks',
        r'(\d+)\s*months? ago': 'months',
    }
    
    for pattern, unit in patterns.items():
        match = re.search(pattern, time_text)
        if match:
            value = int(match.group(1))
            now = datetime.now()
            
            if unit == 'seconds':
                return now - timedelta(seconds=value)
            elif unit == 'minutes':
                return now - timedelta(minutes=value)
            elif unit == 'hours':
                return now - timedelta(hours=value)
            elif unit == 'days':
                return now - timedelta(days=value)
            elif unit == 'weeks':
                return now - timedelta(weeks=value)
            elif unit == 'months':
                return now - timedelta(days=value*30)
    
    return None

def format_posted_time(posted_date):
    """Format the posted time in a user-friendly way"""
    if not posted_date:
        return "Recently"
    
    if isinstance(posted_date, str):
        return posted_date
    
    now = datetime.now()
    time_diff = now - posted_date
    
    if time_diff.days == 0:
        if time_diff.seconds < 3600:  # Less than 1 hour
            minutes = time_diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            hours = time_diff.seconds // 3600
            return f"{hours} hours ago"
    elif time_diff.days == 1:
        return "1 day ago"
    elif time_diff.days < 7:
        return f"{time_diff.days} days ago"
    else:
        return posted_date.strftime("%b %d, %Y")

def log_message(message):
    """Simple logging function"""
    print(f"[LOG] {message}")