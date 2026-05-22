"""
设置采集日志表大小上限为500M并配置轮询清理机制
使用Python脚本实现更灵活的清理逻辑
"""
import mysql.connector
import os
import sys
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}

MAX_SIZE_MB = 500
BATCH_DELETE = 5000

def get_table_size(cursor):
    cursor.execute("""
        SELECT ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb, table_rows
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'collector_logs'
    """)
    return cursor.fetchone()

def cleanup_logs():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("\n开始清理采集日志表...")
        
        size_info = get_table_size(cursor)
        if not size_info:
            print("✗ 表 collector_logs 不存在")
            return
        
        current_size = size_info[0]
        total_records = size_info[1]
        print(f"当前大小: {current_size} MB, 记录数: {total_records} 条")
        
        if current_size <= MAX_SIZE_MB:
            print(f"✓ 表大小在限制范围内（{current_size} MB <= {MAX_SIZE_MB} MB）")
            return
        
        # 计算需要保留的大致记录数（基于当前平均每条记录大小）
        avg_size_per_record = float(current_size) / float(total_records) if total_records > 0 else 0
        target_records = int(float(MAX_SIZE_MB) * 0.9 / avg_size_per_record) if avg_size_per_record > 0 else 0
        
        print(f"目标记录数: ~{target_records} 条（预留10%缓冲）")
        
        if target_records > 0 and target_records < total_records:
            # 找到保留记录的截止日期
            cursor.execute("""
                SELECT created_at 
                FROM collector_logs 
                ORDER BY created_at DESC 
                LIMIT %s, 1
            """, (target_records,))
            result = cursor.fetchone()
            
            if result:
                cutoff_date = result[0]
                print(f"截止日期: {cutoff_date}")
                
                # 删除截止日期之前的所有记录
                cursor.execute("""
                    DELETE FROM collector_logs 
                    WHERE created_at < %s
                """, (cutoff_date,))
                
                deleted = cursor.rowcount
                conn.commit()
                print(f"已删除 {deleted} 条记录")
        
        print(f"\n✓ 清理完成！")
        
        size_info = get_table_size(cursor)
        print(f"最终大小: {size_info[0]} MB, 剩余记录: {size_info[1]} 条")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 清理失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

def check_current_size():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        size_info = get_table_size(cursor)
        if size_info:
            print(f"\n当前表状态：")
            print(f"  大小：{size_info[0]} MB")
            print(f"  记录数：{size_info[1]} 条")
            print(f"  限制：{MAX_SIZE_MB} MB")
            usage = (size_info[0] / MAX_SIZE_MB) * 100
            print(f"  使用率：{usage:.2f}%")
        else:
            print("✗ 表 collector_logs 不存在")
            
    except Exception as e:
        print(f"✗ 查询失败：{e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("设置采集日志表大小上限为500M")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    check_current_size()
    
    cleanup_logs()
    
    check_current_size()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
