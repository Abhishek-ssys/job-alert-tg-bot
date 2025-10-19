import sqlite3
import os
from datetime import datetime, timedelta
from config import DB_PATH
import threading
import time

def create_table():
    """Create jobs table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            posted_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_job(job):
    """Save job to database if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (title, company, location, link, source, posted_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job['title'], job['company'], job['location'], job['link'], job['source'], job.get('posted_time')))
        
        conn.commit()
        is_new = cursor.rowcount > 0
        return is_new
        
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_sent_jobs_count():
    """Get total count of jobs in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def cleanup_old_jobs():
    """Delete all jobs from the database (clean slate)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM jobs')
        conn.commit()
        deleted_count = cursor.rowcount
        
        # Reset autoincrement counter
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="jobs"')
        conn.commit()
        
        return deleted_count
        
    except Exception as e:
        print(f"Error cleaning up database: {e}")
        return 0
    finally:
        conn.close()

def get_database_size():
    """Get database file size"""
    if os.path.exists(DB_PATH):
        return os.path.getsize(DB_PATH)
    return 0

def start_daily_cleanup():
    """Start background thread for daily database cleanup"""
    def cleanup_worker():
        while True:
            try:
                # Wait 24 hours
                time.sleep(24 * 60 * 60)  # 24 hours in seconds
                
                # Perform cleanup
                deleted_count = cleanup_old_jobs()
                print(f"🧹 Daily cleanup: Removed {deleted_count} old jobs")
                
            except Exception as e:
                print(f"Error in cleanup worker: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    print("✅ Daily database cleanup scheduler started")