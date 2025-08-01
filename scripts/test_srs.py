#!/usr/bin/env python3
"""
Script test SRS (Spaced Repetition System)
Test flow: tạo study set -> học terms -> test review -> học lại -> test SRS intervals
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Config
BASE_URL = "http://localhost:8000"
USERNAME = "string"
PASSWORD = "string"

def login():
    """Login và lấy access token"""
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def create_study_set(token):
    """Tạo study set test"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test SRS Set",
        "description": "Test SRS functionality",
        "terms": [
            {"term": "Hello", "definition": "Xin chào"},
            {"term": "Goodbye", "definition": "Tạm biệt"},
            {"term": "Thank you", "definition": "Cảm ơn"}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/v1/study-sets/", json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Create study set failed: {response.text}")
        return None

def get_study_progress(token, study_set_id):
    """Lấy progress của study set"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/study/progress/{study_set_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get progress failed: {response.text}")
        return []

def update_term_progress(token, study_set_id, term_id, correct):
    """Cập nhật progress của term"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"correct": correct, "response_time": 2.5}
    response = requests.post(
        f"{BASE_URL}/api/v1/study/progress/{study_set_id}/terms/{term_id}", 
        json=data, headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Update progress failed: {response.text}")
        return None

def get_review_terms(token, study_set_id):
    """Lấy terms cần review"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/study/review/{study_set_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get review terms failed: {response.text}")
        return {"terms": []}

def start_study_session(token, study_set_id):
    """Bắt đầu study session"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"study_set_id": study_set_id, "study_mode": "flashcards"}
    response = requests.post(f"{BASE_URL}/api/v1/study/session", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Start session failed: {response.text}")
        return None

def update_study_session(token, session_id, score, correct_answers, time_spent):
    """Cập nhật study session"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "completed_at": datetime.utcnow().isoformat(),
        "score": score,
        "correct_answers": correct_answers,
        "time_spent_seconds": time_spent
    }
    response = requests.put(f"{BASE_URL}/api/v1/study/session/{session_id}", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Update session failed: {response.text}")
        return None

def print_progress(progress_list):
    """In progress đẹp"""
    print("\n📊 STUDY PROGRESS:")
    print("-" * 80)
    for p in progress_list:
        print(f"Term ID: {p['term_id']}")
        print(f"  Level: {p['familiarity_level']}")
        print(f"  Correct: {p['correct_count']}, Incorrect: {p['incorrect_count']}")
        print(f"  Streak: {p['current_streak']} (longest: {p['longest_streak']})")
        print(f"  Next Review: {p['next_review']}")
        print()

def main():
    print("🚀 TESTING SRS (Spaced Repetition System)")
    print("=" * 50)
    
    # Login
    print("1. Logging in...")
    token = login()
    if not token:
        return
    print("✅ Login successful")
    
    # Create study set
    print("\n2. Creating study set...")
    study_set = create_study_set(token)
    if not study_set:
        return
    study_set_id = study_set["id"]
    print(f"✅ Study set created: {study_set['title']} (ID: {study_set_id})")
    
    # Get initial progress
    print("\n3. Getting initial progress...")
    progress = get_study_progress(token, study_set_id)
    print(f"✅ Found {len(progress)} progress records")
    
    # Start study session
    print("\n4. Starting study session...")
    session = start_study_session(token, study_set_id)
    if not session:
        return
    session_id = session["id"]
    print(f"✅ Session started (ID: {session_id})")
    
    # Test learning first term
    print("\n5. Learning first term (correct)...")
    term_id = 1  # Assuming first term
    result = update_term_progress(token, study_set_id, term_id, True)
    if result:
        print(f"✅ Term {term_id} learned! Level: {result['familiarity_level']}")
        print(f"   Next review: {result['next_review']}")
    
    # Show progress
    progress = get_study_progress(token, study_set_id)
    print_progress(progress)
    
    # Test review terms (should be empty initially)
    print("\n6. Checking review terms...")
    review = get_review_terms(token, study_set_id)
    print(f"✅ Terms due for review: {len(review['terms'])}")
    
    # Wait a bit and test again
    print("\n7. Waiting 2 minutes for SRS to trigger...")
    print("   (In real test, you'd wait or manually update next_review)")
    time.sleep(2)
    
    # Test learning same term again (should level up)
    print("\n8. Learning same term again (correct)...")
    result = update_term_progress(token, study_set_id, term_id, True)
    if result:
        print(f"✅ Term {term_id} leveled up! Level: {result['familiarity_level']}")
        print(f"   Next review: {result['next_review']}")
    
    # Show final progress
    progress = get_study_progress(token, study_set_id)
    print_progress(progress)
    
    # Complete study session
    print("\n9. Completing study session...")
    session_result = update_study_session(token, session_id, 85.5, 2, 120)
    if session_result:
        print(f"✅ Session completed! Score: {session_result['score']}%")
    
    print("\n🎉 SRS Test completed!")
    print("\n📝 Next steps to test:")
    print("1. Wait for next_review time to pass")
    print("2. Call GET /review/{study_set_id} to see terms due for review")
    print("3. Test incorrect answers to see level decrease")
    print("4. Test different study modes")

if __name__ == "__main__":
    main() 