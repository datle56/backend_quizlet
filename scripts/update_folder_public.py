#!/usr/bin/env python3
"""
Script to update existing database to add is_public field to folders table.
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


# Kết nối tới database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    dbname=DB_NAME
)
conn.autocommit = True

# Cập nhật bảng folders để thêm trường is_public
update_folders_sql = """
-- Thêm trường is_public vào bảng folders nếu chưa tồn tại
ALTER TABLE folders ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;

-- Cập nhật tất cả folders hiện tại thành private (mặc định)
UPDATE folders SET is_public = FALSE WHERE is_public IS NULL;
"""

try:
    execute_query(conn, update_folders_sql, autocommit=True)
    print("✅ Đã cập nhật bảng folders với trường is_public")
except Exception as e:
    print("❌ Lỗi khi cập nhật bảng folders:", e)

conn.close()
print("✅ Hoàn thành cập nhật database!") 