#!/usr/bin/env python3
"""
Simple authentication test script
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    """Test authentication endpoints"""
    print("🔍 Testing Authentication...")
    
    # Test register
    register_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123",
        "full_name": "Test User 2"
    }
    
    print("📝 Testing registration...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    print(f"Register status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Registration successful")
        user_data = response.json()
        print(f"User ID: {user_data['id']}")
    else:
        print(f"❌ Registration failed: {response.text}")
    
    # Test login
    print("\n🔑 Testing login...")
    login_data = {
        "username": "testuser2",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful")
        token_data = response.json()
        print(f"Access token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_study_sets(token: str):
    """Test study sets endpoints"""
    print("\n📚 Testing Study Sets...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get study sets
    response = requests.get(f"{BASE_URL}/api/v1/study-sets", headers=headers)
    print(f"Get study sets status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        study_sets = data.get('items', [])
        print(f"✅ Found {len(study_sets)} study sets")
        if study_sets and len(study_sets) > 0:
            study_set_id = study_sets[0]['id']
            print(f"Using study set ID: {study_set_id}")
            return study_set_id
        else:
            print("❌ No study sets found")
    else:
        print(f"❌ Failed to get study sets: {response.text}")
    
    return None

def test_study_modes(token: str, study_set_id: int):
    """Test study modes endpoints"""
    print(f"\n🎯 Testing Study Modes for study set {study_set_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test flashcards
    print("🎴 Testing flashcards...")
    response = requests.get(f"{BASE_URL}/api/v1/study/modes/flashcards/{study_set_id}", headers=headers)
    print(f"Flashcards status: {response.status_code}")
    if response.status_code == 200:
        flashcards = response.json()
        print(f"✅ Got {len(flashcards)} flashcards")
    else:
        print(f"❌ Flashcards failed: {response.text}")
    
    # Test write mode
    print("\n✍️ Testing write mode...")
    response = requests.get(f"{BASE_URL}/api/v1/study/modes/write/{study_set_id}?answer_with=both", headers=headers)
    print(f"Write mode status: {response.status_code}")
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ Got {len(questions)} write questions")
    else:
        print(f"❌ Write mode failed: {response.text}")
    
    # Test test mode
    print("\n📝 Testing test mode...")
    test_config = {
        "max_questions": 5,
        "answer_with": "both",
        "question_types": ["written"],
        "time_limit": 300,
        "randomize_order": True
    }
    response = requests.post(f"{BASE_URL}/api/v1/study/modes/test/{study_set_id}", headers=headers, json=test_config)
    print(f"Test mode status: {response.status_code}")
    if response.status_code == 200:
        test_data = response.json()
        print(f"✅ Created test with {test_data['total_questions']} questions")
    else:
        print(f"❌ Test mode failed: {response.text}")
    
    # Test match mode
    print("\n🎯 Testing match mode...")
    response = requests.post(f"{BASE_URL}/api/v1/study/modes/match/{study_set_id}?pairs_count=4", headers=headers)
    print(f"Match mode status: {response.status_code}")
    if response.status_code == 200:
        match_data = response.json()
        print(f"✅ Created match game with {match_data['pairs_count']} pairs")
    else:
        print(f"❌ Match mode failed: {response.text}")
    
    # Test gravity mode
    print("\n🎮 Testing gravity mode...")
    response = requests.post(f"{BASE_URL}/api/v1/study/modes/gravity/{study_set_id}?difficulty_level=2", headers=headers)
    print(f"Gravity mode status: {response.status_code}")
    if response.status_code == 200:
        gravity_data = response.json()
        print(f"✅ Created gravity game with difficulty {gravity_data['difficulty_level']}")
    else:
        print(f"❌ Gravity mode failed: {response.text}")

if __name__ == "__main__":
    token = test_auth()
    if token:
        study_set_id = test_study_sets(token)
        if study_set_id:
            test_study_modes(token, study_set_id) 