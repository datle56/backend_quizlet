#!/usr/bin/env python3
"""
Test script for classes API with subject field
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_create_class_with_subject():
    """Test creating a class with subject field"""
    url = f"{BASE_URL}/api/v1/classes/"
    
    # Test data
    class_data = {
        "name": "Tiếng Anh 12A1",
        "description": "Mô tả về lớp học này",
        "subject": "Tiếng Anh"  # Trường môn học mới
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_TOKEN_HERE"  # Cần thay bằng token thực
    }
    
    try:
        response = requests.post(url, json=class_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")

def test_update_class_with_subject():
    """Test updating a class with subject field"""
    class_id = 1  # Thay bằng ID thực
    url = f"{BASE_URL}/api/v1/classes/{class_id}"
    
    # Test data
    update_data = {
        "name": "Tiếng Anh 12A1 - Cập nhật",
        "description": "Mô tả cập nhật về lớp học này",
        "subject": "Tiếng Anh - Nâng cao"  # Cập nhật môn học
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_TOKEN_HERE"  # Cần thay bằng token thực
    }
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Classes API with subject field...")
    print("\n1. Testing CREATE class with subject:")
    test_create_class_with_subject()
    
    print("\n2. Testing UPDATE class with subject:")
    test_update_class_with_subject() 