#!/usr/bin/env python3
"""
Script to check database content and add test data
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.models.study_set import StudySet, Term

def check_and_populate_db():
    """Check database content and add test data if needed"""
    print("🔍 Checking database content...")
    
    with Session(engine) as db:
        # Check users
        users = db.query(User).all()
        print(f"👥 Users found: {len(users)}")
        
        if not users:
            print("➕ Creating test user...")
            test_user = User(
                username="testuser",
                email="test@example.com",
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8eG",  # password123
                full_name="Test User"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created user: {test_user.username} (ID: {test_user.id})")
        else:
            test_user = users[0]
            print(f"✅ Using existing user: {test_user.username} (ID: {test_user.id})")
        
        # Check study sets
        study_sets = db.query(StudySet).all()
        print(f"📚 Study sets found: {len(study_sets)}")
        
        if not study_sets:
            print("➕ Creating test study set...")
            test_study_set = StudySet(
                title="Basic English Vocabulary",
                description="Common English words and their definitions",
                user_id=test_user.id,
                is_public=True,
                language_from="en",
                language_to="en"
            )
            db.add(test_study_set)
            db.commit()
            db.refresh(test_study_set)
            print(f"✅ Created study set: {test_study_set.title} (ID: {test_study_set.id})")
        else:
            test_study_set = study_sets[0]
            print(f"✅ Using existing study set: {test_study_set.title} (ID: {test_study_set.id})")
        
        # Check terms
        terms = db.query(Term).filter_by(study_set_id=test_study_set.id).all()
        print(f"📝 Terms found in study set {test_study_set.id}: {len(terms)}")
        
        if not terms:
            print("➕ Creating test terms...")
            test_terms = [
                Term(study_set_id=test_study_set.id, term="Hello", definition="A greeting", position=1),
                Term(study_set_id=test_study_set.id, term="World", definition="The earth and all life upon it", position=2),
                Term(study_set_id=test_study_set.id, term="Computer", definition="An electronic device for processing data", position=3),
                Term(study_set_id=test_study_set.id, term="Programming", definition="The process of writing computer code", position=4),
                Term(study_set_id=test_study_set.id, term="Database", definition="A structured collection of data", position=5),
                Term(study_set_id=test_study_set.id, term="Algorithm", definition="A step-by-step procedure for solving a problem", position=6),
            ]
            
            for term in test_terms:
                db.add(term)
            
            db.commit()
            print(f"✅ Created {len(test_terms)} test terms")
        else:
            print("✅ Terms already exist")
            for term in terms[:3]:  # Show first 3 terms
                print(f"   - {term.term}: {term.definition}")
        
        # Update study set terms count
        term_count = db.query(Term).filter_by(study_set_id=test_study_set.id).count()
        test_study_set.terms_count = term_count
        db.commit()
        print(f"📊 Updated study set terms count: {term_count}")

if __name__ == "__main__":
    check_and_populate_db() 