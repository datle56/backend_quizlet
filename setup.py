#!/usr/bin/env python3
"""
Setup script for Quizlet Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_project():
    """Setup the entire project"""
    print("🚀 Setting up Quizlet Backend...")
    
    # Get project root
    project_root = Path(__file__).parent
    
    # 1. Create .env file
    print("\n📝 Creating .env file...")
    env_content = """# Database Configuration
DATABASE_URL=postgresql://myuser:mypassword@128.199.158.179:5432/quizletDB
TEST_DATABASE_URL=postgresql://myuser:mypassword@128.199.158.179:5432/quizletdb_test

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Email Configuration (for future use)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Environment
ENVIRONMENT=development
DEBUG=True
"""
    
    env_file_path = project_root / ".env"
    if not env_file_path.exists():
        with open(env_file_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please update the database credentials in .env file")
    else:
        print("✅ .env file already exists")
    
    # 2. Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # 3. Initialize Alembic
    if not run_command("alembic init alembic", "Initializing Alembic"):
        return False
    
    # 4. Create initial migration
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update database credentials in .env file")
    print("2. Run: alembic upgrade head")
    print("3. Run: python run.py")
    print("4. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    setup_project() 