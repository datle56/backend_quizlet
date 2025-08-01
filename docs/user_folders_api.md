# User Profile & Folders Management API Documentation

## Overview
This document describes the API endpoints for user profile management and folder organization features.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. User Profile Management

### 1.1 Get Current User Information
**GET** `/users/me`

Returns the current authenticated user's profile information.

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "is_premium": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_active_at": "2024-01-15T10:30:00Z",
  "total_study_sets_created": 5,
  "total_terms_learned": 150
}
```

### 1.2 Update Current User Profile
**PUT** `/users/me`

Update the current user's profile information.

**Request Body:**
```json
{
  "full_name": "John Doe Updated",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "email": "john.updated@example.com",
  "password": "newpassword123"
}
```

**Response:** Same as GET `/users/me`

### 1.3 Get User Statistics
**GET** `/users/me/statistics`

Returns learning statistics for the current user.

**Response:**
```json
{
  "total_study_sets_created": 5,
  "total_terms_learned": 150,
  "total_folders": 3,
  "study_streak_days": 7,
  "last_study_date": "2024-01-15T10:30:00Z",
  "recent_activities": [
    {
      "type": "study_session",
      "study_set_title": "Basic Vocabulary",
      "score": 85.5,
      "date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 1.4 Get User's Study Sets
**GET** `/study-sets/user/me`

Returns all study sets created by the current user.

**Query Parameters:**
- `include_private` (boolean, default: true): Include private study sets

**Response:**
```json
[
  {
    "id": 1,
    "title": "Basic Vocabulary",
    "description": "Essential words for beginners",
    "user_id": 1,
    "is_public": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "terms_count": 50,
    "language_from": "en",
    "language_to": "es",
    "views_count": 120,
    "favorites_count": 5,
    "average_rating": 4.5
  }
]
```

---

## 2. Folders Management

### 2.1 Create New Folder
**POST** `/folders/`

Create a new folder for organizing study sets.

**Request Body:**
```json
{
  "name": "Spanish Vocabulary"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Spanish Vocabulary",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "study_sets_count": 0
}
```

### 2.2 Get User's Folders
**GET** `/folders/`

Returns all folders created by the current user.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Spanish Vocabulary",
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "study_sets_count": 3
  },
  {
    "id": 2,
    "name": "Math Formulas",
    "user_id": 1,
    "created_at": "2024-01-14T15:20:00Z",
    "updated_at": "2024-01-14T15:20:00Z",
    "study_sets_count": 2
  }
]
```

### 2.3 Get Folder with Study Sets
**GET** `/folders/{folder_id}`

Returns a specific folder with all its study sets.

**Response:**
```json
{
  "id": 1,
  "name": "Spanish Vocabulary",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "study_sets_count": 3,
  "study_sets": [
    {
      "id": 1,
      "title": "Basic Vocabulary",
      "description": "Essential words for beginners",
      "user_id": 1,
      "is_public": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "terms_count": 50,
      "language_from": "en",
      "language_to": "es",
      "views_count": 120,
      "favorites_count": 5,
      "average_rating": 4.5
    }
  ]
}
```

### 2.4 Update Folder
**PUT** `/folders/{folder_id}`

Update folder name.

**Request Body:**
```json
{
  "name": "Advanced Spanish Vocabulary"
}
```

**Response:** Same as folder creation response

### 2.5 Delete Folder
**DELETE** `/folders/{folder_id}`

Delete a folder and all its study set associations.

**Response:** 204 No Content

### 2.6 Add Study Set to Folder
**POST** `/folders/{folder_id}/study-sets`

Add a study set to a folder.

**Request Body:**
```json
{
  "study_set_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "folder_id": 1,
  "study_set_id": 1,
  "added_at": "2024-01-15T10:30:00Z"
}
```

### 2.7 Remove Study Set from Folder
**DELETE** `/folders/{folder_id}/study-sets/{study_set_id}`

Remove a study set from a folder.

**Response:** 204 No Content

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Study set already in folder"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Folder not found"
}
```

---

## Examples

### Creating a folder and adding study sets

1. **Create folder:**
```bash
curl -X POST "http://localhost:8000/api/v1/folders/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Study Sets"}'
```

2. **Add study set to folder:**
```bash
curl -X POST "http://localhost:8000/api/v1/folders/1/study-sets" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"study_set_id": 1}'
```

3. **Get folder with study sets:**
```bash
curl -X GET "http://localhost:8000/api/v1/folders/1" \
  -H "Authorization: Bearer <token>"
```

### Getting user statistics

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/statistics" \
  -H "Authorization: Bearer <token>"
```

---

## Notes

- All folder operations require authentication
- Users can only access their own folders
- Study sets must belong to the user to be added to folders
- Deleting a folder removes all study set associations but doesn't delete the study sets themselves
- The statistics endpoint provides basic metrics; advanced analytics can be added later 