#!/usr/bin/env python3
"""
Test script for Study Modes API
Tests all the study mode endpoints to ensure they work correctly
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def login_user() -> str:
    """Login and get access token"""
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def make_authenticated_request(method: str, endpoint: str, token: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make authenticated request to API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    if method.upper() == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    elif method.upper() == "POST":
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
    elif method.upper() == "PUT":
        response = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    print(f"{method} {endpoint} - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def test_flashcards_mode(token: str, study_set_id: int):
    """Test flashcards mode endpoints"""
    print("\n=== Testing Flashcards Mode ===")
    
    # Get flashcards
    flashcards = make_authenticated_request("GET", f"/api/v1/study/modes/flashcards/{study_set_id}", token)
    if flashcards:
        print(f"✅ Got {len(flashcards)} flashcards")
        
        # Star first card
        if flashcards:
            first_card = flashcards[0]
            star_result = make_authenticated_request(
                "POST", 
                f"/api/v1/study/modes/flashcards/{study_set_id}/star/{first_card['term_id']}", 
                token, 
                {"starred": True}
            )
            if star_result:
                print("✅ Starred first card")
            
            # Get starred cards
            starred_cards = make_authenticated_request("GET", f"/api/v1/study/modes/flashcards/{study_set_id}/starred", token)
            if starred_cards:
                print(f"✅ Got {len(starred_cards['cards'])} starred cards")

def test_test_mode(token: str, study_set_id: int):
    """Test test mode endpoints"""
    print("\n=== Testing Test Mode ===")
    
    # Create test
    test_config = {
        "max_questions": 5,
        "answer_with": "both",
        "question_types": ["multiple_choice", "written"],
        "time_limit": 300,
        "randomize_order": True
    }
    
    test_session = make_authenticated_request("POST", f"/api/v1/study/modes/test/{study_set_id}", token, test_config)
    if test_session:
        print(f"✅ Created test session with {test_session['total_questions']} questions")
        
        # Get test
        test_data = make_authenticated_request("GET", f"/api/v1/study/modes/test/{test_session['test_id']}", token)
        if test_data:
            print(f"✅ Retrieved test with {len(test_data['questions'])} questions")
            
            # Submit test (with dummy answers)
            answers = []
            for question in test_data['questions']:
                answers.append({
                    "question_id": question['question_id'],
                    "answer": question['correct_answer'],
                    "time_spent": 10.0
                })
            
            submission = {
                "answers": answers,
                "total_time_spent": 50.0
            }
            
            result = make_authenticated_request("POST", f"/api/v1/study/modes/test/{test_session['test_id']}/submit", token, submission)
            if result:
                print(f"✅ Test completed with score: {result['score']}")

def test_match_mode(token: str, study_set_id: int):
    """Test match mode endpoints"""
    print("\n=== Testing Match Mode ===")
    
    # Create match game
    match_game = make_authenticated_request("POST", f"/api/v1/study/modes/match/{study_set_id}?pairs_count=4", token)
    if match_game:
        print(f"✅ Created match game with {match_game['pairs_count']} pairs")
        print(f"✅ Game has {len(match_game['cards'])} cards")
        
        # Submit a move (simplified)
        if len(match_game['cards']) >= 2:
            move_data = {
                "first_card_id": match_game['cards'][0]['card_id'],
                "second_card_id": match_game['cards'][1]['card_id']
            }
            
            move_result = make_authenticated_request("POST", f"/api/v1/study/modes/match/{match_game['game_id']}/move", token, move_data)
            if move_result:
                print(f"✅ Move submitted, is_match: {move_result['is_match']}")
        
        # Complete game
        completion_data = {
            "completion_time": 120.0,
            "incorrect_matches": 2
        }
        
        completion_result = make_authenticated_request("POST", f"/api/v1/study/modes/match/{match_game['game_id']}/complete", token, completion_data)
        if completion_result:
            print(f"✅ Game completed with score: {completion_result['score']}")

def test_gravity_mode(token: str, study_set_id: int):
    """Test gravity mode endpoints"""
    print("\n=== Testing Gravity Mode ===")
    
    # Create gravity game
    gravity_game = make_authenticated_request("POST", f"/api/v1/study/modes/gravity/{study_set_id}?difficulty_level=2", token)
    if gravity_game:
        print(f"✅ Created gravity game with difficulty {gravity_game['difficulty_level']}")
        
        # Submit an answer
        answer_data = {
            "term_id": 1,  # Assuming term_id 1 exists
            "answer": "test answer",
            "time_to_answer": 5.0
        }
        
        answer_result = make_authenticated_request("POST", f"/api/v1/study/modes/gravity/{gravity_game['game_id']}/answer", token, answer_data)
        if answer_result:
            print(f"✅ Answer submitted, is_correct: {answer_result['is_correct']}")
        
        # Complete game with correct data
        completion_data = {
            "final_score": 150,
            "terms_destroyed": 12,
            "game_duration": 180.0,
            "lives_remaining": 1
        }
        
        completion_result = make_authenticated_request("POST", f"/api/v1/study/modes/gravity/{gravity_game['game_id']}/complete", token, completion_data)
        if completion_result:
            print(f"✅ Game completed with final score: {completion_result['final_score']}")

def test_write_mode(token: str, study_set_id: int):
    """Test write mode endpoints"""
    print("\n=== Testing Write Mode ===")
    
    # Get write questions
    questions = make_authenticated_request("GET", f"/api/v1/study/modes/write/{study_set_id}?answer_with=both", token)
    if questions:
        print(f"✅ Got {len(questions)} write questions")
        
        # Check an answer
        if questions:
            first_question = questions[0]
            answer_data = {
                "question_id": first_question['question_id'],
                "answer": first_question['correct_answer'],
                "response_time": 8.0
            }
            
            check_result = make_authenticated_request("POST", f"/api/v1/study/modes/write/{study_set_id}/check", token, answer_data)
            if check_result:
                print(f"✅ Answer checked, is_correct: {check_result['is_correct']}")

def test_study_progress(token: str, study_set_id: int):
    """Test study progress endpoints"""
    print("\n=== Testing Study Progress ===")
    
    # Get study progress
    progress = make_authenticated_request("GET", f"/api/v1/study/progress/{study_set_id}", token)
    if progress:
        print(f"✅ Got study progress for {len(progress)} terms")
        
        # Update term progress
        if progress:
            first_progress = progress[0]
            update_data = {
                "correct": True,
                "response_time": 5.0,
                "difficulty": 2
            }
            
            update_result = make_authenticated_request("POST", f"/api/v1/study/progress/{study_set_id}/terms/{first_progress['term_id']}", token, update_data)
            if update_result:
                print("✅ Updated term progress")

def main():
    """Main test function"""
    print("🚀 Starting Study Modes API Tests")
    
    # Login
    token = login_user()
    if not token:
        print("❌ Failed to login. Exiting.")
        return
    
    print("✅ Login successful")
    
    # Use a test study set ID (you may need to create one first)
    study_set_id = 1  # Change this to an actual study set ID in your database
    
    try:
        # Test all modes
        test_study_progress(token, study_set_id)
        test_flashcards_mode(token, study_set_id)
        test_test_mode(token, study_set_id)
        test_match_mode(token, study_set_id)
        test_gravity_mode(token, study_set_id)
        test_write_mode(token, study_set_id)
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main() 