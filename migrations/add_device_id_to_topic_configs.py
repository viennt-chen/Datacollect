"""
为 MQTT Topic 配置表添加 device_id 字段
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

def add_device_id_column():
    """添加 device_id 字段"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'mqtt_topic_configs' 
            AND COLUMN_NAME = 'device_id'
        """, (DB_CONFIG['database'],))
        
        result = cursor.fetchone()
        if result[0] > 0:
            print("字段 device_id 已存在")
            return
        
        # 添加字段
        alter_sql = """
        ALTER TABLE mqtt_topic_configs 
        ADD COLUMN device_id INT COMMENT '关联设备 ID',
        ADD INDEX idx_device_id (device_id)
        """
        
        cursor.execute(alter_sql)
        conn.commit()
        
        print("✓ 字段 device_id 添加成功")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 添加字段失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("为 MQTT Topic 配置表添加 device_id 字段")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    add_device_id_column()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
