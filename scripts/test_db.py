#!/usr/bin/env python3
"""
Database connection test script
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine
from app.core.config import settings

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("✅ Database connection successful!")
            
            # Test if tables exist
            result = connection.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in result]
            print(f"📋 Existing tables: {tables}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure database exists")
        print("4. Check network connectivity")
        return False
    
    return True

if __name__ == "__main__":
    test_database_connection() 