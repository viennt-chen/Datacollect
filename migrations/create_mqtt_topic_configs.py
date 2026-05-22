"""
创建 MQTT Topic 配置表
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

def create_table():
    """创建 MQTT Topic 配置表"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查表是否已存在
        cursor.execute("SHOW TABLES LIKE 'mqtt_topic_configs'")
        if cursor.fetchone():
            print("表 mqtt_topic_configs 已存在")
            return
        
        # 创建表
        create_sql = """
        CREATE TABLE mqtt_topic_configs (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
            topic_name VARCHAR(255) UNIQUE NOT NULL COMMENT 'Topic 名称',
            description TEXT COMMENT 'Topic 描述',
            topic_type VARCHAR(50) NOT NULL DEFAULT 'custom' COMMENT 'Topic 类型：event/compress/custom',
            enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
            qos INT DEFAULT 1 COMMENT 'MQTT QoS 级别',
            storage_policy VARCHAR(50) DEFAULT 'save_raw' COMMENT '存储策略',
            parse_rules TEXT COMMENT '解析规则（JSON 格式）',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_topic_name (topic_name),
            INDEX idx_enabled (enabled),
            INDEX idx_topic_type (topic_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MQTT Topic 配置表'
        """
        
        cursor.execute(create_sql)
        conn.commit()
        
        print("✓ 表 mqtt_topic_configs 创建成功")
        
        # 插入默认配置
        default_topics = [
            ('SHXQ/NO1/KP3/IMG/ProcesEvent', '加工事件', 'event', 'save_event', None),
            ('SHXQ/NO1/KP3/IMG/Alarm', '报警数据', 'compress', 'save_raw', None),
            ('SHXQ/NO1/KP3/IMG/PV', 'PV 数据', 'compress', 'save_raw', None),
            ('SHXQ/NO1/KP3/IMG/SV', 'SV 数据', 'compress', 'save_raw', None)
        ]
        
        insert_sql = """
        INSERT INTO mqtt_topic_configs 
        (topic_name, description, topic_type, storage_policy, parse_rules)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for topic in default_topics:
            try:
                cursor.execute(insert_sql, topic)
                print(f"✓ 插入默认 Topic: {topic[0]}")
            except mysql.connector.errors.IntegrityError:
                print(f"- Topic 已存在：{topic[0]}")
        
        conn.commit()
        print("\n✓ 默认配置插入成功")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 创建表失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("创建 MQTT Topic 配置表")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    create_table()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
