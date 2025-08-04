#!/usr/bin/env python3
"""
Script test cho Folders API
"""

import requests
import json
from typing import Optional

# Cấu hình
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = None  # Sẽ được set sau khi login


def login(email: str, password: str) -> Optional[str]:
    """Đăng nhập và lấy token"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "string@gmail.com",
        "password": "string"
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Đăng nhập thành công: {email}")
        return token
    else:
        print(f"❌ Đăng nhập thất bại: {response.text}")
        return None


def test_create_folder(token: str, folder_data: dict):
    """Test tạo folder"""
    url = f"{BASE_URL}/folders/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, json=folder_data, headers=headers)
    print(f"📁 Tạo folder: {response.status_code}")
    if response.status_code == 201:
        folder = response.json()
        print(f"✅ Folder tạo thành công: {folder['name']} (ID: {folder['id']})")
        return folder
    else:
        print(f"❌ Lỗi: {response.text}")
        return None


def test_get_my_folders(token: str):
    """Test lấy danh sách folders của user"""
    url = f"{BASE_URL}/folders/user/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"📁 Lấy danh sách folders: {response.status_code}")
    if response.status_code == 200:
        folders = response.json()
        print(f"✅ Có {len(folders)} folders")
        for folder in folders:
            print(f"  - {folder['name']} (ID: {folder['id']}, {folder['study_sets_count']} study sets)")
        return folders
    else:
        print(f"❌ Lỗi: {response.text}")
        return []


def test_get_folder(token: str, folder_id: int):
    """Test lấy chi tiết folder"""
    url = f"{BASE_URL}/folders/{folder_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"📁 Lấy chi tiết folder {folder_id}: {response.status_code}")
    if response.status_code == 200:
        folder = response.json()
        print(f"✅ Folder: {folder['name']} - {folder['description']}")
        return folder
    else:
        print(f"❌ Lỗi: {response.text}")
        return None


def test_update_folder(token: str, folder_id: int, update_data: dict):
    """Test cập nhật folder"""
    url = f"{BASE_URL}/folders/{folder_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.put(url, json=update_data, headers=headers)
    print(f"📁 Cập nhật folder {folder_id}: {response.status_code}")
    if response.status_code == 200:
        folder = response.json()
        print(f"✅ Cập nhật thành công: {folder['name']}")
        return folder
    else:
        print(f"❌ Lỗi: {response.text}")
        return None


def test_add_study_set_to_folder(token: str, folder_id: int, study_set_id: int):
    """Test thêm study set vào folder"""
    url = f"{BASE_URL}/folders/{folder_id}/study-sets/{study_set_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    print(f"📁 Thêm study set {study_set_id} vào folder {folder_id}: {response.status_code}")
    if response.status_code == 201:
        print("✅ Thêm study set thành công")
        return True
    else:
        print(f"❌ Lỗi: {response.text}")
        return False


def test_get_study_sets_in_folder(token: str, folder_id: int):
    """Test lấy study sets trong folder"""
    url = f"{BASE_URL}/folders/{folder_id}/study-sets"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"📁 Lấy study sets trong folder {folder_id}: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        folder = data["folder"]
        study_sets = data["study_sets"]
        print(f"✅ Folder: {folder['name']} - {len(study_sets)} study sets")
        for study_set in study_sets:
            print(f"  - {study_set['title']} ({study_set['terms_count']} terms)")
        return study_sets
    else:
        print(f"❌ Lỗi: {response.text}")
        return []


def test_get_colors_and_icons(token: str):
    """Test lấy colors và icons"""
    url = f"{BASE_URL}/folders/colors-icons"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"📁 Lấy colors và icons: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Có {len(data['colors'])} colors và {len(data['icons'])} icons")
        print(f"  Colors: {data['colors'][:5]}...")  # Hiển thị 5 colors đầu
        print(f"  Icons: {data['icons'][:5]}...")    # Hiển thị 5 icons đầu
        return data
    else:
        print(f"❌ Lỗi: {response.text}")
        return None


def test_move_study_set_to_folder(token: str, study_set_id: int, folder_id: int):
    """Test di chuyển study set sang folder khác"""
    url = f"{BASE_URL}/study-sets/{study_set_id}/move-to-folder/{folder_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.put(url, headers=headers)
    print(f"📁 Di chuyển study set {study_set_id} sang folder {folder_id}: {response.status_code}")
    if response.status_code == 200:
        print("✅ Di chuyển study set thành công")
        return True
    else:
        print(f"❌ Lỗi: {response.text}")
        return False


def test_reorder_folders(token: str, folder_ids: list):
    """Test sắp xếp lại folders"""
    url = f"{BASE_URL}/folders/reorder"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"folder_ids": folder_ids}
    
    response = requests.put(url, json=data, headers=headers)
    print(f"📁 Sắp xếp lại folders: {response.status_code}")
    if response.status_code == 200:
        folders = response.json()
        print(f"✅ Sắp xếp thành công {len(folders)} folders")
        return folders
    else:
        print(f"❌ Lỗi: {response.text}")
        return []


def main():
    """Test chính"""
    global TOKEN
    
    print("🚀 Bắt đầu test Folders API")
    print("=" * 50)
    
    # 1. Đăng nhập
    TOKEN = login("test@example.com", "password123")
    if not TOKEN:
        print("❌ Không thể đăng nhập, dừng test")
        return
    
    print("\n" + "=" * 50)
    
    # 2. Test tạo folders
    folders_created = []
    
    folder_data_1 = {
        "name": "Tiếng Anh",
        "description": "Các study sets về tiếng Anh",
        "color": "#3B82F6",
        "icon": "language"
    }
    
    folder_data_2 = {
        "name": "Toán học",
        "description": "Các study sets về toán học",
        "color": "#10B981",
        "icon": "math"
    }
    
    folder_data_3 = {
        "name": "Khoa học",
        "description": "Các study sets về khoa học",
        "color": "#F59E0B",
        "icon": "science"
    }
    
    folder1 = test_create_folder(TOKEN, folder_data_1)
    if folder1:
        folders_created.append(folder1)
    
    folder2 = test_create_folder(TOKEN, folder_data_2)
    if folder2:
        folders_created.append(folder2)
    
    folder3 = test_create_folder(TOKEN, folder_data_3)
    if folder3:
        folders_created.append(folder3)
    
    print("\n" + "=" * 50)
    
    # 3. Test lấy danh sách folders
    test_get_my_folders(TOKEN)
    
    print("\n" + "=" * 50)
    
    # 4. Test lấy chi tiết folder
    if folders_created:
        test_get_folder(TOKEN, folders_created[0]["id"])
    
    print("\n" + "=" * 50)
    
    # 5. Test cập nhật folder
    if folders_created:
        update_data = {
            "name": "Tiếng Anh Nâng cao",
            "description": "Các study sets tiếng Anh nâng cao",
            "color": "#8B5CF6"
        }
        test_update_folder(TOKEN, folders_created[0]["id"], update_data)
    
    print("\n" + "=" * 50)
    
    # 6. Test lấy colors và icons
    test_get_colors_and_icons(TOKEN)
    
    print("\n" + "=" * 50)
    
    # 7. Test sắp xếp lại folders
    if len(folders_created) >= 2:
        folder_ids = [folder["id"] for folder in folders_created]
        # Đảo ngược thứ tự
        folder_ids.reverse()
        test_reorder_folders(TOKEN, folder_ids)
    
    print("\n" + "=" * 50)
    print("✅ Hoàn thành test Folders API")


if __name__ == "__main__":
    main() 