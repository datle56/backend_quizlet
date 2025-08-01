#!/usr/bin/env python3
"""
Script test SRS nhanh - sử dụng endpoint force_next_review để test ngay lập tức
"""

import requests
import json
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

def force_next_review(token, study_set_id, term_id):
    """Force next_review về quá khứ để test ngay lập tức"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/v1/study/test/force-review/{study_set_id}/terms/{term_id}", 
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Force next_review failed: {response.text}")
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

def test_srs_flow():
    """Test SRS flow với 1 term"""
    print("🚀 QUICK SRS TEST")
    print("=" * 50)
    
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
    
    print(f"\nTesting SRS for study_set_id={study_set_id}, term_id={term_id}")
    
    # Step 1: Học term lần đầu (correct)
    print("\n1️⃣  Learning term for the first time (correct)...")
    result = update_term_progress(token, study_set_id, term_id, True)
    if result:
        print(f"✅ Level: {result['familiarity_level']}")
        print(f"   Next review: {result['next_review']}")
        print(f"   Streak: {result['current_streak']}")
    
    # Step 2: Check review terms (should be empty)
    print("\n2️⃣  Checking review terms...")
    review = get_review_terms(token, study_set_id)
    print(f"✅ Terms due for review: {len(review['terms'])}")
    
    # Step 3: Force next_review về quá khứ
    print("\n3️⃣  Forcing next_review to past time...")
    force_result = force_next_review(token, study_set_id, term_id)
    if force_result:
        print(f"✅ {force_result['message']}")
    
    # Step 4: Check review terms again (should have the term)
    print("\n4️⃣  Checking review terms again...")
    review = get_review_terms(token, study_set_id)
    print(f"✅ Terms due for review: {len(review['terms'])}")
    for term in review['terms']:
        print(f"   - Term ID: {term['term_id']}, Level: {term['familiarity_level']}")
    
    # Step 5: Học lại term (should level up)
    print("\n5️⃣  Learning term again (correct)...")
    result = update_term_progress(token, study_set_id, term_id, True)
    if result:
        print(f"✅ Level: {result['familiarity_level']}")
        print(f"   Next review: {result['next_review']}")
        print(f"   Streak: {result['current_streak']}")
    
    # Step 6: Test incorrect answer
    print("\n6️⃣  Testing incorrect answer...")
    result = update_term_progress(token, study_set_id, term_id, False)
    if result:
        print(f"✅ Level: {result['familiarity_level']}")
        print(f"   Next review: {result['next_review']}")
        print(f"   Streak: {result['current_streak']}")
    
    # Show final progress
    progress = get_study_progress(token, study_set_id)
    print_progress(progress)
    
    print("\n🎉 Quick SRS test completed!")

if __name__ == "__main__":
    test_srs_flow() 