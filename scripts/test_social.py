#!/usr/bin/env python3
"""
Test script for social functionality (favorites and ratings)
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test user credentials
TEST_USER = {
    "username": "string",
    "email": "test@example.com",
    "password": "string",
    "full_name": "Test User"
}

def get_auth_token() -> str:
    """Get authentication token for testing"""
    # First, try to register the user
    register_url = f"{BASE_URL}/auth/register"
    register_data = TEST_USER.copy()
    
    try:
        response = requests.post(register_url, json=register_data)
        print(f"Register response: {response.status_code}")
        if response.status_code == 201:
            print("✅ User registered successfully")
        elif response.status_code == 400:
            print("ℹ️ User might already exist")
        else:
            print(f"❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Try to login
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            return token_data["access_token"]
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def create_test_study_set(token: str) -> int:
    """Create a test study set for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    
    study_set_data = {
        "title": "Test Study Set for Social Features",
        "description": "A test study set to test favorites and ratings",
        "is_public": True,
        "language_from": "en",
        "language_to": "vi"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/study-sets/",
            json=study_set_data,
            headers=headers
        )
        
        if response.status_code == 201:
            study_set = response.json()
            print(f"✅ Test study set created with ID: {study_set['id']}")
            return study_set['id']
        else:
            print(f"❌ Failed to create study set: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating study set: {e}")
        return None

def test_favorites(token: str, study_set_id: int):
    """Test favorites functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Favorites ===")
    
    # Test 1: Add to favorites
    try:
        response = requests.post(
            f"{BASE_URL}/social/favorites/{study_set_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added to favorites: {result}")
        else:
            print(f"❌ Failed to add to favorites: {response.text}")
    except Exception as e:
        print(f"❌ Error adding to favorites: {e}")
    
    # Test 2: Get user favorites
    try:
        response = requests.get(
            f"{BASE_URL}/social/favorites",
            headers=headers
        )
        
        if response.status_code == 200:
            favorites = response.json()
            print(f"✅ Retrieved {len(favorites)} favorites")
            if favorites:
                print(f"First favorite: {favorites[0]['title']}")
        else:
            print(f"❌ Failed to get favorites: {response.text}")
    except Exception as e:
        print(f"❌ Error getting favorites: {e}")
    
    # Test 3: Remove from favorites (toggle)
    try:
        response = requests.post(
            f"{BASE_URL}/social/favorites/{study_set_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Removed from favorites: {result}")
        else:
            print(f"❌ Failed to remove from favorites: {response.text}")
    except Exception as e:
        print(f"❌ Error removing from favorites: {e}")

def test_ratings(token: str, study_set_id: int):
    """Test ratings functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Ratings ===")
    
    # Test 1: Create a rating
    rating_data = {
        "rating": 5,
        "comment": "Great study set! Very helpful for learning."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/social/ratings/{study_set_id}",
            json=rating_data,
            headers=headers
        )
        
        if response.status_code == 200:
            rating = response.json()
            print(f"✅ Rating created: {rating}")
        else:
            print(f"❌ Failed to create rating: {response.text}")
    except Exception as e:
        print(f"❌ Error creating rating: {e}")
    
    # Test 2: Get rating summary
    try:
        response = requests.get(
            f"{BASE_URL}/social/ratings/{study_set_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Rating summary: {summary}")
        else:
            print(f"❌ Failed to get rating summary: {response.text}")
    except Exception as e:
        print(f"❌ Error getting rating summary: {e}")
    
    # Test 3: Get all ratings
    try:
        response = requests.get(
            f"{BASE_URL}/social/ratings/{study_set_id}/all",
            headers=headers
        )
        
        if response.status_code == 200:
            ratings = response.json()
            print(f"✅ Retrieved {len(ratings)} ratings")
            if ratings:
                print(f"First rating: {ratings[0]}")
        else:
            print(f"❌ Failed to get all ratings: {response.text}")
    except Exception as e:
        print(f"❌ Error getting all ratings: {e}")
    
    # Test 4: Update rating
    updated_rating_data = {
        "rating": 4,
        "comment": "Updated comment: Still good but could be better."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/social/ratings/{study_set_id}",
            json=updated_rating_data,
            headers=headers
        )
        
        if response.status_code == 200:
            rating = response.json()
            print(f"✅ Rating updated: {rating}")
        else:
            print(f"❌ Failed to update rating: {response.text}")
    except Exception as e:
        print(f"❌ Error updating rating: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Social Features (Favorites & Ratings)")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Create a test study set
    study_set_id = 1
    if not study_set_id:
        print("❌ Cannot proceed without a test study set")
        return
    
    # Test favorites
    test_favorites(token, study_set_id)
    
    # Test ratings
    test_ratings(token, study_set_id)
    
    print("\n✅ Social features testing completed!")

if __name__ == "__main__":
    main() 