#!/usr/bin/env python3
"""
Check database schema
"""

import psycopg2
from app.core.config import settings

def check_schema():
    """Check database schema"""
    print("🔍 Checking Database Schema...")
    
    # Parse database URL
    db_url = settings.database_url
    # Extract connection info from URL like: postgresql://user:pass@host:port/dbname
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else '5432'
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ''
    dbname = host_port_db[1]
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        
        cur = conn.cursor()
        
        # Check test_sessions table
        print("\n📋 Checking test_sessions table...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'test_sessions'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[1] == 'YES'})")
        
        # Check match_games table
        print("\n📋 Checking match_games table...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'match_games'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[1] == 'YES'})")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema() 