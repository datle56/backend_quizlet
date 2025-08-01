#!/usr/bin/env python3
"""
Debug script for study modes
"""

import requests
import json
import traceback

BASE_URL = "http://localhost:8000"

def login_user():
    """Login and get access token"""
    login_data = {
        "username": "testuser2",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def debug_test_mode(token: str, study_set_id: int):
    """Debug test mode"""
    print("\n🔍 Debugging Test Mode...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_config = {
        "max_questions": 5,
        "answer_with": "both",
        "question_types": ["written"],
        "time_limit": 300,
        "randomize_order": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/study/modes/test/{study_set_id}", headers=headers, json=test_config)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test created successfully with {data['total_questions']} questions")
        else:
            print("❌ Test creation failed")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        traceback.print_exc()

def debug_match_mode(token: str, study_set_id: int):
    """Debug match mode"""
    print("\n🔍 Debugging Match Mode...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/study/modes/match/{study_set_id}?pairs_count=4", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Match game created successfully with {data['pairs_count']} pairs")
        else:
            print("❌ Match game creation failed")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        traceback.print_exc()

def main():
    print("🚀 Starting Study Modes Debug...")
    
    token = login_user()
    if not token:
        print("❌ Failed to login")
        return
    
    print("✅ Login successful")
    
    # Get study set ID
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/study-sets", headers=headers)
    if response.status_code == 200:
        data = response.json()
        study_sets = data.get('items', [])
        if study_sets:
            study_set_id = study_sets[0]['id']
            print(f"Using study set ID: {study_set_id}")
            
            debug_test_mode(token, study_set_id)
            debug_match_mode(token, study_set_id)
        else:
            print("❌ No study sets found")
    else:
        print(f"❌ Failed to get study sets: {response.text}")

if __name__ == "__main__":
    main() 