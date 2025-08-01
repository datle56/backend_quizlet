#!/usr/bin/env python3
"""
Script to create study mode tables in existing database
Run this after the main database is created to add study mode functionality
"""

import psycopg2
import time

# Database connection info
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

def create_study_mode_tables():
    """Create all study mode related tables"""
    
    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )
    conn.autocommit = True
    
    print("Creating Study Mode Tables...")
    
    # Update study_mode_enum to include gravity
    try:
        execute_query(conn, """
        ALTER TYPE study_mode_enum ADD VALUE IF NOT EXISTS 'gravity';
        """, autocommit=True)
        print("OK - Updated study_mode_enum")
    except Exception as e:
        print(f"WARNING - study_mode_enum update: {e}")
    
    # Create starred_cards table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS starred_cards (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            study_set_id INT REFERENCES study_sets(id),
            term_id INT REFERENCES terms(id),
            starred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, study_set_id, term_id)
        );
        """, autocommit=True)
        print("OK - Created starred_cards table")
    except Exception as e:
        print(f"WARNING - starred_cards table: {e}")
    
    # Create test_sessions table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS test_sessions (
            id SERIAL PRIMARY KEY,
            study_session_id INT REFERENCES study_sessions(id),
            max_questions INT,
            answer_with VARCHAR(20),
            question_types TEXT[],
            time_limit INT,
            randomized_order BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """, autocommit=True)
        print("OK - Created test_sessions table")
    except Exception as e:
        print(f"WARNING - test_sessions table: {e}")
    
    # Create test_questions table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS test_questions (
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
        """, autocommit=True)
        print("OK - Created test_questions table")
    except Exception as e:
        print(f"WARNING - test_questions table: {e}")
    
    # Create match_games table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS match_games (
            id SERIAL PRIMARY KEY,
            study_session_id INT REFERENCES study_sessions(id),
            pairs_count INT,
            selected_terms TEXT[],
            completed_at TIMESTAMP,
            completion_time_seconds INT,
            incorrect_matches INT DEFAULT 0,
            total_matches INT
        );
        """, autocommit=True)
        print("OK - Created match_games table")
    except Exception as e:
        print(f"WARNING - match_games table: {e}")
    
    # Create match_moves table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS match_moves (
            id SERIAL PRIMARY KEY,
            match_game_id INT REFERENCES match_games(id),
            move_number INT,
            first_card_term_id INT REFERENCES terms(id),
            second_card_term_id INT REFERENCES terms(id),
            is_match BOOLEAN,
            time_spent_seconds INT,
            move_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """, autocommit=True)
        print("OK - Created match_moves table")
    except Exception as e:
        print(f"WARNING - match_moves table: {e}")
    
    # Create gravity_games table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS gravity_games (
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
        """, autocommit=True)
        print("OK - Created gravity_games table")
    except Exception as e:
        print(f"WARNING - gravity_games table: {e}")
    
    # Create gravity_terms table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS gravity_terms (
            id SERIAL PRIMARY KEY,
            gravity_game_id INT REFERENCES gravity_games(id),
            term_id INT REFERENCES terms(id),
            appeared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            was_destroyed BOOLEAN DEFAULT FALSE,
            time_to_destroy_seconds INT,
            user_answer TEXT
        );
        """, autocommit=True)
        print("OK - Created gravity_terms table")
    except Exception as e:
        print(f"WARNING - gravity_terms table: {e}")
    
    # Create learn_sessions table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS learn_sessions (
            id SERIAL PRIMARY KEY,
            study_session_id INT REFERENCES study_sessions(id),
            current_difficulty INT DEFAULT 1,
            questions_answered INT DEFAULT 0,
            correct_answers INT DEFAULT 0,
            current_streak INT DEFAULT 0,
            adaptive_algorithm_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """, autocommit=True)
        print("OK - Created learn_sessions table")
    except Exception as e:
        print(f"WARNING - learn_sessions table: {e}")
    
    # Create learn_questions table
    try:
        execute_query(conn, """
        CREATE TABLE IF NOT EXISTS learn_questions (
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
        """, autocommit=True)
        print("OK - Created learn_questions table")
    except Exception as e:
        print(f"WARNING - learn_questions table: {e}")
    
    conn.close()
    print("\nStudy mode tables creation completed!")

if __name__ == "__main__":
    create_study_mode_tables() 