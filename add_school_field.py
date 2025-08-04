#!/usr/bin/env python3
"""
Script to add school field to existing classes table.
"""

import psycopg2

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

# Thêm trường school vào bảng classes
try:
    execute_query(conn, "ALTER TABLE classes ADD COLUMN IF NOT EXISTS school VARCHAR(100);", autocommit=True)
    print("✅ Đã thêm trường school vào bảng classes")
except Exception as e:
    print("❌ Lỗi khi thêm trường school:", e)

conn.close()
print("✅ Hoàn thành!") 