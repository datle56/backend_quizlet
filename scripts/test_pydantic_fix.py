#!/usr/bin/env python3
"""
Script test fix Pydantic validation errors
"""

import requests
import json

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

def test_term_progress_update(token, study_set_id, term_id):
    """Test TermProgressUpdate schema"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧪 Testing TermProgressUpdate schema...")
    
    # Test 1: Chỉ gửi required field
    print("1. Testing with only required field (correct)...")
    data = {"correct": True}
    response = requests.post(
        f"{BASE_URL}/api/v1/study/progress/{study_set_id}/terms/{term_id}", 
        json=data, headers=headers
    )
    if response.status_code == 200:
        print("✅ Success: Only correct field")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: Gửi tất cả fields
    print("2. Testing with all fields...")
    data = {"correct": True, "response_time": 2.5, "difficulty": 1}
    response = requests.post(
        f"{BASE_URL}/api/v1/study/progress/{study_set_id}/terms/{term_id}", 
        json=data, headers=headers
    )
    if response.status_code == 200:
        print("✅ Success: All fields")
    else:
        print(f"❌ Failed: {response.text}")

def test_study_session_update(token, study_set_id):
    """Test StudySessionUpdate schema"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing StudySessionUpdate schema...")
    
    # Start session first
    print("1. Starting study session...")
    session_data = {"study_set_id": study_set_id, "study_mode": "flashcards"}
    response = requests.post(f"{BASE_URL}/api/v1/study/session", json=session_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.text}")
        return
    
    session = response.json()
    session_id = session["id"]
    print(f"✅ Session started (ID: {session_id})")
    
    # Test 1: Chỉ gửi required fields
    print("2. Testing with minimal fields...")
    data = {"score": 85.5}
    response = requests.put(f"{BASE_URL}/api/v1/study/session/{session_id}", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ Success: Minimal fields")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: Gửi tất cả fields
    print("3. Testing with all fields...")
    data = {
        "completed_at": "2024-06-01T10:30:00Z",
        "score": 90.0,
        "total_questions": 20,
        "correct_answers": 18,
        "time_spent_seconds": 1800
    }
    response = requests.put(f"{BASE_URL}/api/v1/study/session/{session_id}", json=data, headers=headers)
    if response.status_code == 200:
        print("✅ Success: All fields")
    else:
        print(f"❌ Failed: {response.text}")

def main():
    print("🔧 TESTING PYDANTIC FIXES")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        return
    
    # Nhập study_set_id và term_id
    study_set_id = input("Enter study_set_id: ")
    term_id = input("Enter term_id: ")
    
    try:
        study_set_id = int(study_set_id)
        term_id = int(term_id)
    except ValueError:
        print("Invalid ID")
        return
    
    # Test TermProgressUpdate
    test_term_progress_update(token, study_set_id, term_id)
    
    # Test StudySessionUpdate
    test_study_session_update(token, study_set_id)
    
    print("\n🎉 Pydantic fix test completed!")

if __name__ == "__main__":
    main() 