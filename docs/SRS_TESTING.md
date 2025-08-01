# Hướng dẫn Test SRS (Spaced Repetition System)

## Tổng quan

SRS đã được cấu hình để test nhanh với các khoảng thời gian ngắn:
- **Learning**: 1 phút
- **Familiar**: 3 phút  
- **Mastered**: 7 phút

## Cách Test SRS

### 1. Test Cơ bản (Manual)

#### Bước 1: Tạo Study Set
```bash
POST /api/v1/study-sets/
{
  "title": "Test SRS",
  "description": "Test SRS functionality",
  "terms": [
    {"term": "Hello", "definition": "Xin chào"},
    {"term": "Goodbye", "definition": "Tạm biệt"}
  ]
}
```

#### Bước 2: Học Term lần đầu
```bash
POST /api/v1/study/progress/{study_set_id}/terms/{term_id}
{
  "correct": true,
  "response_time": 2.5
}
```
**Kết quả:**
- `familiarity_level`: "learning"
- `next_review`: now + 1 phút
- `current_streak`: 1

#### Bước 3: Force Next Review (để test ngay)
```bash
POST /api/v1/study/test/force-review/{study_set_id}/terms/{term_id}
```
**Kết quả:** `next_review` được set về 1 giờ trước

#### Bước 4: Kiểm tra Review Terms
```bash
GET /api/v1/study/review/{study_set_id}
```
**Kết quả:** Term sẽ xuất hiện trong danh sách review

#### Bước 5: Học lại Term
```bash
POST /api/v1/study/progress/{study_set_id}/terms/{term_id}
{
  "correct": true,
  "response_time": 2.0
}
```
**Kết quả:**
- `familiarity_level`: "familiar" (level up!)
- `next_review`: now + 3 phút
- `current_streak`: 2

### 2. Test với Script

#### Chạy Script Test Đầy đủ
```bash
python scripts/test_srs.py
```

#### Chạy Script Test Nhanh
```bash
python scripts/test_srs_quick.py
```

## Study Session Flow

### 1. Bắt đầu Session
```bash
POST /api/v1/study/session
{
  "study_set_id": 1,
  "study_mode": "flashcards"
}
```
**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "study_set_id": 1,
  "study_mode": "flashcards",
  "started_at": "2024-06-01T10:00:00Z"
}
```

### 2. Học các Terms
Sử dụng `POST /api/v1/study/progress/{study_set_id}/terms/{term_id}` cho từng term

### 3. Kết thúc Session
```bash
PUT /api/v1/study/session/{id}
{
  "completed_at": "2024-06-01T10:30:00Z",
  "score": 85.5,
  "correct_answers": 17,
  "time_spent_seconds": 1800
}
```

## Test Cases

### Test Case 1: Level Up
1. Học term → Learning (1 phút)
2. Force review → Học lại → Familiar (3 phút)
3. Force review → Học lại → Mastered (7 phút)

### Test Case 2: Level Down
1. Học term → Mastered
2. Trả lời sai → Familiar
3. Trả lời sai → Learning

### Test Case 3: Streak
1. Học term đúng → Streak = 1
2. Học lại đúng → Streak = 2
3. Trả lời sai → Streak = 0

## API Endpoints

### Study Progress
- `GET /api/v1/study/progress/{study_set_id}` - Lấy progress
- `POST /api/v1/study/progress/{study_set_id}/terms/{term_id}` - Cập nhật progress

### Review
- `GET /api/v1/study/review/{study_set_id}` - Lấy terms cần review

### Study Session
- `POST /api/v1/study/session` - Bắt đầu session
- `PUT /api/v1/study/session/{id}` - Cập nhật session

### Test (Development)
- `POST /api/v1/study/test/force-review/{study_set_id}/terms/{term_id}` - Force next_review

## Schema Fields

### TermProgressUpdate
```json
{
  "correct": true,                    // Required
  "response_time": 2.5,              // Optional
  "difficulty": 1                    // Optional
}
```

### StudySessionUpdate
```json
{
  "completed_at": "2024-06-01T10:30:00Z",  // Optional
  "score": 85.5,                           // Optional
  "total_questions": 20,                   // Optional
  "correct_answers": 17,                   // Optional
  "time_spent_seconds": 1800               // Optional
}
```

## Lưu ý

1. **SRS Intervals**: Đã được set về phút để test nhanh
2. **Force Review**: Chỉ dùng trong development để test
3. **Study Session**: Để thống kê và theo dõi thời gian học
4. **Streak**: Tăng khi đúng, reset về 0 khi sai
5. **Optional Fields**: Tất cả fields ngoài `correct` đều optional

## Troubleshooting

### Term không xuất hiện trong review
- Kiểm tra `next_review` có <= now() không
- Sử dụng force review endpoint để test

### Level không tăng/giảm
- Kiểm tra `correct` field trong request
- Kiểm tra logic trong `_next_familiarity()`

### Session không update
- Kiểm tra session ID có đúng không
- Kiểm tra các field trong StudySessionUpdate schema

### Pydantic Validation Errors
- Đảm bảo `correct` field được gửi (required)
- Các field khác có thể bỏ qua (optional)
- Kiểm tra kiểu dữ liệu đúng (boolean, float, int) 