#!/usr/bin/env python3
"""
Script to create quizletDB database and all required tables, including study mode functionality.
"""

import psycopg2
import time

# Thông tin kết nối
DB_HOST = '128.199.158.179'
DB_PORT = '5432'
DB_USER = 'myuser'
DB_PASS = 'mypassword'
DB_NAME = 'quizletDB'


def execute_query(conn, query, autocommit=False):
    """Execute a database query"""
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
    execute_query(
        conn, f'''DROP DATABASE IF EXISTS "{DB_NAME}"''', autocommit=True)
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
-- Tạo các enum trước khi sử dụng
CREATE TYPE familiarity_level_enum AS ENUM('learning', 'familiar', 'mastered');
CREATE TYPE study_mode_enum AS ENUM('flashcards', 'learn', 'write', 'spell', 'test', 'match', 'gravity');

-- Cập nhật study_mode_enum để đảm bảo có 'gravity'
ALTER TYPE study_mode_enum ADD VALUE IF NOT EXISTS 'gravity';

-- Bảng users (cập nhật: tách họ tên, bỏ username, thêm receive_tips)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(50),
    first_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_premium BOOLEAN DEFAULT FALSE,
    last_active_at TIMESTAMP,
    total_study_sets_created INT DEFAULT 0,
    total_terms_learned INT DEFAULT 0,
    receive_tips BOOLEAN DEFAULT FALSE
);

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

-- Thêm trường color (màu chủ đề)
ALTER TABLE study_sets ADD COLUMN IF NOT EXISTS color VARCHAR(20);

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

-- Bảng folders (cập nhật với các trường mới)
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    color VARCHAR(20),  -- Màu sắc thư mục (string để FE tự định nghĩa)
    icon VARCHAR(50),   -- Biểu tượng thư mục (string để FE tự định nghĩa)
    user_id INT REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,  -- Thêm trường public/private
    position INT DEFAULT 0,  -- Thứ tự sắp xếp
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

-- starred_cards (for flashcards mode)
CREATE TABLE starred_cards (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    study_set_id INT REFERENCES study_sets(id),
    term_id INT REFERENCES terms(id),
    starred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, study_set_id, term_id)
);

-- test_sessions (for test mode)
CREATE TABLE test_sessions (
    id SERIAL PRIMARY KEY,
    study_session_id INT REFERENCES study_sessions(id),
    max_questions INT,
    answer_with VARCHAR(20) CHECK (answer_with IN ('term', 'definition', 'both')),
    question_types TEXT[],
    time_limit INT,
    randomized_order BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- test_questions (individual questions in a test)
CREATE TABLE test_questions (
    id SERIAL PRIMARY KEY,
    test_session_id INT REFERENCES test_sessions(id),
    term_id INT REFERENCES terms(id),
    question_type VARCHAR(20),
    question_text TEXT,
    correct_answer TEXT,
    options TEXT[],
    user_answer TEXT,
    is_correct BOOLEAN,
    points_earned DECIMAL(3,2),
    time_spent_seconds INT,
    position INT
);

-- match_games (for match mode)
CREATE TABLE match_games (
    id SERIAL PRIMARY KEY,
    study_session_id INT REFERENCES study_sessions(id),
    pairs_count INT,
    selected_terms TEXT[],
    completed_at TIMESTAMP,
    completion_time_seconds INT,
    incorrect_matches INT DEFAULT 0,
    total_matches INT
);

-- match_moves (tracking moves in match game)
CREATE TABLE match_moves (
    id SERIAL PRIMARY KEY,
    match_game_id INT REFERENCES match_games(id),
    move_number INT,
    first_card_term_id INT REFERENCES terms(id),
    second_card_term_id INT REFERENCES terms(id),
    is_match BOOLEAN,
    time_spent_seconds INT,
    move_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- gravity_games (for gravity mode)
CREATE TABLE gravity_games (
    id SERIAL PRIMARY KEY,
    study_session_id INT REFERENCES study_sessions(id),
    difficulty_level INT DEFAULT 1,
    speed_multiplier DECIMAL(3,2) DEFAULT 1.0,
    lives_remaining INT DEFAULT 3,
    score INT DEFAULT 0,
    terms_destroyed INT DEFAULT 0,
    game_duration_seconds INT,
    completed_at TIMESTAMP
);

-- gravity_terms (terms that appeared in gravity game)
CREATE TABLE gravity_terms (
    id SERIAL PRIMARY KEY,
    gravity_game_id INT REFERENCES gravity_games(id),
    term_id INT REFERENCES terms(id),
    appeared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    was_destroyed BOOLEAN DEFAULT FALSE,
    time_to_destroy_seconds INT,
    user_answer TEXT
);

-- learn_sessions (for learn mode)
CREATE TABLE learn_sessions (
    id SERIAL PRIMARY KEY,
    study_session_id INT REFERENCES study_sessions(id),
    current_difficulty INT DEFAULT 1,
    questions_answered INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    current_streak INT DEFAULT 0,
    adaptive_algorithm_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- learn_questions (questions in learn mode)
CREATE TABLE learn_questions (
    id SERIAL PRIMARY KEY,
    learn_session_id INT REFERENCES learn_sessions(id),
    term_id INT REFERENCES terms(id),
    question_type VARCHAR(20),
    difficulty_level INT,
    user_answer TEXT,
    is_correct BOOLEAN,
    response_time_seconds DECIMAL(5,2),
    points_earned INT,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    subject VARCHAR(100),  -- Môn học (optional)
    school VARCHAR(100),   -- Trường/Tổ chức (optional)
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
    print("✅ Tạo tất cả bảng thành công trong database quizletDB, bao gồm study mode tables.")
except Exception as e:
    print("❌ Lỗi khi tạo bảng:", e)

conn.close()
