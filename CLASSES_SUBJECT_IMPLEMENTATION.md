# Classes Subject Field Implementation

## Tổng quan
Đã thêm trường `subject` (môn học) vào bảng `classes` để hỗ trợ việc phân loại lớp học theo môn học.

## Thay đổi đã thực hiện

### 1. Database Schema (`create_db.py`)
- Thêm trường `subject VARCHAR(100)` vào bảng `classes`
- Trường này là optional (nullable=True)

### 2. Model (`app/models/class_.py`)
- Thêm `subject = Column(String(100), nullable=True)` vào model `Class`

### 3. Schemas (`app/schemas/class_.py`)
- Thêm `subject: Optional[str] = None` vào `ClassBase`
- Thêm `subject: Optional[str] = None` vào `ClassUpdate`

### 4. API Endpoints (`app/api/v1/classes.py`)
- Cập nhật `_to_class_dict()` để bao gồm trường `subject` trong response
- Các endpoint hiện tại sẽ tự động hỗ trợ trường subject mới:
  - `POST /api/v1/classes/` - Tạo lớp học với môn học
  - `PUT /api/v1/classes/{class_id}` - Cập nhật lớp học với môn học

### 5. Service Layer (`app/services/class_service.py`)
- Không cần thay đổi vì đã sử dụng `**class_data.dict()` để xử lý động các trường

## Cách sử dụng

### Tạo lớp học với môn học:
```json
POST /api/v1/classes/
{
    "name": "Tiếng Anh 12A1",
    "description": "Mô tả về lớp học này",
    "subject": "Tiếng Anh"
}
```

### Cập nhật lớp học với môn học:
```json
PUT /api/v1/classes/{class_id}
{
    "name": "Tiếng Anh 12A1 - Cập nhật",
    "description": "Mô tả cập nhật về lớp học này",
    "subject": "Tiếng Anh - Nâng cao"
}
```

### Response mẫu:
```json
{
    "id": 1,
    "name": "Tiếng Anh 12A1",
    "description": "Mô tả về lớp học này",
    "subject": "Tiếng Anh",
    "teacher_id": 1,
    "join_code": "ABC123",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
}
```

## Lưu ý
- Trường `subject` là optional, có thể có hoặc không
- Database đã được cập nhật với trường mới
- Tất cả các endpoint hiện tại vẫn hoạt động bình thường
- Backward compatibility được đảm bảo 