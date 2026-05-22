"""
数据库迁移脚本：更新字段类型以支持 Protobuf 格式
1. processing_events.extra_data: JSON -> TEXT
2. collected_data.data_json: JSON -> TEXT
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

def alter_column_to_text(table_name: str, column_name: str, new_comment: str):
    """将列类型修改为 TEXT"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查当前列类型
        cursor.execute("""
            SELECT COLUMN_TYPE, COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s 
            AND COLUMN_NAME = %s
        """, (DB_CONFIG['database'], table_name, column_name))
        
        result = cursor.fetchone()
        if not result:
            print(f"✗ 列 {table_name}.{column_name} 不存在")
            return
        
        current_type = result[0]
        current_comment = result[1]
        
        print(f"当前: {table_name}.{column_name} = {current_type}")
        print(f"注释: {current_comment}")
        
        # 修改列类型
        alter_sql = f"""
        ALTER TABLE {table_name} 
        MODIFY COLUMN {column_name} TEXT 
        COMMENT '{new_comment}'
        """
        
        cursor.execute(alter_sql)
        conn.commit()
        
        print(f"✓ {table_name}.{column_name} 已修改为 TEXT 类型")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 修改失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    print("=" * 60)
    print("数据库迁移：支持 Protobuf 格式存储")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    # 1. 修改 processing_events.extra_data
    print("[1/2] 修改 processing_events.extra_data ...")
    alter_column_to_text(
        'processing_events',
        'extra_data',
        '其他所有原始字段的完整备份（支持JSON或Protobuf格式）'
    )
    
    print()
    
    # 2. 修改 collected_data.data_json
    print("[2/2] 修改 collected_data.data_json ...")
    alter_column_to_text(
        'collected_data',
        'data_json',
        'JSON 数据或 Protobuf 二进制数据'
    )
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
