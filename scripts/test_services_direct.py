#!/usr/bin/env python3
"""
Test service methods directly
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.services.study_service import StudyService
from app.schemas.study_progress import TestConfig

def test_services_directly():
    """Test service methods directly"""
    print("🔍 Testing Service Methods Directly...")
    
    with Session(engine) as db:
        # Test user ID and study set ID
        user_id = 3  # testuser2
        study_set_id = 1
        
        print(f"Testing with user_id={user_id}, study_set_id={study_set_id}")
        
        # Test 1: Create test session
        print("\n📝 Testing create_test_session...")
        try:
            test_config = TestConfig(
                max_questions=5,
                answer_with="both",
                question_types=["written"],
                time_limit=300,
                randomize_order=True
            )
            
            result = StudyService.create_test_session(db, user_id, study_set_id, test_config)
            print(f"✅ Test session created: {result}")
            
        except Exception as e:
            print(f"❌ Test session creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Create match game
        print("\n🎯 Testing create_match_game...")
        try:
            result = StudyService.create_match_game(db, user_id, study_set_id, 4)
            print(f"✅ Match game created: {result}")
            
        except Exception as e:
            print(f"❌ Match game creation failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_services_directly() 