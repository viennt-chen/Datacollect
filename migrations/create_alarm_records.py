"""
创建报警管理表
"""
import mysql.connector
import os
import sys

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}

def create_table():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SHOW TABLES LIKE 'alarm_records'")
        if cursor.fetchone():
            print("表 alarm_records 已存在")
            return
        
        create_sql = """
        CREATE TABLE alarm_records (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
            alarm_code VARCHAR(100) UNIQUE NOT NULL COMMENT '报警编号',
            alarm_source VARCHAR(50) NOT NULL COMMENT '报警来源',
            alarm_level VARCHAR(20) NOT NULL COMMENT '报警级别',
            alarm_type VARCHAR(100) COMMENT '报警类型',
            title VARCHAR(255) NOT NULL COMMENT '报警标题',
            description TEXT COMMENT '报警描述',
            device_code VARCHAR(100) COMMENT '关联设备编号',
            device_name VARCHAR(255) COMMENT '关联设备名称',
            alarm_value FLOAT COMMENT '报警值',
            threshold_value FLOAT COMMENT '阈值',
            status VARCHAR(20) DEFAULT 'pending' NOT NULL COMMENT '报警状态',
            handler VARCHAR(100) COMMENT '处理人',
            handled_at DATETIME COMMENT '处理时间',
            handle_remark TEXT COMMENT '处理备注',
            alarm_time DATETIME NOT NULL COMMENT '报警时间',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_alarm_code (alarm_code),
            INDEX idx_alarm_level (alarm_level),
            INDEX idx_status (status),
            INDEX idx_device_code (device_code),
            INDEX idx_alarm_time (alarm_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报警记录表'
        """
        
        cursor.execute(create_sql)
        conn.commit()
        
        print("✓ 表 alarm_records 创建成功")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 创建表失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("创建报警管理表")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    create_table()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
