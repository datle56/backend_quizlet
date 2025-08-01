#!/usr/bin/env python3
"""
Setup environment file script
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with default configuration"""
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
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    env_file_path = project_root / ".env"
    
    # Create .env file if it doesn't exist
    if not env_file_path.exists():
        with open(env_file_path, "w") as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file_path}")
        print("⚠️  Please update the database credentials in .env file")
    else:
        print(f"✅ .env file already exists at {env_file_path}")


if __name__ == "__main__":
    create_env_file() 