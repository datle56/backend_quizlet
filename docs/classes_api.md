# Classes & Collaboration API Documentation

## Overview

The Classes & Collaboration API provides functionality for teachers to create and manage classes, assign study sets, and track student progress. Students can join classes using join codes and access assigned study materials.

## Base URL

```
/api/v1/classes
```

## Authentication

All endpoints require authentication. Include the Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Create Class

**POST** `/api/v1/classes/`

Creates a new class. Only authenticated users can create classes (they become the teacher).

**Request Body:**
```json
{
  "name": "Advanced Mathematics",
  "description": "A comprehensive course covering advanced mathematical concepts"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Advanced Mathematics",
  "description": "A comprehensive course covering advanced mathematical concepts",
  "teacher_id": 123,
  "join_code": "ABC123",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### 2. Get User Classes

**GET** `/api/v1/classes/`

Returns all classes where the authenticated user is a member (either as teacher or student).

**Response:**
```json
[
  {
    "id": 1,
    "name": "Advanced Mathematics",
    "description": "A comprehensive course covering advanced mathematical concepts",
    "teacher_id": 123,
    "join_code": "ABC123",
    "created_at": "2024-01-15T10:30:00Z",
    "is_active": true
  }
]
```

### 3. Join Class

**POST** `/api/v1/classes/join`

Joins a class using a join code.

**Request Body:**
```json
{
  "join_code": "ABC123"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Advanced Mathematics",
  "description": "A comprehensive course covering advanced mathematical concepts",
  "teacher_id": 123,
  "join_code": "ABC123",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### 4. Get Class Details

**GET** `/api/v1/classes/{class_id}`

Returns detailed information about a class, including members and assignments. Only class members can access this endpoint.

**Response:**
```json
{
  "id": 1,
  "name": "Advanced Mathematics",
  "description": "A comprehensive course covering advanced mathematical concepts",
  "teacher_id": 123,
  "join_code": "ABC123",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true,
  "teacher": {
    "id": 123,
    "username": "teacher_john",
    "full_name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg"
  },
  "members": [
    {
      "id": 1,
      "class_id": 1,
      "user_id": 123,
      "role": "teacher",
      "joined_at": "2024-01-15T10:30:00Z",
      "user": {
        "id": 123,
        "username": "teacher_john",
        "full_name": "John Doe",
        "avatar_url": "https://example.com/avatar.jpg"
      }
    },
    {
      "id": 2,
      "class_id": 1,
      "user_id": 456,
      "role": "student",
      "joined_at": "2024-01-15T11:00:00Z",
      "user": {
        "id": 456,
        "username": "student_jane",
        "full_name": "Jane Smith",
        "avatar_url": "https://example.com/avatar2.jpg"
      }
    }
  ],
  "study_sets": [
    {
      "id": 1,
      "class_id": 1,
      "study_set_id": 789,
      "assigned_at": "2024-01-15T12:00:00Z",
      "due_date": "2024-01-20T23:59:59Z",
      "is_optional": false,
      "study_set": {
        "id": 789,
        "title": "Calculus Fundamentals",
        "description": "Basic calculus concepts",
        "terms_count": 50
      }
    }
  ]
}
```

### 5. Get Class Members

**GET** `/api/v1/classes/{class_id}/members`

Returns all members of a class. Only class members can access this endpoint.

**Response:**
```json
[
  {
    "id": 1,
    "class_id": 1,
    "user_id": 123,
    "role": "teacher",
    "joined_at": "2024-01-15T10:30:00Z",
    "user": {
      "id": 123,
      "username": "teacher_john",
      "full_name": "John Doe",
      "avatar_url": "https://example.com/avatar.jpg"
    }
  },
  {
    "id": 2,
    "class_id": 1,
    "user_id": 456,
    "role": "student",
    "joined_at": "2024-01-15T11:00:00Z",
    "user": {
      "id": 456,
      "username": "student_jane",
      "full_name": "Jane Smith",
      "avatar_url": "https://example.com/avatar2.jpg"
    }
  }
]
```

### 6. Assign Study Set to Class

**POST** `/api/v1/classes/{class_id}/study-sets`

Assigns a study set to a class. Only the class teacher can assign study sets.

**Request Body:**
```json
{
  "study_set_id": 789,
  "due_date": "2024-01-20T23:59:59Z",
  "is_optional": false
}
```

**Response:**
```json
{
  "id": 1,
  "class_id": 1,
  "study_set_id": 789,
  "assigned_at": "2024-01-15T12:00:00Z",
  "due_date": "2024-01-20T23:59:59Z",
  "is_optional": false
}
```

### 7. Get Class Assignments

**GET** `/api/v1/classes/{class_id}/assignments`

Returns all study sets assigned to a class. Only class members can access this endpoint.

**Response:**
```json
[
  {
    "id": 1,
    "class_id": 1,
    "study_set_id": 789,
    "assigned_at": "2024-01-15T12:00:00Z",
    "due_date": "2024-01-20T23:59:59Z",
    "is_optional": false,
    "study_set": {
      "id": 789,
      "title": "Calculus Fundamentals",
      "description": "Basic calculus concepts",
      "terms_count": 50
    }
  }
]
```

### 8. Remove Assignment

**DELETE** `/api/v1/classes/{class_id}/assignments/{assignment_id}`

Removes a study set assignment from a class. Only the class teacher can remove assignments.

**Response:** 204 No Content

### 9. Get Class Progress

**GET** `/api/v1/classes/{class_id}/progress`

Returns progress information for all students in a class. Only the class teacher can access this endpoint.

**Response:**
```json
[
  {
    "user_id": 456,
    "username": "student_jane",
    "full_name": "Jane Smith",
    "total_assignments": 3,
    "completed_assignments": 2,
    "average_score": 85.5,
    "last_activity": "2024-01-18T15:30:00Z"
  },
  {
    "user_id": 789,
    "username": "student_bob",
    "full_name": "Bob Wilson",
    "total_assignments": 3,
    "completed_assignments": 1,
    "average_score": 72.0,
    "last_activity": "2024-01-17T09:15:00Z"
  }
]
```

### 10. Update Class

**PUT** `/api/v1/classes/{class_id}`

Updates class information. Only the class teacher can update the class.

**Request Body:**
```json
{
  "name": "Advanced Mathematics - Updated",
  "description": "Updated course description",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Advanced Mathematics - Updated",
  "description": "Updated course description",
  "teacher_id": 123,
  "join_code": "ABC123",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### 11. Delete Class

**DELETE** `/api/v1/classes/{class_id}`

Deletes a class (soft delete by setting is_active to false). Only the class teacher can delete the class.

**Response:** 204 No Content

## Error Responses

### 400 Bad Request
```json
{
  "detail": "User is already a member of this class"
}
```

### 403 Forbidden
```json
{
  "detail": "You are not a member of this class"
}
```

### 404 Not Found
```json
{
  "detail": "Class not found"
}
```

## Data Models

### Class
- `id`: Unique identifier
- `name`: Class name
- `description`: Class description
- `teacher_id`: ID of the teacher who created the class
- `join_code`: Unique 6-character code for joining the class
- `created_at`: Creation timestamp
- `is_active`: Whether the class is active

### ClassMember
- `id`: Unique identifier
- `class_id`: ID of the class
- `user_id`: ID of the user
- `role`: Either "teacher" or "student"
- `joined_at`: When the user joined the class

### ClassStudySet
- `id`: Unique identifier
- `class_id`: ID of the class
- `study_set_id`: ID of the study set
- `assigned_at`: When the study set was assigned
- `due_date`: Optional due date for the assignment
- `is_optional`: Whether the assignment is optional

## Usage Examples

### Creating and Managing a Class

1. **Create a class:**
```bash
curl -X POST "http://localhost:8000/api/v1/classes/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Physics 101",
    "description": "Introduction to physics concepts"
  }'
```

2. **Share the join code with students**

3. **Students join the class:**
```bash
curl -X POST "http://localhost:8000/api/v1/classes/join" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "join_code": "ABC123"
  }'
```

4. **Assign study sets:**
```bash
curl -X POST "http://localhost:8000/api/v1/classes/1/study-sets" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "study_set_id": 123,
    "due_date": "2024-01-25T23:59:59Z",
    "is_optional": false
  }'
```

5. **Track student progress:**
```bash
curl -X GET "http://localhost:8000/api/v1/classes/1/progress" \
  -H "Authorization: Bearer <token>"
```

## Notes

- Join codes are automatically generated as 6-character alphanumeric strings
- Classes support soft deletion (setting is_active to false)
- Only teachers can assign/remove study sets and view progress
- All class members can view assignments and other class information
- Progress tracking is based on study sessions completed by students 