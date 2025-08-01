#!/usr/bin/env python3
"""
Script to manually test the Study Sets API endpoints.
Run this after starting the server.
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"


def login(username: str, password: str) -> Optional[str]:
    """Login and get access token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login successful for user: {username}")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None


def test_study_sets_api():
    """Test Study Sets API endpoints"""
    print("🧪 Testing Study Sets API...")
    
    # Login
    token = login("testuser", "testpassword")
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Create Study Set
    print("\n1. Creating a new study set...")
    study_set_data = {
        "title": "English to Vietnamese Basic Phrases",
        "description": "Common phrases for beginners",
        "is_public": True,
        "language_from": "en",
        "language_to": "vi"
    }
    
    response = requests.post(f"{BASE_URL}/study-sets/", json=study_set_data, headers=headers)
    if response.status_code == 201:
        study_set = response.json()
        study_set_id = study_set["id"]
        print(f"✅ Study set created with ID: {study_set_id}")
        print(f"   Title: {study_set['title']}")
        print(f"   Terms count: {study_set['terms_count']}")
    else:
        print(f"❌ Failed to create study set: {response.text}")
        return
    
    # Test 2: Add Terms
    print("\n2. Adding terms to the study set...")
    terms_data = {
        "terms": [
            {"term": "Hello", "definition": "Xin chào"},
            {"term": "Goodbye", "definition": "Tạm biệt"},
            {"term": "Thank you", "definition": "Cảm ơn"},
            {"term": "Please", "definition": "Làm ơn"},
            {"term": "Sorry", "definition": "Xin lỗi"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/study-sets/{study_set_id}/terms/bulk", 
                           json=terms_data, headers=headers)
    if response.status_code == 201:
        terms = response.json()
        print(f"✅ Added {len(terms)} terms")
        for term in terms:
            print(f"   - {term['term']}: {term['definition']}")
    else:
        print(f"❌ Failed to add terms: {response.text}")
    
    # Test 3: Get Study Set Details
    print("\n3. Getting study set details...")
    response = requests.get(f"{BASE_URL}/study-sets/{study_set_id}", headers=headers)
    if response.status_code == 200:
        study_set_detail = response.json()
        print(f"✅ Study set details retrieved")
        print(f"   Title: {study_set_detail['title']}")
        print(f"   Terms count: {study_set_detail['terms_count']}")
        print(f"   Views: {study_set_detail['views_count']}")
        print(f"   Terms: {len(study_set_detail['terms'])}")
    else:
        print(f"❌ Failed to get study set details: {response.text}")
    
    # Test 4: Search Study Sets
    print("\n4. Searching study sets...")
    response = requests.get(f"{BASE_URL}/study-sets/?search=English&size=5", headers=headers)
    if response.status_code == 200:
        search_results = response.json()
        print(f"✅ Found {search_results['total']} study sets")
        print(f"   Page {search_results['page']} of {search_results['pages']}")
        for item in search_results['items']:
            print(f"   - {item['title']} (by {item['user']['username']})")
    else:
        print(f"❌ Failed to search study sets: {response.text}")
    
    # Test 5: Update Study Set
    print("\n5. Updating study set...")
    update_data = {
        "title": "English to Vietnamese Basic Phrases (Updated)",
        "description": "Common phrases for beginners - Updated description"
    }
    
    response = requests.put(f"{BASE_URL}/study-sets/{study_set_id}", 
                          json=update_data, headers=headers)
    if response.status_code == 200:
        updated_study_set = response.json()
        print(f"✅ Study set updated")
        print(f"   New title: {updated_study_set['title']}")
        print(f"   New description: {updated_study_set['description']}")
    else:
        print(f"❌ Failed to update study set: {response.text}")
    
    # Test 6: Get My Study Sets
    print("\n6. Getting my study sets...")
    response = requests.get(f"{BASE_URL}/study-sets/user/me", headers=headers)
    if response.status_code == 200:
        my_study_sets = response.json()
        print(f"✅ Found {len(my_study_sets)} study sets")
        for study_set in my_study_sets:
            print(f"   - {study_set['title']} ({study_set['terms_count']} terms)")
    else:
        print(f"❌ Failed to get my study sets: {response.text}")
    
    print("\n🎉 Study Sets API test completed!")


if __name__ == "__main__":
    test_study_sets_api() 