# Folders API Documentation

## Tổng quan

Folders API cho phép người dùng tổ chức study sets vào các thư mục để dễ quản lý và tìm kiếm. Mỗi thư mục có thể có tên, mô tả, màu sắc và biểu tượng tùy chỉnh.

## Data Structure

### Folder Entity
```json
{
  "id": 123,
  "name": "Tiếng Anh",
  "description": "Các study sets về tiếng Anh",
  "color": "#3B82F6",
  "icon": "language",
  "user_id": 456,
  "position": 1,
  "study_sets_count": 15,
  "created_at": "2025-08-01T10:00:00Z",
  "updated_at": "2025-08-01T11:30:00Z"
}
```

### Folder Colors & Icons
```json
{
  "colors": [
    "#3B82F6", "#EF4444", "#10B981", "#F59E0B", 
    "#8B5CF6", "#EC4899", "#6B7280", "#F97316",
    "#06B6D4", "#84CC16", "#A855F7", "#F43F5E"
  ],
  "icons": [
    "folder", "book", "language", "science", "history", 
    "math", "music", "art", "sports", "business",
    "computer", "medical", "travel", "food", "nature",
    "star", "heart", "fire", "lightning", "moon", "sun"
  ]
}
```

## API Endpoints

### 1. Tạo thư mục
**POST** `/api/v1/folders/`

Tạo một thư mục mới.

**Request Body:**
```json
{
  "name": "Tiếng Anh",
  "description": "Các study sets về tiếng Anh",
  "color": "#3B82F6",
  "icon": "language"
}
```

**Response (201):**
```json
{
  "id": 123,
  "name": "Tiếng Anh",
  "description": "Các study sets về tiếng Anh",
  "color": "#3B82F6",
  "icon": "language",
  "user_id": 456,
  "position": 1,
  "study_sets_count": 0,
  "created_at": "2025-08-01T10:00:00Z",
  "updated_at": "2025-08-01T10:00:00Z"
}
```

### 2. Lấy danh sách thư mục của user
**GET** `/api/v1/folders/user/me`

Lấy tất cả thư mục của user hiện tại.

**Response (200):**
```json
[
  {
    "id": 123,
    "name": "Tiếng Anh",
    "description": "Các study sets về tiếng Anh",
    "color": "#3B82F6",
    "icon": "language",
    "user_id": 456,
    "position": 1,
    "study_sets_count": 5,
    "created_at": "2025-08-01T10:00:00Z",
    "updated_at": "2025-08-01T10:00:00Z"
  },
  {
    "id": 124,
    "name": "Toán học",
    "description": "Các study sets về toán học",
    "color": "#10B981",
    "icon": "math",
    "user_id": 456,
    "position": 2,
    "study_sets_count": 3,
    "created_at": "2025-08-01T11:00:00Z",
    "updated_at": "2025-08-01T11:00:00Z"
  }
]
```

### 3. Lấy chi tiết thư mục
**GET** `/api/v1/folders/{folder_id}`

Lấy thông tin chi tiết của một thư mục.

**Response (200):**
```json
{
  "id": 123,
  "name": "Tiếng Anh",
  "description": "Các study sets về tiếng Anh",
  "color": "#3B82F6",
  "icon": "language",
  "user_id": 456,
  "position": 1,
  "study_sets_count": 5,
  "created_at": "2025-08-01T10:00:00Z",
  "updated_at": "2025-08-01T10:00:00Z"
}
```

### 4. Cập nhật thư mục
**PUT** `/api/v1/folders/{folder_id}`

Cập nhật thông tin thư mục.

**Request Body:**
```json
{
  "name": "Tiếng Anh Nâng cao",
  "description": "Các study sets tiếng Anh nâng cao",
  "color": "#8B5CF6",
  "icon": "language"
}
```

**Response (200):**
```json
{
  "id": 123,
  "name": "Tiếng Anh Nâng cao",
  "description": "Các study sets tiếng Anh nâng cao",
  "color": "#8B5CF6",
  "icon": "language",
  "user_id": 456,
  "position": 1,
  "study_sets_count": 5,
  "created_at": "2025-08-01T10:00:00Z",
  "updated_at": "2025-08-01T12:00:00Z"
}
```

### 5. Xóa thư mục
**DELETE** `/api/v1/folders/{folder_id}`

Xóa thư mục và tất cả study sets trong thư mục đó.

**Response (204):** No content

### 6. Sắp xếp lại thư mục
**PUT** `/api/v1/folders/reorder`

Sắp xếp lại thứ tự các thư mục.

**Request Body:**
```json
{
  "folder_ids": [124, 123, 125]
}
```

**Response (200):**
```json
[
  {
    "id": 124,
    "name": "Toán học",
    "position": 1,
    "study_sets_count": 3
  },
  {
    "id": 123,
    "name": "Tiếng Anh",
    "position": 2,
    "study_sets_count": 5
  },
  {
    "id": 125,
    "name": "Khoa học",
    "position": 3,
    "study_sets_count": 2
  }
]
```

### 7. Lấy colors và icons có sẵn
**GET** `/api/v1/folders/colors-icons`

Lấy danh sách màu sắc và biểu tượng có sẵn.

**Response (200):**
```json
{
  "colors": [
    "#3B82F6", "#EF4444", "#10B981", "#F59E0B", 
    "#8B5CF6", "#EC4899", "#6B7280", "#F97316",
    "#06B6D4", "#84CC16", "#A855F7", "#F43F5E"
  ],
  "icons": [
    "folder", "book", "language", "science", "history", 
    "math", "music", "art", "sports", "business",
    "computer", "medical", "travel", "food", "nature",
    "star", "heart", "fire", "lightning", "moon", "sun"
  ]
}
```

## Study Sets trong Folders

### 8. Lấy study sets trong thư mục
**GET** `/api/v1/folders/{folder_id}/study-sets`

Lấy danh sách study sets trong một thư mục.

**Response (200):**
```json
{
  "folder": {
    "id": 123,
    "name": "Tiếng Anh",
    "description": "Các study sets về tiếng Anh",
    "color": "#3B82F6",
    "icon": "language",
    "user_id": 456,
    "position": 1,
    "study_sets_count": 2,
    "created_at": "2025-08-01T10:00:00Z",
    "updated_at": "2025-08-01T10:00:00Z"
  },
  "study_sets": [
    {
      "id": 1,
      "title": "Basic English Vocabulary",
      "description": "Từ vựng tiếng Anh cơ bản",
      "terms_count": 50,
      "color": "#3B82F6",
      "added_at": "2025-08-01T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Advanced English Grammar",
      "description": "Ngữ pháp tiếng Anh nâng cao",
      "terms_count": 30,
      "color": "#10B981",
      "added_at": "2025-08-01T11:00:00Z"
    }
  ],
  "total": 2
}
```

### 9. Thêm study set vào thư mục
**POST** `/api/v1/folders/{folder_id}/study-sets/{study_set_id}`

Thêm một study set vào thư mục.

**Response (201):**
```json
{
  "message": "Đã thêm study set vào thư mục"
}
```

### 10. Xóa study set khỏi thư mục
**DELETE** `/api/v1/folders/{folder_id}/study-sets/{study_set_id}`

Xóa study set khỏi thư mục.

**Response (204):** No content

### 11. Di chuyển study set sang thư mục khác
**PUT** `/api/v1/study-sets/{study_set_id}/move-to-folder/{folder_id}`

Di chuyển study set từ thư mục hiện tại sang thư mục mới.

**Response (200):**
```json
{
  "message": "Đã di chuyển study set sang thư mục mới"
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Thư mục không tồn tại"
}
```

### 400 Bad Request
```json
{
  "detail": "Không thể thêm study set vào thư mục"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

## Authentication

Tất cả endpoints đều yêu cầu authentication thông qua Bearer token:

```
Authorization: Bearer <access_token>
```

## Implementation Notes

1. **Position Management**: Mỗi folder có một position để sắp xếp thứ tự hiển thị
2. **Study Sets Count**: Số lượng study sets được tính toán tự động
3. **Cascade Delete**: Khi xóa folder, tất cả study sets trong folder sẽ bị xóa khỏi folder đó
4. **User Isolation**: Mỗi user chỉ có thể truy cập folders của mình
5. **Color & Icon Validation**: Colors và icons phải nằm trong danh sách có sẵn

## Testing

Sử dụng script test: `scripts/test_folders.py`

```bash
python scripts/test_folders.py
``` 