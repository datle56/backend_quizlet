
import psycopg2
import time

# Thông tin kết nối
DB_HOST = '128.199.158.179'
DB_PORT = '5432'
DB_USER = 'myuser'
DB_PASS = 'mypassword'
DB_NAME = 'quizletDB'

def execute_query(conn, query, autocommit=False):
    with conn.cursor() as cur:
        cur.execute(query)
    if autocommit:
        conn.commit()

# Kết nối tới default 'postgres' database để xóa và tạo db mới
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    dbname='postgres'
)
conn.autocommit = True

# Xóa database nếu tồn tại
try:
    execute_query(conn, f'''DROP DATABASE IF EXISTS "{DB_NAME}"''', autocommit=True)
    print(f"✅ Đã xóa database {DB_NAME} (nếu có)")
except Exception as e:
    print("❌ Lỗi khi xóa database:", e)

# Tạo database mới
try:
    execute_query(conn, f'''CREATE DATABASE "{DB_NAME}"''', autocommit=True)
    print(f"✅ Đã tạo database {DB_NAME}")
except Exception as e:
    print("❌ Lỗi khi tạo database:", e)

conn.close()

# Đợi vài giây để Postgres cập nhật db list
time.sleep(2)

# Kết nối tới quizletDB mới tạo
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    dbname=DB_NAME
)
conn.autocommit = True

# Truy vấn tạo bảng
create_tables_sql = """
-- Bảng users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_premium BOOLEAN DEFAULT FALSE,
    last_active_at TIMESTAMP,
    total_study_sets_created INT DEFAULT 0,
    total_terms_learned INT DEFAULT 0
);

-- Bảng study_sets
CREATE TABLE study_sets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    description TEXT,
    user_id INT REFERENCES users(id),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    terms_count INT DEFAULT 0,
    language_from VARCHAR(10),
    language_to VARCHAR(10),
    views_count INT DEFAULT 0,
    favorites_count INT DEFAULT 0,
    average_rating DECIMAL(3,2)
);

-- Bảng terms
CREATE TABLE terms (
    id SERIAL PRIMARY KEY,
    study_set_id INT REFERENCES study_sets(id),
    term VARCHAR(500),
    definition TEXT,
    image_url VARCHAR(255),
    audio_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INT
);

-- Bảng folders
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    user_id INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- folder_study_sets
CREATE TABLE folder_study_sets (
    id SERIAL PRIMARY KEY,
    folder_id INT REFERENCES folders(id),
    study_set_id INT REFERENCES study_sets(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- study_progress
CREATE TYPE familiarity_level_enum AS ENUM('learning', 'familiar', 'mastered');

CREATE TABLE study_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    study_set_id INT REFERENCES study_sets(id),
    term_id INT REFERENCES terms(id),
    familiarity_level familiarity_level_enum,
    correct_count INT DEFAULT 0,
    incorrect_count INT DEFAULT 0,
    last_studied TIMESTAMP,
    next_review TIMESTAMP,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0
);

-- study_sessions
CREATE TYPE study_mode_enum AS ENUM('flashcards', 'learn', 'write', 'spell', 'test', 'match');

CREATE TABLE study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    study_set_id INT REFERENCES study_sets(id),
    study_mode study_mode_enum,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    score DECIMAL(5,2),
    total_questions INT,
    correct_answers INT,
    time_spent_seconds INT
);

-- favorites
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    study_set_id INT REFERENCES study_sets(id),
    favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, study_set_id)
);

-- classes
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    teacher_id INT REFERENCES users(id),
    join_code VARCHAR(10) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- class_members
CREATE TABLE class_members (
    id SERIAL PRIMARY KEY,
    class_id INT REFERENCES classes(id),
    user_id INT REFERENCES users(id),
    role VARCHAR(10) CHECK (role IN ('teacher', 'student')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(class_id, user_id)
);

-- class_study_sets
CREATE TABLE class_study_sets (
    id SERIAL PRIMARY KEY,
    class_id INT REFERENCES classes(id),
    study_set_id INT REFERENCES study_sets(id),
    assigned_at TIMESTAMP,
    due_date TIMESTAMP,
    is_optional BOOLEAN DEFAULT FALSE
);

-- ratings
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

-- notifications
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    type VARCHAR(50),
    related_entity_type VARCHAR(50),
    related_entity_id INT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- reports
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    reported_by_user_id INT REFERENCES users(id),
    reported_entity_type VARCHAR(50),
    reported_entity_id INT,
    reason TEXT,
    status VARCHAR(20) CHECK (status IN ('pending', 'reviewed', 'resolved', 'dismissed')) DEFAULT 'pending',
    resolved_by_user_id INT REFERENCES users(id),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- study_set_versions
CREATE TABLE study_set_versions (
    id SERIAL PRIMARY KEY,
    study_set_id INT REFERENCES study_sets(id),
    version_number INT,
    title VARCHAR(200),
    description TEXT,
    user_id INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changes_summary TEXT
);
"""

try:
    execute_query(conn, create_tables_sql, autocommit=True)
    print("✅ Tạo tất cả bảng thành công trong database quizletDB.")
except Exception as e:
    print("❌ Lỗi khi tạo bảng:", e)

conn.close()
