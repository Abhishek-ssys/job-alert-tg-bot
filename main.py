import os
# Check if we're running on Railway
if os.getenv('RAILWAY_ENVIRONMENT'):
    # Let webdriver-manager handle everything
    os.environ['WDM_LOG_LEVEL'] = '0'  # Disable webdriver-manager logs
    os.environ['WDM_LOCAL'] = '1'      # Use local cache

# Rest of your imports remain exactly the same
import time
import schedule
from datetime import datetime
import threading
from config import KEYWORDS, LOCATION, SCRAPING_INTERVAL
from scraper.naukri_scraper import scrape_naukri_recent_jobs
from scraper.linkedin_scraper import scrape_linkedin_recent_jobs
from db.database import create_table, save_job, get_sent_jobs_count, cleanup_old_jobs, start_daily_cleanup, get_database_size
from tg.bot import send_bulk_alerts, send_summary, send_message
from utils.helpers import log_message

# Rest of your code remains exactly the same...

# Rest of your code remains the same...
def run_job_scraping():
    """Main function to run all scrapers and send alerts"""
    try:
        log_message("🔄 Starting job scraping session...")
        
        all_jobs = []
        new_jobs = []
        
        # Run scrapers for each keyword (limit to avoid timeout)
        for keyword in KEYWORDS[:3]:
            log_message(f"🔍 Scraping jobs for: {keyword}")
            
            try:
                # Scrape with recent filtering (last 24 hours)
                naukri_jobs = scrape_naukri_recent_jobs(keyword, LOCATION, max_hours_old=24)
                linkedin_jobs = scrape_linkedin_recent_jobs(keyword, LOCATION, max_hours_old=24)
                
                all_jobs.extend(naukri_jobs)
                all_jobs.extend(linkedin_jobs)
                
                log_message(f"✅ {keyword}: Naukri({len(naukri_jobs)}), LinkedIn({len(linkedin_jobs)})")
                time.sleep(5)  # Delay between keywords
                
            except Exception as e:
                log_message(f"❌ Error scraping {keyword}: {e}")
                continue
        
        # Remove duplicates and filter new jobs
        seen_links = set()
        for job in all_jobs:
            if job['link'] and job['link'] not in seen_links:
                seen_links.add(job['link'])
                if save_job(job):  # Only save if it's new
                    new_jobs.append(job)
        
        # Send alerts in smaller batches
        total_sent = 0
        if new_jobs:
            total_sent = send_bulk_alerts(new_jobs[:10])  # Limit to 10 jobs per cycle
        
        # Send summary with database info
        db_size_kb = get_database_size() / 1024
        summary_msg = f"""
📊 Scraping Cycle Complete
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔍 Total Scanned: {len(all_jobs)}
🆕 New Jobs Found: {len(new_jobs)}
📤 Successfully Sent: {total_sent}
💾 DB Size: {db_size_kb:.1f} KB
🗃️ Total Jobs in DB: {get_sent_jobs_count()}
        """
        send_message(summary_msg)
        
        log_message(f"✅ Cycle complete. Found: {len(all_jobs)}, New: {len(new_jobs)}, Sent: {total_sent}")
        
    except Exception as e:
        error_msg = f"❌ Error in scraping cycle: {str(e)}"
        log_message(error_msg)
        send_message(error_msg)

def manual_cleanup():
    """Manual cleanup function that can be scheduled"""
    try:
        deleted_count = cleanup_old_jobs()
        message = f"🧹 Manual Cleanup Complete!\n🗑️ Removed {deleted_count} jobs\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        send_message(message)
        log_message(f"Manual cleanup: Removed {deleted_count} jobs")
    except Exception as e:
        log_message(f"Error in manual cleanup: {e}")

def keep_alive():
    """Send heartbeat every 6 hours to prevent shutdown"""
    while True:
        try:
            db_count = get_sent_jobs_count()
            db_size = get_database_size() / 1024
            send_message(f"💓 Job Bot Heartbeat\n🗃️ Jobs in DB: {db_count}\n💾 DB Size: {db_size:.1f} KB\n⏰ Time: {datetime.now().strftime('%H:%M')}")
            time.sleep(6 * 60 * 60)  # 6 hours
        except:
            time.sleep(60)

def main():
    """Main entry point optimized for Railway"""
    log_message("🚀 Job Alert Bot Starting on Railway...")
    
    # Initialize database
    create_table()
    sent_count = get_sent_jobs_count()
    log_message(f"📦 Database initialized. Previous jobs: {sent_count}")
    
    # Start daily cleanup scheduler
    start_daily_cleanup()
    
    # Schedule daily cleanup at specific time (e.g., 2:00 AM)
    schedule.every().day.at("02:00").do(manual_cleanup)
    
    # Send startup message
    send_message(f"""
🤖 Job Alert Bot Activated!
📍 Location: {LOCATION}
🔍 Keywords: {', '.join(KEYWORDS[:3])}
⏰ Interval: {SCRAPING_INTERVAL} minutes
🧹 Auto-cleanup: Every 24 hours
🚀 Deployed on Railway
    """)
    
    # Start keep-alive thread
    heartbeat_thread = threading.Thread(target=keep_alive, daemon=True)
    heartbeat_thread.start()
    
    # Schedule the scraping job
    schedule.every(SCRAPING_INTERVAL).minutes.do(run_job_scraping)
    
    # Run immediately once
    run_job_scraping()
    
    # Keep the script running
    log_message("⏰ Scheduler started. Waiting for intervals...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            log_message("🛑 Bot stopped by user")
            break
        except Exception as e:
            log_message(f"❌ Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main()