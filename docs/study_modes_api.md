# Study Modes API Documentation

## Overview

The Study Modes API provides comprehensive functionality for different learning modes in the Quizlet-like application. Each mode offers unique learning experiences tailored to different study preferences and goals.

## Base URL
```
http://localhost:8000/api/v1/study
```

## Authentication
All endpoints require authentication using Bearer token:
```
Authorization: Bearer <access_token>
```

## Study Modes

### 🎴 Flashcards Mode
Interactive flashcard learning with progress tracking and starring functionality.

#### Endpoints

##### GET `/modes/flashcards/{study_set_id}`
Get all flashcards for a study set with progress and starred status.

**Response:**
```json
[
  {
    "term_id": 1,
    "term": "Hello",
    "definition": "A greeting",
    "image_url": "https://example.com/image.jpg",
    "audio_url": "https://example.com/audio.mp3",
    "is_starred": false,
    "familiarity_level": "learning",
    "position": 1
  }
]
```

##### POST `/modes/flashcards/{study_set_id}/star/{term_id}`
Star or unstar a flashcard.

**Request:**
```json
{
  "starred": true
}
```

**Response:**
```json
{
  "starred": true
}
```

##### GET `/modes/flashcards/{study_set_id}/starred`
Get all starred cards for a study set.

**Response:**
```json
{
  "study_set_id": 1,
  "cards": [
    {
      "term_id": 1,
      "term": "Hello",
      "definition": "A greeting",
      "image_url": "https://example.com/image.jpg",
      "audio_url": "https://example.com/audio.mp3",
      "is_starred": true,
      "starred_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 🧠 Learn Mode (Adaptive Learning)
Intelligent adaptive learning that adjusts difficulty based on performance.

#### Endpoints

##### GET `/modes/learn/{study_set_id}`
Get next adaptive question for learn mode.

**Query Parameters:**
- `learn_session_id` (int): ID of the learn session

**Response:**
```json
{
  "question_id": "learn_1_5_multiple_choice",
  "term_id": 5,
  "question_type": "multiple_choice",
  "question_text": "What is the definition of 'Hello'?",
  "correct_answer": "A greeting",
  "options": ["A greeting", "A farewell", "A question", "An answer"],
  "difficulty_level": 2,
  "points_worth": 2
}
```

##### POST `/modes/learn/{study_set_id}/answer`
Submit answer for learn mode.

**Request:**
```json
{
  "question_id": "learn_1_5_multiple_choice",
  "answer": "A greeting",
  "response_time": 3.5
}
```

**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "A greeting",
  "points_earned": 2,
  "current_streak": 3,
  "difficulty_level": 2
}
```

##### GET `/modes/learn/{study_set_id}/options`
Get learn mode customization options.

**Response:**
```json
{
  "study_with_spell": false,
  "answer_with": "both",
  "question_types": ["multiple_choice", "written"]
}
```

### 📝 Test Mode (Comprehensive Assessment)
Create and take comprehensive tests with various question types.

#### Endpoints

##### POST `/modes/test/{study_set_id}`
Create a new test session.

**Request:**
```json
{
  "max_questions": 10,
  "answer_with": "both",
  "question_types": ["multiple_choice", "true_false", "written"],
  "time_limit": 600,
  "randomize_order": true
}
```

**Response:**
```json
{
  "test_id": 1,
  "study_set_id": 1,
  "config": {
    "max_questions": 10,
    "answer_with": "both",
    "question_types": ["multiple_choice", "true_false", "written"],
    "time_limit": 600,
    "randomize_order": true
  },
  "total_questions": 10,
  "time_limit": 600,
  "created_at": "2024-01-01T12:00:00Z",
  "questions": [
    {
      "question_id": "test_1",
      "term_id": 1,
      "question_type": "multiple_choice",
      "question_text": "What is the definition of 'Hello'?",
      "correct_answer": "A greeting",
      "options": ["A greeting", "A farewell", "A question", "An answer"],
      "points_worth": 1.0,
      "position": 1
    }
  ]
}
```

##### GET `/modes/test/{test_id}`
Get test session with questions.

**Response:** Same as POST response above.

##### POST `/modes/test/{test_id}/submit`
Submit test answers and get results.

**Request:**
```json
{
  "answers": [
    {
      "question_id": "test_1",
      "answer": "A greeting",
      "time_spent": 15.5
    }
  ],
  "total_time_spent": 180.0
}
```

**Response:**
```json
{
  "test_id": 1,
  "score": 8.5,
  "total_questions": 10,
  "correct_answers": 8,
  "total_time_spent": 180.0,
  "breakdown_by_type": {
    "multiple_choice": {
      "correct": 5,
      "total": 6,
      "score": 5.0
    },
    "written": {
      "correct": 3,
      "total": 4,
      "score": 3.5
    }
  },
  "incorrect_answers": [
    {
      "term_id": 3,
      "question_text": "What is the definition of 'Goodbye'?",
      "user_answer": "A greeting",
      "correct_answer": "A farewell",
      "question_type": "multiple_choice"
    }
  ],
  "suggested_review": [3, 7]
}
```

##### GET `/modes/test/{test_id}/results`
Get test results (retrieves stored results).

### 🎯 Match Game
Interactive matching game with term-definition pairs.

#### Endpoints

##### POST `/modes/match/{study_set_id}`
Create a new match game.

**Query Parameters:**
- `pairs_count` (int, 4-12): Number of term-definition pairs

**Response:**
```json
{
  "game_id": 1,
  "study_set_id": 1,
  "pairs_count": 6,
  "selected_terms": [1, 2, 3, 4, 5, 6],
  "cards": [
    {
      "card_id": "term_1",
      "term_id": 1,
      "content": "Hello",
      "is_term": true,
      "position": 0
    },
    {
      "card_id": "def_1",
      "term_id": 1,
      "content": "A greeting",
      "is_term": false,
      "position": 1
    }
  ]
}
```

##### POST `/modes/match/{game_id}/move`
Submit a move in match game.

**Request:**
```json
{
  "first_card_id": "term_1",
  "second_card_id": "def_1"
}
```

**Response:**
```json
{
  "is_match": true,
  "move_number": 1,
  "incorrect_matches": 0
}
```

##### POST `/modes/match/{game_id}/complete`
Complete match game and get results.

**Request:**
```json
{
  "completion_time": 120.0,
  "incorrect_matches": 2
}
```

**Response:**
```json
{
  "game_id": 1,
  "completion_time": 120.0,
  "total_matches": 6,
  "incorrect_matches": 2,
  "score": 580
}
```

### 🎮 Gravity Game
Fast-paced typing game where terms fall and must be destroyed by typing definitions.

#### Endpoints

##### POST `/modes/gravity/{study_set_id}`
Create a new gravity game.

**Query Parameters:**
- `difficulty_level` (int, 1-5): Game difficulty

**Response:**
```json
{
  "game_id": 1,
  "study_set_id": 1,
  "difficulty_level": 2,
  "lives_remaining": 3,
  "speed_multiplier": 1.2
}
```

##### POST `/modes/gravity/{game_id}/answer`
Submit answer for gravity game.

**Request:**
```json
{
  "term_id": 1,
  "answer": "A greeting",
  "time_to_answer": 3.5
}
```

**Response:**
```json
{
  "is_correct": true,
  "lives_remaining": 3,
  "score": 25,
  "terms_destroyed": 1
}
```

##### POST `/modes/gravity/{game_id}/complete`
Complete gravity game.

**Request:**
```json
{
  "final_score": 150,
  "game_duration": 180.0
}
```

**Response:**
```json
{
  "final_score": 150,
  "terms_destroyed": 12,
  "game_duration": 180.0,
  "lives_remaining": 1
}
```

##### GET `/modes/gravity/{game_id}/leaderboard`
Get gravity game leaderboard.

**Response:**
```json
[
  {
    "user_id": 1,
    "username": "player1",
    "score": 200,
    "terms_destroyed": 15,
    "game_duration": 150.0,
    "completed_at": "2024-01-01T12:00:00Z"
  }
]
```

### ✍️ Write Mode
Written response mode with fuzzy matching and partial credit.

#### Endpoints

##### GET `/modes/write/{study_set_id}`
Get write mode questions.

**Query Parameters:**
- `answer_with` (string): "term", "definition", or "both"

**Response:**
```json
[
  {
    "question_id": "write_term_1",
    "term_id": 1,
    "prompt": "What is the definition of 'Hello'?",
    "correct_answer": "A greeting",
    "synonyms": ["greeting", "salutation"],
    "points_worth": 1
  }
]
```

##### POST `/modes/write/{study_set_id}/check`
Check written answer.

**Request:**
```json
{
  "question_id": "write_term_1",
  "answer": "A greeting",
  "response_time": 8.0
}
```

**Response:**
```json
{
  "is_correct": true,
  "score": 1.0,
  "feedback": "Correct! Well done!",
  "suggested_answer": null,
  "partial_credit": false
}
```

## Study Progress Endpoints

### GET `/progress/{study_set_id}`
Get study progress for all terms in a study set.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "study_set_id": 1,
    "term_id": 1,
    "familiarity_level": "familiar",
    "correct_count": 5,
    "incorrect_count": 2,
    "last_studied": "2024-01-01T12:00:00Z",
    "next_review": "2024-01-01T13:00:00Z",
    "current_streak": 3,
    "longest_streak": 5
  }
]
```

### POST `/progress/{study_set_id}/terms/{term_id}`
Update term progress.

**Request:**
```json
{
  "correct": true,
  "response_time": 5.0,
  "difficulty": 2
}
```

### GET `/review/{study_set_id}`
Get terms due for review (SRS algorithm).

**Response:**
```json
{
  "study_set_id": 1,
  "terms": [
    {
      "term_id": 1,
      "term": "Hello",
      "definition": "A greeting",
      "familiarity_level": "learning",
      "next_review": "2024-01-01T11:00:00Z"
    }
  ]
}
```

## Study Session Management

### POST `/session`
Start a new study session.

**Request:**
```json
{
  "study_set_id": 1,
  "study_mode": "flashcards"
}
```

### PUT `/session/{id}`
Update study session.

**Request:**
```json
{
  "completed_at": "2024-01-01T12:30:00Z",
  "score": 85.5,
  "total_questions": 20,
  "correct_answers": 17,
  "time_spent_seconds": 900
}
```

## Error Responses

All endpoints return standard HTTP status codes and error messages:

```json
{
  "error": "Study set not found",
  "detail": "The requested study set does not exist"
}
```

Common status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Usage Examples

### Complete Flashcards Session
```python
import requests

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "username": "user",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get flashcards
flashcards = requests.get("http://localhost:8000/api/v1/study/modes/flashcards/1", headers=headers)

# Star a card
requests.post("http://localhost:8000/api/v1/study/modes/flashcards/1/star/1", 
              headers=headers, json={"starred": True})
```

### Take a Test
```python
# Create test
test_config = {
    "max_questions": 10,
    "answer_with": "both",
    "question_types": ["multiple_choice", "written"],
    "time_limit": 600,
    "randomize_order": True
}

test = requests.post("http://localhost:8000/api/v1/study/modes/test/1", 
                     headers=headers, json=test_config)

# Submit answers
answers = [
    {"question_id": "test_1", "answer": "A greeting", "time_spent": 15.0}
]

result = requests.post(f"http://localhost:8000/api/v1/study/modes/test/{test.json()['test_id']}/submit",
                       headers=headers, json={"answers": answers, "total_time_spent": 180.0})
```

## Database Schema

The study modes API uses several new tables:

- `starred_cards`: Track starred flashcards
- `test_sessions`: Test session configuration
- `test_questions`: Individual test questions
- `match_games`: Match game sessions
- `match_moves`: Match game moves
- `gravity_games`: Gravity game sessions
- `gravity_terms`: Terms in gravity games
- `learn_sessions`: Learn mode sessions
- `learn_questions`: Learn mode questions

## Performance Considerations

- All endpoints are optimized for low latency
- Database queries use proper indexing
- Large result sets are paginated where appropriate
- Caching can be implemented for frequently accessed data

## Security

- All endpoints require authentication
- User can only access their own study data
- Input validation prevents SQL injection
- Rate limiting prevents abuse 