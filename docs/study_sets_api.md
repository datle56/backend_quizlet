# Study Sets API Documentation

## Overview

The Study Sets API provides comprehensive functionality for managing study sets (flashcard collections) and their terms. This is the core feature of the Quizlet application.

## Authentication

All endpoints require authentication using JWT Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Study Sets Endpoints

### 1. Create Study Set

**POST** `/api/v1/study-sets/`

Creates a new study set for the authenticated user.

**Request Body:**
```json
{
  "title": "English to Vietnamese Basic Phrases",
  "description": "Common phrases for beginners",
  "is_public": true,
  "language_from": "en",
  "language_to": "vi"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "English to Vietnamese Basic Phrases",
  "description": "Common phrases for beginners",
  "is_public": true,
  "language_from": "en",
  "language_to": "vi",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "terms_count": 0,
  "views_count": 0,
  "favorites_count": 0,
  "average_rating": 0.0,
  "user": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "avatar_url": null
  }
}
```

### 2. Get Study Set Details

**GET** `/api/v1/study-sets/{study_set_id}`

Retrieves detailed information about a study set, including all its terms.

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "English to Vietnamese Basic Phrases",
  "description": "Common phrases for beginners",
  "is_public": true,
  "language_from": "en",
  "language_to": "vi",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "terms_count": 5,
  "views_count": 1,
  "favorites_count": 0,
  "average_rating": 0.0,
  "user": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "avatar_url": null
  },
  "terms": [
    {
      "id": 1,
      "term": "Hello",
      "definition": "Xin chào",
      "image_url": null,
      "audio_url": null,
      "study_set_id": 1,
      "position": 1,
      "created_at": "2024-01-15T10:35:00Z",
      "updated_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

### 3. Update Study Set

**PUT** `/api/v1/study-sets/{study_set_id}`

Updates a study set. Only the owner can update their study sets.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "is_public": false
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated description",
  "is_public": false,
  "language_from": "en",
  "language_to": "vi",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "terms_count": 5,
  "views_count": 1,
  "favorites_count": 0,
  "average_rating": 0.0,
  "user": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "avatar_url": null
  }
}
```

### 4. Delete Study Set

**DELETE** `/api/v1/study-sets/{study_set_id}`

Deletes a study set (soft delete by setting is_public to false).

**Response (204 No Content)**

### 5. Search Study Sets

**GET** `/api/v1/study-sets/`

Searches and filters public study sets with pagination.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `size` (int, default: 10, max: 100): Items per page
- `search` (string, optional): Search term for title/description
- `language_from` (string, optional): Filter by source language
- `language_to` (string, optional): Filter by target language
- `user_id` (int, optional): Filter by user ID
- `min_rating` (float, optional): Minimum rating filter
- `sort_by` (string, default: "created_at"): Sort field
- `sort_order` (string, default: "desc"): Sort order (asc/desc)

**Example Request:**
```
GET /api/v1/study-sets/?search=English&language_from=en&page=1&size=10
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "English to Vietnamese Basic Phrases",
      "description": "Common phrases for beginners",
      "user_id": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "terms_count": 5,
      "views_count": 10,
      "favorites_count": 2,
      "average_rating": 4.5,
      "language_from": "en",
      "language_to": "vi",
      "is_public": true,
      "user": {
        "id": 1,
        "username": "john_doe",
        "full_name": "John Doe",
        "avatar_url": null
      }
    }
  ],
  "total": 25,
  "page": 1,
  "size": 10,
  "pages": 3
}
```

### 6. Get My Study Sets

**GET** `/api/v1/study-sets/user/me`

Retrieves all study sets owned by the authenticated user.

**Query Parameters:**
- `include_private` (bool, default: true): Include private study sets

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "My Private Study Set",
    "description": "Private study set",
    "is_public": false,
    "language_from": "en",
    "language_to": "vi",
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "terms_count": 5,
    "views_count": 0,
    "favorites_count": 0,
    "average_rating": 0.0,
    "user": {
      "id": 1,
      "username": "john_doe",
      "full_name": "John Doe",
      "avatar_url": null
    }
  }
]
```

## Terms Endpoints

### 1. Create Term

**POST** `/api/v1/study-sets/{study_set_id}/terms/`

Adds a new term to a study set.

**Request Body:**
```json
{
  "term": "Hello",
  "definition": "Xin chào",
  "image_url": "https://example.com/image.jpg",
  "audio_url": "https://example.com/audio.mp3"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "term": "Hello",
  "definition": "Xin chào",
  "image_url": "https://example.com/image.jpg",
  "audio_url": "https://example.com/audio.mp3",
  "study_set_id": 1,
  "position": 1,
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 2. Get Terms

**GET** `/api/v1/study-sets/{study_set_id}/terms/`

Retrieves all terms for a study set, ordered by position.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "term": "Hello",
    "definition": "Xin chào",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 1,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  },
  {
    "id": 2,
    "term": "Goodbye",
    "definition": "Tạm biệt",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 2,
    "created_at": "2024-01-15T10:36:00Z",
    "updated_at": "2024-01-15T10:36:00Z"
  }
]
```

### 3. Update Term

**PUT** `/api/v1/study-sets/{study_set_id}/terms/{term_id}`

Updates a specific term.

**Request Body:**
```json
{
  "term": "Updated Term",
  "definition": "Updated Definition"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "term": "Updated Term",
  "definition": "Updated Definition",
  "image_url": null,
  "audio_url": null,
  "study_set_id": 1,
  "position": 1,
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### 4. Delete Term

**DELETE** `/api/v1/study-sets/{study_set_id}/terms/{term_id}`

Deletes a specific term.

**Response (204 No Content)**

### 5. Bulk Create Terms

**POST** `/api/v1/study-sets/{study_set_id}/terms/bulk`

Creates multiple terms at once.

**Request Body:**
```json
{
  "terms": [
    {
      "term": "Hello",
      "definition": "Xin chào"
    },
    {
      "term": "Goodbye",
      "definition": "Tạm biệt"
    },
    {
      "term": "Thank you",
      "definition": "Cảm ơn"
    }
  ]
}
```

**Response (201 Created):**
```json
[
  {
    "id": 1,
    "term": "Hello",
    "definition": "Xin chào",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 1,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  },
  {
    "id": 2,
    "term": "Goodbye",
    "definition": "Tạm biệt",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 2,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  },
  {
    "id": 3,
    "term": "Thank you",
    "definition": "Cảm ơn",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 3,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
]
```

### 6. Reorder Terms

**PUT** `/api/v1/study-sets/{study_set_id}/terms/reorder`

Reorders terms by updating their positions.

**Request Body:**
```json
{
  "term_ids": [3, 1, 2]
}
```

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "term": "Thank you",
    "definition": "Cảm ơn",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 1,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  {
    "id": 1,
    "term": "Hello",
    "definition": "Xin chào",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 2,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  {
    "id": 2,
    "term": "Goodbye",
    "definition": "Tạm biệt",
    "image_url": null,
    "audio_url": null,
    "study_set_id": 1,
    "position": 3,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
]
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error"
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
  "detail": "Study set not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Features

### ✅ Implemented Features

1. **Study Sets CRUD Operations**
   - Create, read, update, delete study sets
   - Soft delete (sets is_public to false)
   - Version history tracking

2. **Terms Management**
   - Add, update, delete individual terms
   - Bulk create terms
   - Reorder terms by position
   - Automatic position management

3. **Search and Filtering**
   - Full-text search in title and description
   - Filter by language, user, rating
   - Pagination support
   - Multiple sorting options

4. **Access Control**
   - Only owners can edit/delete their study sets
   - Private study sets are only visible to owners
   - Public study sets are visible to everyone

5. **Statistics Tracking**
   - View count tracking
   - Terms count management
   - User's total study sets created

### 🔮 Future Enhancements

1. **File Upload Support**
   - Image upload for terms
   - Audio upload for pronunciation

2. **Advanced Search**
   - Search within terms
   - Fuzzy matching
   - Advanced filters

3. **Collaboration Features**
   - Share study sets
   - Collaborative editing
   - Comments and ratings

4. **Import/Export**
   - CSV import/export
   - JSON import/export
   - Integration with other platforms

## Database Schema

### StudySets Table
- `id`: Primary key
- `title`: Study set title (required)
- `description`: Optional description
- `user_id`: Owner (foreign key to users)
- `is_public`: Visibility flag
- `language_from`: Source language code
- `language_to`: Target language code
- `terms_count`: Number of terms
- `views_count`: View counter
- `favorites_count`: Favorites counter
- `average_rating`: Average rating
- `created_at`, `updated_at`: Timestamps

### Terms Table
- `id`: Primary key
- `study_set_id`: Parent study set
- `term`: The term/word
- `definition`: Definition/translation
- `image_url`: Optional image URL
- `audio_url`: Optional audio URL
- `position`: Order in study set
- `created_at`, `updated_at`: Timestamps

### StudySetVersions Table
- `id`: Primary key
- `study_set_id`: Parent study set
- `version_number`: Version number
- `title`: Title at this version
- `description`: Description at this version
- `user_id`: User who made the change
- `changes_summary`: Summary of changes
- `created_at`: When version was created 

