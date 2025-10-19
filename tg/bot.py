import requests
from config import TOKEN, CHAT_ID

def send_message(text):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def send_job_alert(job):
    """Send a single job alert"""
    from utils.helpers import format_job_text
    message = format_job_text(job)
    return send_message(message)

def send_bulk_alerts(jobs):
    """Send multiple job alerts"""
    from utils.helpers import format_job_text
    
    if not jobs:
        return 0
    
    sent_count = 0
    for job in jobs:
        message = format_job_text(job)
        if send_message(message):
            sent_count += 1
    
    return sent_count

def send_summary(total_found, total_sent):
    """Send a summary of the scraping session"""
    summary = f"📊 **Job Alert Summary**\n"
    summary += f"🔄 Jobs found: {total_found}\n"
    summary += f"📤 Jobs sent: {total_sent}\n"
    summary += f"⏰ Next check in 30 minutes"
    
    send_message(summary)