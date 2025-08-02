# Quizlet Backend API

Backend API cho ứng dụng Quizlet được xây dựng với FastAPI, SQLAlchemy và PostgreSQL.

## Cấu trúc dự án

```
backend_quizlet/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── auth.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   └── user.py
│   ├── services/
│   │   └── auth_service.py
│   ├── utils/
│   │   └── validators.py
│   └── main.py
├── alembic/
├── tests/
├── scripts/
├── requirements.txt
├── env.example
├── setup.py
├── run.py
└── README.md
```

## 🚀 Quick Setup

### Cách 1: Setup tự động
```bash
cd backend_quizlet
python setup.py
```

### Cách 2: Setup thủ công

1. **Cài đặt dependencies:**
```bash
cd backend_quizlet
pip install -r requirements.txt
```

2. **Tạo file .env:**
```bash
python scripts/setup_env.py
# Hoặc copy env.example và chỉnh sửa
cp env.example .env
```

3. **Cập nhật database credentials trong .env:**
```env
DATABASE_URL=postgresql://username:password@host:port/database
```

4. **Khởi tạo database:**
```bash
python scripts/init_db.py
# Hoặc sử dụng Alembic
alembic upgrade head
```

5. **Chạy server:**
```bash
python run.py
# Hoặc
uvicorn app.main:app --reload
```

## 🔧 Troubleshooting

### Lỗi Pydantic Settings
Nếu gặp lỗi "Extra inputs are not permitted", hãy:

1. **Kiểm tra file .env có đúng format không:**
```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key
```

2. **Chạy lại setup:**
```bash
python setup.py
```

### Lỗi Database Connection
1. **Kiểm tra PostgreSQL đã chạy chưa**
2. **Kiểm tra credentials trong .env**
3. **Test connection:**
```bash
python scripts/init_db.py
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Đăng ký tài khoản mới
- `POST /api/v1/auth/login` - Đăng nhập
- `POST /api/v1/auth/refresh` - Làm mới access token

### Users
- `GET /api/v1/users/me` - Lấy thông tin user hiện tại
- `PUT /api/v1/users/me` - Cập nhật thông tin user
- `GET /api/v1/users/{user_id}` - Lấy thông tin user theo ID

### Study Sets
- `POST /api/v1/study-sets/` - Tạo bộ thẻ học mới
- `GET /api/v1/study-sets/{id}` - Lấy chi tiết bộ thẻ học
- `PUT /api/v1/study-sets/{id}` - Cập nhật bộ thẻ học
- `DELETE /api/v1/study-sets/{id}` - Xóa bộ thẻ học
- `GET /api/v1/study-sets/` - Tìm kiếm và lọc bộ thẻ học
- `GET /api/v1/study-sets/user/me` - Lấy bộ thẻ học của user hiện tại

### Terms (Thuật ngữ)
- `POST /api/v1/study-sets/{id}/terms/` - Thêm thuật ngữ mới
- `GET /api/v1/study-sets/{id}/terms/` - Lấy tất cả thuật ngữ
- `PUT /api/v1/study-sets/{id}/terms/{term_id}` - Cập nhật thuật ngữ
- `DELETE /api/v1/study-sets/{id}/terms/{term_id}` - Xóa thuật ngữ
- `POST /api/v1/study-sets/{id}/terms/bulk` - Thêm nhiều thuật ngữ cùng lúc
- `PUT /api/v1/study-sets/{id}/terms/reorder` - Sắp xếp lại thứ tự thuật ngữ

### Study Modes
- `POST /api/v1/study/flashcards/{study_set_id}` - Flashcards mode
- `POST /api/v1/study/learn/{study_set_id}` - Learn mode
- `POST /api/v1/study/write/{study_set_id}` - Write mode
- `POST /api/v1/study/spell/{study_set_id}` - Spell mode
- `POST /api/v1/study/test/{study_set_id}` - Test mode
- `POST /api/v1/study/match/{study_set_id}` - Match mode
- `POST /api/v1/study/gravity/{study_set_id}` - Gravity mode

### Social Features
- `POST /api/v1/social/favorites/{study_set_id}` - Toggle favorite
- `GET /api/v1/social/favorites` - Get user favorites
- `POST /api/v1/social/ratings/{study_set_id}` - Create/update rating
- `GET /api/v1/social/ratings/{study_set_id}` - Get rating summary

### Classes
- `POST /api/v1/classes/` - Create class
- `GET /api/v1/classes/` - Get user's classes
- `POST /api/v1/classes/{class_id}/join` - Join class
- `GET /api/v1/classes/{class_id}/members` - Get class members

### Notifications (Phase 6)
- `GET /api/v1/notifications/` - Get user notifications
- `PUT /api/v1/notifications/{id}/read` - Mark notification as read
- `PUT /api/v1/notifications/mark-all-read` - Mark all as read
- `GET /api/v1/notifications/stats` - Get notification statistics
- `POST /api/v1/notifications/test-email` - Test email notification
- `POST /api/v1/notifications/test-push` - Test push notification

### Reports & Moderation (Phase 6)
- `POST /api/v1/reports/` - Create report
- `GET /api/v1/reports/` - Get all reports (admin)
- `PUT /api/v1/reports/{id}/resolve` - Resolve report (admin)
- `GET /api/v1/reports/stats` - Get report statistics (admin)
- `GET /api/v1/reports/my-reports` - Get user's reports

### Analytics (Phase 6)
- `GET /api/v1/analytics/user-stats` - Get user statistics
- `GET /api/v1/analytics/study-set-stats/{id}` - Get study set analytics
- `GET /api/v1/analytics/class-stats/{id}` - Get class statistics
- `GET /api/v1/analytics/study-session-stats` - Get session statistics
- `GET /api/v1/analytics/comprehensive` - Get comprehensive analytics
- `GET /api/v1/analytics/dashboard` - Get dashboard statistics
- `GET /api/v1/analytics/progress/{study_set_id}` - Get study progress

## Database Schema

Dự án sử dụng PostgreSQL với các bảng chính:
- `users` - Thông tin người dùng
- `study_sets` - Bộ thẻ học
- `terms` - Các thẻ trong bộ thẻ
- `folders` - Thư mục nhóm bộ thẻ
- `study_progress` - Tiến trình học
- `study_sessions` - Phiên học
- `favorites` - Bộ thẻ yêu thích
- `classes` - Lớp học
- `ratings` - Đánh giá
- `notifications` - Thông báo
- `reports` - Báo cáo

## Development

### Tạo migration mới:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Chạy tests:
```bash
pytest
```

### API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `SECRET_KEY` | JWT secret key | - |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | 7 |
| `REDIS_URL` | Redis connection string | - |
| `ENVIRONMENT` | Environment (dev/prod) | development |
| `DEBUG` | Debug mode | True |

## 🎯 Features

- ✅ **Authentication System** - JWT-based auth với access/refresh tokens
- ✅ **User Management** - CRUD operations cho users
- ✅ **Study Sets Management** - CRUD operations cho study sets và terms
- ✅ **Study Progress Tracking** - SRS algorithm và progress tracking
- ✅ **Study Modes** - Flashcards, Learn, Write, Spell, Test, Match, Gravity
- ✅ **Social Features** - Favorites, ratings, comments
- ✅ **Class Management** - Class creation, joining, assignments
- ✅ **Notifications System** - Real-time notifications, email, push notifications
- ✅ **Reports & Moderation** - Content reporting, admin moderation tools
- ✅ **Analytics & Statistics** - User stats, study set analytics, class statistics
- ✅ **Database Integration** - SQLAlchemy với PostgreSQL
- ✅ **API Documentation** - Auto-generated Swagger docs
- ✅ **Security** - Password hashing, input validation
- ✅ **Testing** - Pytest framework
- ✅ **Migrations** - Alembic database versioning
- ✅ **Error Handling** - Proper HTTP status codes
- ✅ **CORS Support** - Cross-origin requests
- ✅ **Environment Config** - Flexible configuration system
- ✅ **Background Tasks** - Asynchronous processing for notifications

## 🔮 Roadmap

- [ ] File Upload System
- [ ] Real-time Features (WebSockets)
- [ ] Advanced Analytics with Machine Learning
- [ ] Automated Content Moderation
- [ ] Mobile API Support
- [ ] Performance Optimizations
- [ ] Advanced Caching Strategy "# backend_quizlet" 
"# backend_quizlet" 
"# backend_quizlet" 
