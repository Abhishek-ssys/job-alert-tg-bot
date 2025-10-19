#!/usr/bin/env python3
"""Test database operations"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database functionality"""
    print("\n🗃️ Testing Database...")
    
    try:
        from db.database import (
            create_table, save_job, get_sent_jobs_count, 
            cleanup_old_jobs, get_database_size
        )
        
        # Test database creation
        create_table()
        print("✅ Database table created")
        
        # Test initial count
        initial_count = get_sent_jobs_count()
        print(f"✅ Initial job count: {initial_count}")
        
        # Test saving a job
        test_job = {
            'title': 'Test Python Developer',
            'company': 'Test Company Inc',
            'location': 'Remote',
            'link': 'https://example.com/test-job-123',
            'source': 'Test',
            'posted_time': 'Just now'
        }
        
        # Save first time - should succeed
        result1 = save_job(test_job)
        assert result1 == True, "First save should return True"
        print("✅ First job save successful")
        
        # Save same job again - should fail (duplicate)
        result2 = save_job(test_job)
        assert result2 == False, "Duplicate save should return False"
        print("✅ Duplicate job prevention working")
        
        # Test count after save
        new_count = get_sent_jobs_count()
        assert new_count == initial_count + 1, f"Count should be {initial_count + 1}, got {new_count}"
        print(f"✅ Job count after save: {new_count}")
        
        # Test database size
        db_size = get_database_size()
        assert db_size > 0, "Database file should have size > 0"
        print(f"✅ Database size: {db_size} bytes")
        
        # Test cleanup
        deleted_count = cleanup_old_jobs()
        assert deleted_count >= 1, f"Should delete at least 1 job, deleted {deleted_count}"
        print(f"✅ Cleanup removed {deleted_count} jobs")
        
        # Verify cleanup
        final_count = get_sent_jobs_count()
        assert final_count == 0, f"After cleanup, count should be 0, got {final_count}"
        print(f"✅ Final job count: {final_count}")
        
        print("✅ Database test passed")
        return "PASS"
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return f"Database error: {e}"