"""
快速清理采集日志表到500M以内
直接执行SQL删除最旧的记录
"""
import mysql.connector
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}

MAX_SIZE_MB = 500

def get_table_size(cursor):
    cursor.execute("""
        SELECT ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb, table_rows
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'collector_logs'
    """)
    return cursor.fetchone()

def fast_cleanup():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("\n开始快速清理采集日志表...")
        
        size_info = get_table_size(cursor)
        current_size = float(size_info[0])
        total_records = int(size_info[1])
        
        print(f"当前大小: {current_size} MB, 记录数: {total_records} 条")
        
        if current_size <= MAX_SIZE_MB:
            print(f"✓ 已在限制范围内")
            return
        
        # 计算需要保留的记录数（90% of 500MB）
        avg_size = current_size / total_records
        target_records = int((MAX_SIZE_MB * 0.9) / avg_size)
        
        print(f"目标: 保留约 {target_records} 条记录")
        
        # 获取截止日期
        cursor.execute("""
            SELECT created_at FROM collector_logs 
            ORDER BY created_at DESC 
            LIMIT %s, 1
        """, (target_records,))
        cutoff = cursor.fetchone()[0]
        
        print(f"删除 {cutoff} 之前的记录...")
        
        # 批量删除
        cursor.execute("""
            DELETE FROM collector_logs 
            WHERE created_at < %s
        """, (cutoff,))
        
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"✓ 已删除 {deleted} 条记录")
        
        size_info = get_table_size(cursor)
        print(f"当前大小: {size_info[0]} MB, 剩余: {size_info[1]} 条")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("快速清理采集日志表到500M")
    print("=" * 60)
    
    fast_cleanup()
    
    print("\n完成！")
