"""
为设备表添加 mqtt_topics 字段
"""
import mysql.connector
import os

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}

def add_column():
    """添加 mqtt_topics 列"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查列是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'devices' 
            AND COLUMN_NAME = 'mqtt_topics'
        """, (DB_CONFIG['database'],))
        
        if cursor.fetchone()[0] > 0:
            print("列 mqtt_topics 已存在")
            return
        
        # 添加列
        alter_sql = """
        ALTER TABLE devices 
        ADD COLUMN mqtt_topics TEXT COMMENT '关联的 MQTT Topic 列表（JSON 数组）'
        """
        
        cursor.execute(alter_sql)
        conn.commit()
        
        print("✓ 列 mqtt_topics 添加成功")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 添加列失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("为设备表添加 mqtt_topics 字段")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    add_column()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
