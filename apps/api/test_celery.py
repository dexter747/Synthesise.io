#!/usr/bin/env python3
"""
Quick test to verify Celery integration works
Run this after starting Docker services
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.celery_app import celery_app
from app.tasks.generation import generate_dataset
from app.tasks.notifications import send_email


def test_celery_connection():
    """Test if Celery can connect to Redis"""
    print("Testing Celery connection to Redis...")
    
    try:
        # Ping the broker
        celery_app.control.ping(timeout=1.0)
        print("✅ Successfully connected to Redis broker")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return False


def test_simple_task():
    """Test a simple Celery task"""
    print("\nTesting simple task execution...")
    
    try:
        # Queue a test task
        result = send_email.delay(
            to="test@example.com",
            subject="Test Email",
            body="This is a test"
        )
        
        print(f"✅ Task queued successfully: {result.id}")
        print(f"   Waiting for result (timeout 10s)...")
        
        # Wait for result
        task_result = result.get(timeout=10)
        print(f"✅ Task completed: {task_result}")
        return True
        
    except Exception as e:
        print(f"❌ Task failed: {e}")
        return False


def test_generation_task():
    """Test data generation task"""
    print("\nTesting generation task...")
    
    try:
        # Queue generation task
        result = generate_dataset.delay(
            job_id="test_job_123",
            request_data={
                "row_count": 10,
                "format": "csv",
                "sample_data": [{"name": "John", "age": 30}]
            }
        )
        
        print(f"✅ Generation task queued: {result.id}")
        print(f"   Waiting for result (timeout 30s)...")
        
        task_result = result.get(timeout=30)
        print(f"✅ Generation completed: {task_result}")
        return True
        
    except Exception as e:
        print(f"❌ Generation task failed: {e}")
        return False


def test_worker_status():
    """Check if workers are running"""
    print("\nChecking worker status...")
    
    try:
        stats = celery_app.control.inspect().stats()
        
        if not stats:
            print("❌ No workers found")
            return False
        
        print(f"✅ Found {len(stats)} worker(s):")
        for worker_name, worker_stats in stats.items():
            print(f"   - {worker_name}")
            print(f"     Pool: {worker_stats.get('pool', {}).get('implementation', 'unknown')}")
            print(f"     Max concurrency: {worker_stats.get('pool', {}).get('max-concurrency', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get worker status: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("CELERY INTEGRATION TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Connection
    results.append(test_celery_connection())
    
    # Test 2: Worker status
    results.append(test_worker_status())
    
    # Test 3: Simple task
    results.append(test_simple_task())
    
    # Test 4: Generation task
    results.append(test_generation_task())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Celery is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
