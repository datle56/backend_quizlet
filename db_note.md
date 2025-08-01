🗃️ Database: quizletDB – Ghi chú thiết kế
1. Users
Thông tin người dùng trong hệ thống.

id: Khóa chính, tự động tăng.

username: Tên đăng nhập duy nhất.

email: Email người dùng (duy nhất).

password_hash: Mật khẩu đã mã hóa.

full_name: Họ tên người dùng.

avatar_url: Link ảnh đại diện.

created_at, updated_at: Thời gian tạo và cập nhật.

is_premium: Người dùng có tài khoản trả phí không.

last_active_at: Thời gian hoạt động gần nhất.

total_study_sets_created: Số bộ thẻ đã tạo.

total_terms_learned: Số thuật ngữ đã học thành thạo.

2. StudySets
Bộ thẻ học (flashcards).

id: Khóa chính.

title, description: Tiêu đề và mô tả bộ thẻ.

user_id: Người tạo (liên kết Users).

is_public: Bộ thẻ công khai hay không.

created_at, updated_at: Ngày tạo và cập nhật.

terms_count: Số lượng thuật ngữ.

language_from, language_to: Ngôn ngữ nguồn → đích.

views_count: Lượt xem.

favorites_count: Lượt yêu thích.

average_rating: Trung bình đánh giá (ví dụ: 4.5).

3. Terms
Các thẻ (term) trong bộ thẻ học.

id: Khóa chính.

study_set_id: Bộ thẻ chứa thuật ngữ này.

term: Thuật ngữ.

definition: Định nghĩa/giải thích.

image_url, audio_url: Tài nguyên hỗ trợ học.

created_at, updated_at: Thời gian tạo/cập nhật.

position: Vị trí sắp xếp trong bộ thẻ.

4. Folders
Thư mục nhóm các bộ thẻ.

id: Khóa chính.

name: Tên thư mục.

user_id: Người sở hữu.

created_at, updated_at: Thời gian tạo/cập nhật.

5. FolderStudySets
Liên kết nhiều bộ thẻ vào thư mục.

id: Khóa chính.

folder_id: ID thư mục.

study_set_id: ID bộ thẻ.

added_at: Thời gian thêm vào thư mục.

6. StudyProgress
Tiến trình học từng thuật ngữ.

id: Khóa chính.

user_id: Người học.

study_set_id: Bộ thẻ đang học.

term_id: Thuật ngữ đang học.

familiarity_level: Mức độ quen thuộc (learning, familiar, mastered).

correct_count, incorrect_count: Thống kê kết quả.

last_studied, next_review: Lịch sử học và nhắc lại.

current_streak, longest_streak: Chuỗi trả lời đúng liên tục.

7. StudySessions
Ghi lại từng phiên học.

id: Khóa chính.

user_id, study_set_id: Ai học, học gì.

study_mode: Chế độ học (flashcards, learn, v.v.).

started_at, completed_at: Thời điểm bắt đầu/kết thúc.

score: Điểm tổng kết.

total_questions, correct_answers: Thống kê.

time_spent_seconds: Thời gian học (tính bằng giây).

8. Favorites
Người dùng đánh dấu bộ thẻ yêu thích.

id: Khóa chính.

user_id, study_set_id: Ai thích bộ thẻ nào.

favorited_at: Thời gian thêm yêu thích.

✅ Ràng buộc UNIQUE(user_id, study_set_id).

9. Classes
Lớp học trong hệ thống.

id: Khóa chính.

name, description: Tên và mô tả lớp học.

teacher_id: Giáo viên quản lý lớp (liên kết Users).

join_code: Mã tham gia lớp (duy nhất).

created_at: Ngày tạo lớp.

is_active: Lớp có đang hoạt động không.

10. ClassMembers
Danh sách thành viên trong lớp.

id: Khóa chính.

class_id, user_id: Lớp nào – ai là thành viên.

role: Vai trò (teacher, student).

joined_at: Ngày tham gia.

✅ UNIQUE(class_id, user_id) đảm bảo không trùng.

11. ClassStudySets
Các bộ thẻ được phân vào lớp học.

id: Khóa chính.

class_id, study_set_id: Liên kết lớp học với bộ thẻ.

assigned_at: Ngày giao.

due_date: Hạn nộp (nếu là bài tập).

is_optional: Có bắt buộc học không.

12. Ratings
Đánh giá và bình luận của người dùng với bộ thẻ.

id: Khóa chính.

study_set_id, user_id: Ai đánh giá bộ nào.

rating: Số sao (1–5).

comment: Nội dung bình luận (tùy chọn).

created_at, updated_at: Thời gian tạo/cập nhật.

✅ UNIQUE(study_set_id, user_id).

13. Notifications
Thông báo gửi đến người dùng.

id: Khóa chính.

user_id: Ai nhận thông báo.

type: Loại thông báo (new_assignment, study_reminder, ...).

related_entity_type, related_entity_id: Nội dung liên quan (ví dụ: bộ thẻ, lớp học).

message: Nội dung thông báo.

is_read: Đã đọc hay chưa.

created_at: Thời điểm gửi thông báo.

14. Reports
Báo cáo nội dung vi phạm.

id: Khóa chính.

reported_by_user_id: Ai gửi báo cáo.

reported_entity_type, reported_entity_id: Báo cáo nội dung nào (term, set, comment, ...).

reason: Lý do báo cáo.

status: Trạng thái (pending, reviewed, resolved, dismissed).

resolved_by_user_id: Người xử lý.

reported_at, resolved_at: Thời gian.

15. StudySetVersions
Lưu lịch sử chỉnh sửa bộ thẻ.

id: Khóa chính.

study_set_id: Bộ thẻ gốc.

version_number: Thứ tự phiên bản.

title, description: Nội dung phiên bản.

user_id: Người chỉnh sửa.

created_at: Thời điểm tạo.

changes_summary: Ghi chú về thay đổi (nếu có).

