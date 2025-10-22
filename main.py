import os
import sys
import time
import schedule
from datetime import datetime
import threading

from config import KEYWORDS, LOCATION, SCRAPING_INTERVAL

# Smart scraper selection - try Selenium first, fallback to requests
try:
    from scraper.naukri_scraper import scrape_naukri_recent_jobs
    NAUKRI_SCRAPER = "selenium"
    print("✅ Using Selenium for Naukri")
except Exception as e:
    print(f"⚠️ Selenium failed: {e}")
    from scraper.naukri_fallback import scrape_naukri_fallback as scrape_naukri_recent_jobs
    NAUKRI_SCRAPER = "fallback"
    print("✅ Using fallback for Naukri")

from scraper.linkedin_scraper import scrape_linkedin_recent_jobs
from db.database import create_table, save_job, get_sent_jobs_count, cleanup_old_jobs, start_daily_cleanup, get_database_size
from tg.bot import send_bulk_alerts, send_summary, send_message
from utils.helpers import log_message

def run_job_scraping():
    """Main function to run all scrapers and send alerts"""
    try:
        log_message("🔄 Starting job scraping session...")
        
        all_jobs = []
        new_jobs = []
        
        # Run scrapers for each keyword
        for keyword in KEYWORDS[:3]:
            log_message(f"🔍 Scraping jobs for: {keyword}")
            
            try:
                # Scrape Naukri (auto-selects best method)
                naukri_jobs = scrape_naukri_recent_jobs(keyword, LOCATION)
                
                # Scrape LinkedIn (always requests-based)
                linkedin_jobs = scrape_linkedin_recent_jobs(keyword, LOCATION)
                
                all_jobs.extend(naukri_jobs)
                all_jobs.extend(linkedin_jobs)
                
                log_message(f"✅ {keyword}: Naukri({len(naukri_jobs)}), LinkedIn({len(linkedin_jobs)}) | Naukri mode: {NAUKRI_SCRAPER}")
                time.sleep(3)
                
            except Exception as e:
                log_message(f"❌ Error scraping {keyword}: {e}")
                continue
        
        # Remove duplicates and filter new jobs
        seen_links = set()
        for job in all_jobs:
            if job['link'] and job['link'] not in seen_links:
                seen_links.add(job['link'])
                if save_job(job):
                    new_jobs.append(job)
        
        # Send alerts
        total_sent = 0
        if new_jobs:
            total_sent = send_bulk_alerts(new_jobs[:8])
        
        # Send summary with scraper info
        summary_msg = f"""
📊 Scraping Complete
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔍 Total Scanned: {len(all_jobs)}
🆕 New Jobs: {len(new_jobs)}
📤 Sent: {total_sent}
🔧 Naukri Mode: {NAUKRI_SCRAPER.upper()}
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