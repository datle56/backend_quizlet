## Study & Learning APIs (Quizlet SRS)

### 1. Get Study Progress
**GET** `/api/v1/study/progress/{study_set_id}`
- Lấy tiến độ học của user cho từng term trong study set.
- Familiarity levels: Not studied, Learning, Familiar, Mastered
- Trả về danh sách progress từng term.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "study_set_id": 1,
    "term_id": 10,
    "familiarity_level": "learning",
    "correct_count": 3,
    "incorrect_count": 1,
    "last_studied": "2024-06-01T10:00:00Z",
    "next_review": "2024-06-01T10:01:00Z",
    "current_streak": 2,
    "longest_streak": 2
  }
]
```

---

### 2. Update Term Progress
**POST** `/api/v1/study/progress/{study_set_id}/terms/{term_id}`
- Cập nhật tiến độ học cho 1 term (đúng/sai, thời gian trả lời, độ khó...)
- Tăng/giảm familiarity, cập nhật streak, SRS scheduling.

**Request:**
```json
{
  "correct": true,
  "response_time": 2.5,
  "difficulty": 1
}
```
**Response:**
- Trả về progress mới nhất của term đó (như trên).

---

### 3. Get Review Terms (SRS)
**GET** `/api/v1/study/review/{study_set_id}`
- Lấy danh sách các term cần ôn tập theo thuật toán SRS (Spaced Repetition).
- Ưu tiên các term đến hạn, hoặc có performance thấp.

**Response:**
```json
{
  "study_set_id": 1,
  "terms": [
    {
      "term_id": 10,
      "term": "Hello",
      "definition": "Xin chào",
      "familiarity_level": "learning",
      "next_review": "2024-06-01T10:01:00Z"
    }
  ]
}
```

---

### 4. Start Study Session
**POST** `/api/v1/study/session`
- Bắt đầu một phiên học (flashcards, learn, test...)
- Lưu lại mode, thời gian bắt đầu để thống kê

**Request:**
```json
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

---

### 5. Update Study Session
**PUT** `/api/v1/study/session/{id}`
- Cập nhật kết quả, thời gian hoàn thành, điểm số, số câu đúng...

**Request:**
```json
{
  "completed_at": "2024-06-01T10:30:00Z",
  "score": 95.5,
  "correct_answers": 19,
  "time_spent_seconds": 1800
}
```
**Response:**
- Trả về thông tin session đã cập nhật.

---

## Cách Test SRS (Spaced Repetition System)

### Test Flow:
1. **Tạo study set** với một số terms
2. **Học term lần đầu** (POST `/progress/{study_set_id}/terms/{term_id}` với `correct: true`)
   - Term sẽ có `familiarity_level: "learning"` và `next_review: now + 1 phút`
3. **Đợi 1 phút** hoặc set `next_review` về quá khứ để test
4. **Gọi GET `/review/{study_set_id}`** - term sẽ xuất hiện trong danh sách review
5. **Học lại term** (POST với `correct: true`)
   - Term sẽ lên `familiarity_level: "familiar"` và `next_review: now + 3 phút`
6. **Lặp lại** để test các level khác nhau

### SRS Intervals (để test nhanh):
- **Learning**: 1 phút
- **Familiar**: 3 phút  
- **Mastered**: 7 phút

### Study Session Flow:
1. **Bắt đầu học**: `POST /session` với `study_set_id` và `study_mode`
2. **Học các terms**: Sử dụng `POST /progress/{study_set_id}/terms/{term_id}` 
3. **Kết thúc**: `PUT /session/{id}` với kết quả cuối cùng

---

## Backend SRS (Spaced Repetition System) - BE xử lý sao?
- Mỗi lần user học/ôn 1 term, BE cập nhật familiarity_level (learning → familiar → mastered) dựa trên đúng/sai.
- Sử dụng SRS: mỗi familiarity_level có khoảng thời gian ôn lại khác nhau (learning: 1 phút, familiar: 3 phút, mastered: 7 phút).
- Nếu trả lời sai, giảm level và reset streak.
- BE tự động tính toán next_review cho từng term dựa trên kết quả học.
- Khi gọi API review, BE trả về các term đến hạn hoặc cần ưu tiên ôn tập.
- Tất cả logic SRS, streak, thống kê đều xử lý phía backend.