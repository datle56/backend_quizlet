#!/usr/bin/env python3
"""
Simple service test without problematic imports
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.study_set import Term
from app.models.study_progress import StudySession, StudyModeEnum, TestSession, MatchGame
from datetime import datetime
import random

def test_simple_services():
    """Test simple service operations"""
    print("🔍 Testing Simple Service Operations...")
    
    with Session(engine) as db:
        # Test user ID and study set ID
        user_id = 3  # testuser2
        study_set_id = 1
        
        print(f"Testing with user_id={user_id}, study_set_id={study_set_id}")
        
        # Test 1: Check if terms exist
        print("\n📝 Checking terms...")
        terms = db.query(Term).filter_by(study_set_id=study_set_id).all()
        print(f"Found {len(terms)} terms")
        for term in terms:
            print(f"  - {term.term}: {term.definition}")
        
        # Test 2: Create study session manually
        print("\n📚 Creating study session...")
        try:
            session = StudySession(
                user_id=user_id,
                study_set_id=study_set_id,
                study_mode=StudyModeEnum.test,
                started_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            print(f"✅ Study session created with ID: {session.id}")
            
            # Test 3: Create test session
            print("\n📝 Creating test session...")
            test_session = TestSession(
                study_session_id=session.id,
                max_questions=5,
                answer_with="both",
                question_types=["written"],
                time_limit=300,
                randomized_order=True,
                created_at=datetime.utcnow()
            )
            db.add(test_session)
            db.commit()
            db.refresh(test_session)
            print(f"✅ Test session created with ID: {test_session.id}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Create match game
        print("\n🎯 Creating match game...")
        try:
            # Create another study session for match
            match_session = StudySession(
                user_id=user_id,
                study_set_id=study_set_id,
                study_mode=StudyModeEnum.match,
                started_at=datetime.utcnow()
            )
            db.add(match_session)
            db.commit()
            db.refresh(match_session)
            
            # Create match game
            selected_terms = random.sample(terms, min(4, len(terms)))
            selected_term_ids = [t.id for t in selected_terms]
            
            match_game = MatchGame(
                study_session_id=match_session.id,
                pairs_count=len(selected_terms),
                selected_terms=selected_term_ids
            )
            db.add(match_game)
            db.commit()
            db.refresh(match_game)
            print(f"✅ Match game created with ID: {match_game.id}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_simple_services() 