"""Add missing workshop column to products table"""
import pymysql

DB_CONFIG = {
    'host': '10.10.180.241',
    'port': 3306,
    'user': 'admin',
    'password': 'admin',
    'database': 'datacollect'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE products ADD COLUMN workshop VARCHAR(100) COMMENT 'workshop' AFTER project")
    conn.commit()
    print("OK: workshop column added to products table")
except Exception as e:
    if "Duplicate column" in str(e):
        print("Column 'workshop' already exists")
    else:
        raise
finally:
    cursor.close()
    conn.close()
