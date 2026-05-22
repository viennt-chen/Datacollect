"""
更新 PV、SV、ALARM 压缩参数表 - 将时间戳字段改为 datetime(6) 类型
"""
import mysql.connector
import os
import sys

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}


def update_table_columns(table_name: str):
    """更新表的时间戳列"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 先清空表数据（因为旧数据格式不兼容）
        truncate_sql = f"TRUNCATE TABLE {table_name}"
        cursor.execute(truncate_sql)
        print(f"✓ 清空表 {table_name} 的旧数据")
        
        # 删除旧索引
        drop_index_sql_1 = f"ALTER TABLE {table_name} DROP INDEX idx_{table_name.split('_')[0]}_topic_timestamp"
        try:
            cursor.execute(drop_index_sql_1)
            print(f"✓ 删除旧索引: idx_{table_name.split('_')[0]}_topic_timestamp")
        except Exception as e:
            print(f"- 索引不存在或已删除: {e}")
        
        # 删除旧列 timestamp_ms
        drop_column_sql = f"ALTER TABLE {table_name} DROP COLUMN timestamp_ms"
        try:
            cursor.execute(drop_column_sql)
            print(f"✓ 删除旧列: {table_name}.timestamp_ms")
        except Exception as e:
            print(f"- 列不存在或已删除: {e}")
        
        # 添加新列 timestamp (datetime(6))
        add_column_sql = f"""
        ALTER TABLE {table_name} 
        ADD COLUMN timestamp DATETIME(6) NOT NULL COMMENT '时间戳（精确到毫秒）' 
        AFTER event_uid
        """
        try:
            cursor.execute(add_column_sql)
            print(f"✓ 添加新列: {table_name}.timestamp DATETIME(6)")
        except Exception as e:
            print(f"- 列已存在: {e}")
        
        # 修改 original_timestamp 为 datetime(6)
        modify_column_sql = f"""
        ALTER TABLE {table_name} 
        MODIFY COLUMN original_timestamp DATETIME(6) COMMENT '原始时间戳（精确到毫秒）'
        """
        cursor.execute(modify_column_sql)
        print(f"✓ 修改列: {table_name}.original_timestamp -> DATETIME(6)")
        
        # 修改 created_at 为 datetime(6)
        modify_created_at_sql = f"""
        ALTER TABLE {table_name} 
        MODIFY COLUMN created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间'
        """
        cursor.execute(modify_created_at_sql)
        print(f"✓ 修改列: {table_name}.created_at -> DATETIME(6)")
        
        # 添加新索引
        prefix = table_name.split('_')[0]
        add_index_sql = f"""
        ALTER TABLE {table_name} 
        ADD INDEX idx_{prefix}_topic_timestamp (topic, timestamp)
        """
        try:
            cursor.execute(add_index_sql)
            print(f"✓ 添加新索引: idx_{prefix}_topic_timestamp")
        except Exception as e:
            print(f"- 索引已存在: {e}")
        
        conn.commit()
        print(f"✓ 表 {table_name} 更新完成\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ 更新表 {table_name} 失败：{e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("更新 PV、SV、ALARM 压缩参数表时间戳字段")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    # 更新 PV 压缩参数表
    update_table_columns('pv_compressed_params')
    
    # 更新 SV 压缩参数表
    update_table_columns('sv_compressed_params')
    
    # 更新 ALARM 压缩参数表
    update_table_columns('alarm_compressed_params')
    
    print("=" * 60)
    print("完成！")
    print("=" * 60)
