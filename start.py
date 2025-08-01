#!/usr/bin/env python3
"""
Start script for Quizlet Backend with automatic setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found. Creating one...")
        subprocess.run([sys.executable, "scripts/setup_env.py"])
        print("✅ .env file created. Please update database credentials.")
        return False
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def test_database():
    """Test database connection"""
    try:
        subprocess.run([sys.executable, "scripts/test_db.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Database connection failed")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Quizlet Backend Server...")
    print("📖 API Documentation will be available at:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("   - Health Check: http://localhost:8000/health")
    print("\n🔄 Starting server...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🎯 Quizlet Backend Setup & Start")
    print("=" * 40)
    
    # Check and setup environment
    if not check_env_file():
        print("⚠️  Please update database credentials in .env file and run again")
        return
    
    # Check dependencies
    check_dependencies()
    
    # Test database connection
    if not test_database():
        print("⚠️  Database connection failed. Please check your .env file")
        print("   Expected format: DATABASE_URL=postgresql://user:pass@host:port/db")
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 