# Public/Private Features Documentation

## Tổng quan

Hệ thống đã được cập nhật để hỗ trợ tính năng public/private cho cả folders và study sets. Người dùng có thể:

1. **Folders**: Đặt thư mục thành public hoặc private
2. **Study Sets**: Đặt bộ thẻ thành public hoặc private
3. **Public Access**: Truy cập nội dung public mà không cần đăng nhập

## Database Changes

### Folders Table
- Thêm trường `is_public` (BOOLEAN, DEFAULT FALSE)
- Mặc định tất cả folders là private

### Study Sets Table
- Đã có trường `is_public` (BOOLEAN, DEFAULT TRUE)
- Mặc định tất cả study sets là public

## API Endpoints

### Folders

#### 1. Toggle Public/Private Status
```
PUT /api/v1/folders/{folder_id}/public
```
**Request Body:**
```json
{
  "is_public": true
}
```
**Response:** FolderResponse với trạng thái mới

#### 2. Get Public Folders (No Authentication Required)
```
GET /api/v1/folders/public?limit=50&offset=0
```
**Query Parameters:**
- `limit`: Số lượng folders tối đa (1-100, default: 50)
- `offset`: Số folders bỏ qua (default: 0)

#### 3. Get Public Folder Details (No Authentication Required)
```
GET /api/v1/folders/public/{folder_id}
```
**Response:** FolderResponse cho folder public

#### 4. Get Public Study Sets in Folder (No Authentication Required)
```
GET /api/v1/folders/public/{folder_id}/study-sets
```
**Response:** Chỉ trả về study sets public trong folder

### Study Sets

#### 1. Toggle Public/Private Status
```
PUT /api/v1/study-sets/{study_set_id}/public
```
**Request Body:**
```json
{
  "is_public": true
}
```
**Response:** StudySetResponse với trạng thái mới

#### 2. Get Public Study Set Details (No Authentication Required)
```
GET /api/v1/study-sets/public/{study_set_id}
```
**Response:** StudySetDetailResponse với terms

#### 3. Get Public Study Set Terms (No Authentication Required)
```
GET /api/v1/study-sets/public/{study_set_id}/terms/
```
**Response:** List[TermResponse] cho study set public

#### 4. Search Public Study Sets (No Authentication Required)
```
GET /api/v1/study-sets/?search=keyword&language_from=en&language_to=vi
```
**Response:** Chỉ trả về study sets public

## Access Control Rules

### Folders
- **Private Folders**: Chỉ user sở hữu có thể xem và chỉnh sửa
- **Public Folders**: Ai cũng có thể xem, chỉ user sở hữu có thể chỉnh sửa
- **Study Sets trong Public Folders**: Chỉ hiển thị study sets public

### Study Sets
- **Private Study Sets**: Chỉ user sở hữu có thể xem và chỉnh sửa
- **Public Study Sets**: Ai cũng có thể xem, chỉ user sở hữu có thể chỉnh sửa

## Migration Script

Để cập nhật database hiện tại, chạy script:
```bash
python scripts/update_folder_public.py
```

## Usage Examples

### 1. Tạo folder private
```bash
POST /api/v1/folders/
{
  "name": "My Private Folder",
  "description": "Private folder for my study sets",
  "is_public": false
}
```

### 2. Chuyển folder thành public
```bash
PUT /api/v1/folders/1/public
{
  "is_public": true
}
```

### 3. Xem danh sách folders public
```bash
GET /api/v1/folders/public?limit=20
```

### 4. Chuyển study set thành private
```bash
PUT /api/v1/study-sets/1/public
{
  "is_public": false
}
```

### 5. Xem study set public mà không cần đăng nhập
```bash
GET /api/v1/study-sets/public/1
```

## Security Considerations

1. **Private Content**: Nội dung private không thể truy cập từ bên ngoài
2. **Owner Only**: Chỉ chủ sở hữu có thể thay đổi trạng thái public/private
3. **Cascade Effect**: Study sets private trong folder public sẽ không hiển thị
4. **Audit Trail**: Tất cả thay đổi được ghi lại trong database

## Error Handling

- **404 Not Found**: Folder/Study set không tồn tại hoặc không public
- **403 Forbidden**: Không có quyền truy cập nội dung private
- **400 Bad Request**: Dữ liệu request không hợp lệ 