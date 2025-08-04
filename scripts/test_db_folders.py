#!/usr/bin/env python3
"""
Script test database schema cho Folders
"""

import psycopg2
import time

# Thông tin kết nối
DB_HOST = '128.199.158.179'
DB_PORT = '5432'
DB_USER = 'myuser'
DB_PASS = 'mypassword'
DB_NAME = 'quizletDB'


def test_folder_schema():
    """Test schema của bảng folders"""
    try:
        # Kết nối database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        conn.autocommit = True
        
        print("🔍 Kiểm tra schema bảng folders...")
        
        # Kiểm tra cấu trúc bảng folders
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'folders'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            print("📋 Cấu trúc bảng folders:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # Kiểm tra bảng folder_study_sets
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'folder_study_sets'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            print("\n📋 Cấu trúc bảng folder_study_sets:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # Test insert dữ liệu mẫu
        print("\n🧪 Test insert dữ liệu mẫu...")
        
        # Tạo user test nếu chưa có
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name)
                VALUES ('test@example.com', 'test_hash', 'Test', 'User')
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """)
            user_id = cur.fetchone()
            if user_id:
                user_id = user_id[0]
            else:
                cur.execute("SELECT id FROM users WHERE email = 'test@example.com'")
                user_id = cur.fetchone()[0]
        
        # Tạo folder test
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO folders (name, description, color, icon, user_id, position)
                VALUES ('Test Folder', 'Test description', '#3B82F6', 'folder', %s, 1)
                RETURNING id
            """, (user_id,))
            folder_id = cur.fetchone()[0]
            print(f"✅ Tạo folder thành công: ID = {folder_id}")
        
        # Tạo study set test
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO study_sets (title, description, user_id)
                VALUES ('Test Study Set', 'Test study set description', %s)
                RETURNING id
            """, (user_id,))
            study_set_id = cur.fetchone()[0]
            print(f"✅ Tạo study set thành công: ID = {study_set_id}")
        
        # Thêm study set vào folder
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO folder_study_sets (folder_id, study_set_id)
                VALUES (%s, %s)
            """, (folder_id, study_set_id))
            print(f"✅ Thêm study set vào folder thành công")
        
        # Test query để lấy thông tin folder
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.id, f.name, f.description, f.color, f.icon, f.position,
                       COUNT(fs.study_set_id) as study_sets_count
                FROM folders f
                LEFT JOIN folder_study_sets fs ON f.id = fs.folder_id
                WHERE f.id = %s
                GROUP BY f.id
            """, (folder_id,))
            
            result = cur.fetchone()
            if result:
                print(f"\n📁 Thông tin folder:")
                print(f"  - ID: {result[0]}")
                print(f"  - Name: {result[1]}")
                print(f"  - Description: {result[2]}")
                print(f"  - Color: {result[3]}")
                print(f"  - Icon: {result[4]}")
                print(f"  - Position: {result[5]}")
                print(f"  - Study Sets Count: {result[6]}")
        
        # Test query để lấy study sets trong folder
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id, s.title, s.description, fs.added_at
                FROM study_sets s
                JOIN folder_study_sets fs ON s.id = fs.study_set_id
                WHERE fs.folder_id = %s
                ORDER BY fs.added_at DESC
            """, (folder_id,))
            
            study_sets = cur.fetchall()
            print(f"\n📚 Study sets trong folder:")
            for study_set in study_sets:
                print(f"  - {study_set[1]} (ID: {study_set[0]}) - {study_set[3]}")
        
        # Cleanup - xóa dữ liệu test
        with conn.cursor() as cur:
            cur.execute("DELETE FROM folder_study_sets WHERE folder_id = %s", (folder_id,))
            cur.execute("DELETE FROM folders WHERE id = %s", (folder_id,))
            cur.execute("DELETE FROM study_sets WHERE id = %s", (study_set_id,))
            print(f"\n🧹 Đã cleanup dữ liệu test")
        
        conn.close()
        print("\n✅ Test database schema thành công!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


def main():
    """Test chính"""
    print("🚀 Bắt đầu test database schema cho Folders")
    print("=" * 60)
    
    test_folder_schema()
    
    print("\n" + "=" * 60)
    print("✅ Hoàn thành test database schema")


if __name__ == "__main__":
    main() 