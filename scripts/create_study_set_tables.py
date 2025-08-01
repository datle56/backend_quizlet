#!/usr/bin/env python3
"""
Script to create study set tables in the database.
Run this after setting up the database connection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import User, StudySet, Term, StudySetVersion


def create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")
    
    # Import all models to ensure they are registered with Base
    from app.models.user import User
    from app.models.study_set import StudySet, Term, StudySetVersion
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print("\nCreated tables:")
    print("- users")
    print("- study_sets")
    print("- terms")
    print("- study_set_versions")


if __name__ == "__main__":
    create_tables() 