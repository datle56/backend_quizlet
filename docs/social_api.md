# Social API Documentation

This document describes the social features API endpoints for favorites and ratings functionality.

## Base URL
```
/api/v1/social
```

## Authentication
All endpoints require authentication using Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Favorites Endpoints

### POST /social/favorites/{study_set_id}
Toggle favorite status for a study set.

**Parameters:**
- `study_set_id` (path): ID of the study set to favorite/unfavorite

**Response:**
```json
{
  "is_favorited": true,
  "favorites_count": 5
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/social/favorites/123" \
  -H "Authorization: Bearer <token>"
```

### GET /social/favorites
Get all favorited study sets for the current user.

**Query Parameters:**
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum number of items to return (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 123,
    "title": "English Vocabulary",
    "description": "Basic English vocabulary",
    "user_id": 1,
    "is_public": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "terms_count": 50,
    "language_from": "en",
    "language_to": "vi",
    "views_count": 100,
    "favorites_count": 5,
    "average_rating": 4.5,
    "favorited_at": "2024-01-01T00:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social/favorites?skip=0&limit=10" \
  -H "Authorization: Bearer <token>"
```

## Ratings Endpoints

### POST /social/ratings/{study_set_id}
Create or update a rating for a study set.

**Parameters:**
- `study_set_id` (path): ID of the study set to rate

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great study set! Very helpful for learning."
}
```

**Response:**
```json
{
  "id": 1,
  "study_set_id": 123,
  "user_id": 1,
  "rating": 5,
  "comment": "Great study set! Very helpful for learning.",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/social/ratings/123" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Great study set! Very helpful for learning."
  }'
```

### GET /social/ratings/{study_set_id}
Get rating summary for a study set.

**Parameters:**
- `study_set_id` (path): ID of the study set

**Response:**
```json
{
  "study_set_id": 123,
  "average_rating": 4.5,
  "total_ratings": 10,
  "rating_distribution": {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 4,
    "5": 3
  },
  "user_rating": 5,
  "user_comment": "Great study set! Very helpful for learning."
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social/ratings/123" \
  -H "Authorization: Bearer <token>"
```

### GET /social/ratings/{study_set_id}/all
Get all ratings for a study set with user information.

**Parameters:**
- `study_set_id` (path): ID of the study set

**Query Parameters:**
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum number of items to return (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "study_set_id": 123,
    "user_id": 1,
    "rating": 5,
    "comment": "Great study set! Very helpful for learning.",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "user": {
      "id": 1,
      "username": "john_doe",
      "full_name": "John Doe",
      "avatar_url": "https://example.com/avatar.jpg"
    }
  }
]
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social/ratings/123/all?skip=0&limit=10" \
  -H "Authorization: Bearer <token>"
```

### DELETE /social/ratings/{study_set_id}
Delete the current user's rating for a study set.

**Parameters:**
- `study_set_id` (path): ID of the study set

**Response:**
- Status: 204 No Content

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/social/ratings/123" \
  -H "Authorization: Bearer <token>"
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Cannot rate your own study set"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Study set not found"
}
```

## Business Rules

1. **Favorites:**
   - Users can favorite/unfavorite any public study set
   - Toggle functionality: if already favorited, removes from favorites; if not favorited, adds to favorites
   - Favorites count is automatically updated on the study set

2. **Ratings:**
   - Users cannot rate their own study sets
   - Rating must be between 1 and 5
   - Users can update their existing ratings
   - Average rating is automatically calculated and updated on the study set
   - Comments are optional

3. **Authentication:**
   - All endpoints require valid authentication token
   - User information is extracted from the token

## Database Schema

### Favorites Table
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    study_set_id INT REFERENCES study_sets(id),
    favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, study_set_id)
);
```

### Ratings Table
```sql
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    study_set_id INT REFERENCES study_sets(id),
    user_id INT REFERENCES users(id),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(study_set_id, user_id)
);
``` 